"""
Utils contains misc. functions to aid in data analysis.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright U of Oklahoma Center for Autonomous Sensing and Sampling 2019
"""

import warnings
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
from numpy import sin, cos
from pandas.plotting import register_matplotlib_converters
from pint import UnitStrippedWarning


warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("error", category=UnitStrippedWarning)
register_matplotlib_converters()

coeff = {"N955":
         {"IMET1": (1.02777010e-03, 2.59349232e-04, 1.56043078e-07),  # 57562
          "IMET2": (9.91077399e-04, 2.64646362e-04, 1.43596294e-07),  # 57563
          "IMET3": (1.00786813e-03, 2.61722397e-04, 1.48476183e-07)  # 58821
          }}

"""
More coefficients can be found at https://github.com/oucass/CASS-ardupilot/
blob/Copter-3.6/ArduCopter/sensors.cpp
TODO create JSON file to read into variable coeff with coefficients from all
IMET sensors and platforms which can be updated any time a platform is changed
"""


def regrid(base=None, base_times=None, data=None, data_times=None,
           new_res=None, ascent=True, units=None):
    """ Returns data interpolated to an evenly spaced array with resolution
    new_res.

    :param np.array<Quantity> base: Measurements of the variable serving as \
       the vertical coordinate
    :param np.array<Datetime> base_times: Times coresponding to base
    :param np.array<Quantity> data: Measurements of the dependent variable
    :param np.array<Datetime> data_times: Times coresponding to data
    :param Quantity new_res: The resolution to which base should be gridded. \
       This must have the same dimension as base.
    :param bool ascent: True if data from ascending leg of profile is to be \
       analyzed, false if descending
    :param pint.UnitRegistry units: The unit registry defined in Profile
    :cite: https://www.geeksforgeeks.org/python-get-the-index-of-first- \
       element-greater-than-k/
    :rtype: tuple
    :return: (new_base, new_times, new_data)
    """

    # Sanity check
    if len(base) == 0:
        print("Empty base passed to regrid")
        return

    # Set variables passes as params
    base_units = base.units
    data_units = data.units
    data = data.to_base_units()
    base = base.to(new_res.units)

    # Declare bounding indices
    data_seg_start_ind = None
    data_seg_end_ind = None
    base_seg_start_ind = None
    base_seg_end_ind = None

    # Check if data and base are already aligned (i.e. they are always
    # reported at the same time)
    if(np.abs(len(data)-len(base)) <= 1):
        print("Data temporally aligned. Using sloppy_regrid for variable " +
              "with units " + str(data_units))
        minlen = min([len(data), len(base)])
        return sloppy_regrid(base[0:minlen-1], data[0:minlen-1],
                             base_times[0:minlen-1], new_res, ascent, units,
                             base_units, data_units)

    # Use negative pressure so that the max of the data list is the peak
    if new_res.dimensionality == units.Pa.dimensionality:
        base = -1*base

    # Create new base list if the one given has not already been regridded
    # Inside if-statement is VERY TIME CONSUMING - only use once per data set.
    # Note: Start is always near the ground, even when analyzing descent
    if(np.abs(base[1]-base[0]) != new_res):
        print("Gridding base")

        # Find a starting base index at least 1 res step above the ground.
        for x, val in enumerate(base):
            if ascent and val > base[0] + new_res:
                base_start_ind = x
            if not ascent and val < base[-1] + new_res:
                base_start_ind = x

        # Round the starting index to a multiple of new_res.
        base_start_val = new_res * round(base[base_start_ind] / new_res)

        # move starting index to match base_start_val
        for x, val in enumerate(base):
            if ascent and val > base_start_val:
                base_start_ind = x
            if not ascent and val < base_start_val:
                base_start_ind = x

        # find highest usable index
        for x, val in enumerate(base):
            if ascent and val > max(base) - 2*new_res:
                base_end_ind = x
            if not ascent and val < max(base) - 2*new_res:
                base_end_ind = x

        # round highest usable alt
        base_end_val = new_res * round(base[base_end_ind] / new_res)

        # Create new base array using start and end vals and res
        if ascent:
            new_base = np.arange(base_start_val.magnitude,
                                 base_end_val.magnitude,
                                 new_res.magnitude) * new_res.units
        else:
            new_base = np.arange(base_end_val.magnitude,
                                 base_start_val.magnitude,
                                 -1*new_res.magnitude) * new_res.units

        #
        # Find corresponding times
        #
        new_times = []
        for elem in new_base:
            # Find the index of the base just past level elem - greater than
            # on ascent, less than on descent
            for x, val in enumerate(base):
                if ascent and val > elem:
                    closest_base_val_ind = x
                    break
                elif not ascent and val < elem:
                    closest_base_val_ind = x
                    break
            new_times.append(base_times[closest_base_val_ind])

    else:
        new_base = base
        new_times = base_times

    #
    # Average around selected points
    #

    # prepare for 1st iteration of data averaging
    if ascent:
        for x, val in enumerate(base):
            if val > new_base[0] - 0.5 * new_res:
                base_seg_start_ind = x
                break
        for x, val in enumerate(data_times):
            if val > base_times[base_seg_start_ind]:
                data_seg_start_ind = x
                break

    else:
        for x, val in enumerate(base):
            if val < new_base[0] + 0.5 * new_res:
                base_seg_start_ind = x
                break
        for x, val in enumerate(data_times):
            if val > base_times[base_seg_start_ind]:
                data_seg_start_ind = x
                break

    new_data = []
    for i in range(len(new_times)):
        level = new_base[i]
        data_seg_end_ind = None
        base_seg_end_ind = None
        # prepare for this iteration
        # The try blocks are needed because the index location algorithm
        # can't handle data that fits perfectly.
        if ascent:
            for x, val in enumerate(base):
                if base_seg_end_ind is not None:
                    break
                if val >= level + 0.4999 * new_res:
                    base_seg_end_ind = x
                    break

        else:
            for x, val in enumerate(base):
                if base_seg_end_ind is not None:
                    break
                if val <= level - 0.4999 * new_res:
                    base_seg_end_ind = x
                    break

        for x, val in enumerate(data_times):
            if data_seg_end_ind is not None:
                break
            if base_seg_end_ind is None:
                # The end of the data has been reached. Use whatever's left
                data_seg_end_ind = -1
                break
            elif val > base_times[base_seg_end_ind]:
                data_seg_end_ind = x
                break

        #
        #
        new_data.append(np.nanmean(data.magnitude[data_seg_start_ind:
                                   data_seg_end_ind]))
        #
        #

        # prepare for next iteration
        base_seg_start_ind = base_seg_end_ind
        data_seg_start_ind = data_seg_end_ind

    new_data = np.array(new_data) * data_units

    if new_res.dimensionality == units.Pa.dimensionality:
        new_base = -1*new_base

    new_base = new_base.to(base_units)
    new_data = new_data.to(data_units)
    return (new_base, new_times, new_data)


def sloppy_regrid(base, data, times, new_res, ascent, units, base_units,
                  data_units):
    """ Significanly faster way to regrid data to be used when data and base
    have the same (+/- 1) length. Assumes that data and base align temporally

    :param list-like<Quantity> base: Measurements of the variable serving as \
       the vertical coordinate
    :param list-like<Quantity> data: Measurements of the dependent variable
    :param list-like<Datetime> times: Times coresponding to data (same as to \
        time)
    :param Quantity new_res: The resolution to which base should be gridded. \
       This must have the same dimension as base.
    :param bool ascent: True if data from ascending leg of profile is to be \
       analyzed, false if descending
    :param pint.UnitRegistry units: The unit registry defined in Profile
    :rtype: tuple
    :return: (new_base, new_times, new_data)
    """

    # Use negative pressure so that the max of the data list is the peak
    if new_res.dimensionality == units.Pa.dimensionality:
        base = -1*base

    # Regrid base
    if ascent:
        new_base = np.arange((base[0] + 0.5*new_res).magnitude, (max(base) -
                             0.5*new_res).magnitude,
                             new_res.magnitude)
    else:
        new_base = np.arange((base[0] - 0.5*new_res).magnitude, (min(base) +
                             0.5*new_res).magnitude,
                             -1*new_res.magnitude)
    new_base = np.array(new_base) * base_units

    # Find times corresponding to regridded base
    new_times = []
    for elem in new_base:
        if ascent:
            closest_base_val_ind = next(x for x, val in enumerate(base)
                                        if val > elem)
        else:
            closest_base_val_ind = next(x for x, val in enumerate(base)
                                        if val < elem)
        new_times.append(times[closest_base_val_ind])

    # Grid data
    new_data = []

    # Prepare for first iteration of data averaging by declaring
    # base_seg_start_ind, base_seg_end_ind, data_seg_start_ind, and
    # data_seg_end_ind.
    base_seg_end_ind = None
    data_seg_end_ind = None
    if ascent:
        base_seg_start_ind = next(x for x, val in enumerate(base)
                                  if val.to_base_units() >
                                  new_base[0].to_base_units() - 0.5 * new_res)
        data_seg_start_ind = next(x for x, val in enumerate(times)
                                  if val > times[base_seg_start_ind])
    else:
        base_seg_start_ind = next(x for x, val in enumerate(base)
                                  if val.to_base_units() <
                                  new_base[0].to_base_units() + 0.5 * new_res)
        data_seg_start_ind = next(x for x, val in enumerate(times)
                                  if val > times[base_seg_start_ind])

    # Begin data averaging
    for i in range(len(new_times)):
        # Prepare for this iteration
        level = new_base[i]
        data_seg_end_ind = None
        base_seg_end_ind = None

        # Determine bounding indices for base based resolution
        if ascent:
            for x, val in enumerate(base):
                if base_seg_end_ind is not None:
                    break
                if val >= level + 0.4999 * new_res:
                    base_seg_end_ind = x
                    break

        else:
            for x, val in enumerate(base):
                if base_seg_end_ind is not None:
                    break
                if val <= level - 0.4999 * new_res:
                    base_seg_end_ind = x
                    break

        # Determine bounding indices for data based on bounding times of base
        for x, val in enumerate(times):
            if data_seg_end_ind is not None:
                break
            if base_seg_end_ind is None:
                # The end of the data has been reached. Use whatever's left
                data_seg_end_ind = -1
                break
            elif val > times[base_seg_end_ind]:
                data_seg_end_ind = x
                break

        #
        #
        new_data.append(np.nanmean(data.magnitude[data_seg_start_ind:
                                   data_seg_end_ind]))
        #
        #

        # prepare for next iteration
        base_seg_start_ind = base_seg_end_ind
        data_seg_start_ind = data_seg_end_ind

    if new_res.dimensionality == units.Pa.dimensionality:
        new_base = -1*new_base
    new_data = np.array(new_data) * data_units

    return(new_base, new_times, new_data)


def temp_calib(resistance, nnumber):
    """ Converts voltage to temperatures using the given coefficients.

    :param list<Quantity> resistance: resistances recorded by temperature \
       sensors
    :param str nnumber: The platform identifier, used to determine which \
       coefficients should be pulled from the database
    :rtype: list<Quantity>
    :return: list of temperatures in K
    """

    print("Temperature calculated from resistance using coefficients ",
          coeff[nnumber])

    return np.pow(np.add(np.add(np.multiply(np.log(resistance),
                                            coeff[nnumber][1])),
                         np.multiply(np.pow(resistance, 3),
                                     coeff[nnumber][2])), -1)


def rotate(u, v, w, yaw, pitch, roll):
    ''' Calculate the value of u, v, and w after a specified axis rotation

    :param list<number> u: U component of the wind
    :param list<number> v: V component of the wind
    :param list<number> w: W component of the wind
    :param list<number> yaw: Rotation about the Z axis
    :param list<number> pitch: Rotation about the X axis
    :param list<number> roll: Rotation about the Y axis
    :rtype: np.array
    :return: 3D array of the new U, V, and W fields after the rotation
    '''

    rot_matrix = np.asarray(
        [[cos(yaw) * cos(pitch),
          cos(yaw) * sin(pitch) * sin(roll) - sin(yaw) * cos(roll),
          cos(yaw) * sin(pitch) * cos(roll) + sin(yaw) * sin(roll)],
         [sin(yaw) * cos(pitch),
          sin(yaw) * sin(pitch) * sin(roll) + cos(yaw) * cos(roll),
          sin(yaw) * sin(pitch) * cos(roll) - cos(yaw) * sin(roll)],
         [-sin(pitch),
          cos(pitch) * sin(roll), cos(pitch) * cos(roll)]])

    vel_matrix = np.asarray([[u], [v], [w]]).transpose()

    result = np.dot(vel_matrix, rot_matrix)

    return result


def qc(data, max_bias, max_variance):
    """ Determines which sensors are not reliable from a given set. Be sure
       to only include like sensors (not both temperature inside and outside
                                     the CO2 sensor) in Data.

    :param list<Quantity> data: a list containing one list for each sensor
       in the ensemble, i.e. all external RH sensors
    :param Quantity max_bias: the maximum absolute difference between the \
       mean of one sensor and the mean of all sensors of that type. This \
       should be determined experimentally for each type of sensor.
    :param Quantity max_variance: the maximum absolute difference between the \
       standard deviation of one sensor and the standard deviation of all \
       sensors of that type. This should be determined experimentally for \
       each type of sensor.
    :rtype: list of length len(data)
    :return: list containing 0 in the position of each "good" sensor, 2 in the
       position of each sensor flagged for bias, and 3 in the position of each
       sensor flagged for response time.
    """

    # _bias: returns list of length number of sensors; 0 means data is good
    good_means = _bias(data, max_bias)
    # _s_dev: returns list of length number of sensors; 0 means data is good
    good_sdevs = _s_dev(data, max_variance)

    combined_sensor_flags = [1] * len(data)

    # Combine good_means and good_sdevs, leaving 0 only where the sensor
    # passed both tests.
    for i in range(len(data)):
        combined_sensor_flags[i] = max([good_means[i], good_sdevs[i]])

    return combined_sensor_flags


def _bias(data, max_abs_error):
    """ This method identifies sensors with excessive biases and returns a
    list flagging sensors determined to be questionable.

    :param np.array<Quantity> data: a list containing one list for each sensor
       in the ensemble, i.e. all external RH sensors
    :param Quantity max_abs_error: sensors with means more than
       max_abs_error from the mean of sensor means will be flagged
    :rtype: list of length len(data)
    :return: list containing 0s by default and 2 in the position of each sensor
       flagged for bias.
    """
    to_return = np.zeros(len(data))
    # Calculate the mean of each sensor
    means = np.zeros(len(data))
    for i in range(len(data)):
        means[i] = np.nanmean(data[i].magnitude)

    while(True):
        # Identify the sensor with the mean farthest from the mean of means
        max_diff = 0
        furthest_from_mean = 0  # index of sensor furthest from mean

        for j in range(len(data)):

            if(np.abs(np.nanmean(means)-means[j]) >
               np.abs(np.nanmean(means)-means[furthest_from_mean])):
                furthest_from_mean = j

            for k in range(len(data)):
                if(np.abs(means[j]-means[k]) > max_diff):
                    max_diff = np.abs(means[j]-means[k])

            # If the furthest sensor is farther than max_abs_error from the
            # mean of means, eliminate it and perform analysis again.
            if(max_diff > max_abs_error):
                to_return[furthest_from_mean] = 2
                means[furthest_from_mean] = np.NaN
            else:
                return to_return


def _s_dev(data, max_abs_error):
    """ This method identifies sensors with excessively low or high
    variabilities and returns a list flagging sensors determined to be
    questionable.

    :param np.array<Quantity> data: a list containing one list for each sensor
       in the ensemble, i.e. all external RH sensors
    :param Quantity max_abs_error: sensors with standard deviations will be
       flagged.
    :rtype: list of length len(data)
    :return: list containing 0s by default and 3 in the position of each sensor
       flagged for variability.
    """
    to_return = np.zeros(len(data))
    # Calculate the mean of each sensor
    sdevs = np.zeros(len(data))
    for i in range(len(data)):
        sdevs[i] = np.nanstd(data[i].magnitude)

    while(True):
        # Identify the sensor with the mean farthest from the mean of means
        max_diff = 0
        furthest_from_mean = 0  # index of sensor furthest from mean

        for j in range(len(data)):

            if(np.abs(np.nanmean(sdevs)-sdevs[j]) >
               np.abs(np.nanmean(sdevs)-sdevs[furthest_from_mean])):
                furthest_from_mean = j

            for k in range(len(data)):
                if(np.abs(sdevs[j]-sdevs[k]) > max_diff):
                    max_diff = np.abs(sdevs[j]-sdevs[k])

            # If the furthest sensor is farther than max_abs_error from the
            # mean of means, eliminate it and perform analysis again.
            if(max_diff > max_abs_error):
                to_return[furthest_from_mean] = 3
                sdevs[furthest_from_mean] = np.NaN
            else:
                return to_return


def identify_profile(alts, alt_times, confirm_bounds=True,
                     profile_start_height=None, to_return=[], ind=0):
    """ Identifies the temporal bounds of all profiles in the data file. These
    assumptions must be valid:
    * The craft starts and ends each profile below profile_start_height
    * The craft does not go above profile_start_height until the first
    profile is started
    * The craft does not go above profile_start_height after the last
    profile is ended.

    :rtype: list<tuple>
    :return: a list of times defining the profiles in the format \
       (time_start, time_max_height, time_end)
    """
    # Get the starting height from the user
    if profile_start_height is None:
        fig1 = plt.figure()
        plt.plot(alt_times, alts, figure=fig1)
        plt.grid(axis="y", which="both", figure=fig1)

        myFmt = mdates.DateFormatter('%M')
        fig1.gca().xaxis.set_major_formatter(myFmt)

        plt.show(block=False)

        try:
            profile_start_height = int(input('Wrong file? Enter "q" to quit. '
                                             + '\nProfile start height: '))
        except ValueError:
            sys.exit(0)
        plt.close()

    # If no profiles exist after ind, return an empty index list.
    if max(alts[ind:]) < profile_start_height:
        return []

    # Declare variables used in loop
    start_ind_asc = None
    end_ind_des = None
    peak_ind = None

    # Check through valid alts for start_ind_asc, peak_ind, end_ind_des in
    # that order
    while ind < len(alts) - 10:
            if(start_ind_asc is None):  # should be ascending
                # finds at what time the altitude range is reached going up

                # Error if starts on a descent
                if(alts[ind] > profile_start_height and
                   alts[ind + 10] < alts[ind]):
                    print("Error separating profiles: start height is first \
                          reached on a descent")
                    break

                # Set start_ind_asc when the craft is first above
                # profile_start_height
                if alts[ind] > profile_start_height:
                    start_ind_asc = ind

                ind += 1

            elif(end_ind_des is None):  # should be descending

                # Set end_ind_des when the craft is again below
                # profile_start_height for the first time since start_ind_asc
                if alts[ind] < profile_start_height:
                    end_ind_des = ind

                    # Now that the bounds of the profile have been found, we
                    # find the index of the maximum altitude.
                    peak_ind = np.where(alts == np.nanmax(alts[start_ind_asc:
                                                          end_ind_des]))[0][0]

                ind += 1

            # The current profile has been processed; we just need to check
            # if there are more profiles in the file
            else:
                if confirm_bounds:
                    # User verifies selection
                    fig2 = plt.figure()
                    plt.plot(alt_times, alts, figure=fig2)
                    plt.grid(axis="y", which="both", figure=fig2)

                    myFmt = mdates.DateFormatter('%M')
                    fig2.gca().xaxis.set_major_formatter(myFmt)

                    plt.vlines([alt_times[start_ind_asc],
                                alt_times[peak_ind],
                                alt_times[end_ind_des]],
                               min(alts) - 50, max(alts) + 50)

                    plt.show(block=False)

                    # Get user opinion
                    valid = input('Correct? (Y/n): ')
                    # If good, wrap up the profile
                    if valid in "yYyesYes" or valid is "":
                        plt.close()
                        if end_ind_des is None:
                            print("Could not find end time des (LineTag B)")
                            return
                        # Add the profile if it is not already in to_return
                        pending_profile = (alt_times[start_ind_asc],
                                           alt_times[peak_ind],
                                           alt_times[end_ind_des])
                        if not _profile_in(pending_profile, to_return):
                            to_return.append((alt_times[start_ind_asc],
                                              alt_times[peak_ind],
                                              alt_times[end_ind_des]))

                            print("Profile from ", alt_times[start_ind_asc],
                                  "to", alt_times[end_ind_des], "added")
                        # Check if more profiles in file
                        if ind + 500 < len(alts) \
                           and max(alts[ind + 500::]) > \
                           (profile_start_height + alts[600] - alts[500]):
                            # There is another profile before the end of the
                            # file - find it.
                            a = profile_start_height
                            to_return =\
                             identify_profile(alts, alt_times,
                                              confirm_bounds=confirm_bounds,
                                              profile_start_height=a,
                                              to_return=to_return,
                                              ind=ind + 500)
                            # Break because the rest of the file will be
                            # processed by the previous call.
                            break

                        ind += 1
                        return to_return

                    elif valid in "nNnoNo":
                        print(max(alts[ind:]), profile_start_height)
                        plt.close()
                        to_return = identify_profile(alts, alt_times,
                                                     to_return)
                    else:
                        print("Invalid choice. Re-selecting profile...")
                        plt.close()
                        to_return = identify_profile(alts, alt_times,
                                                     to_return)

    return to_return


def _profile_in(indices, all_indices):
    """ Helper function for identify_profile to ensure similar or overlapping
    profiles not included
    """
    for profile_n in all_indices:
        # Check for similar
        if ((profile_n[0]-indices[0] <= timedelta(seconds=5)
           and indices[0]-profile_n[0] <= timedelta(seconds=5)) or
           (profile_n[1]-indices[1] <= timedelta(seconds=5)
           and indices[1]-profile_n[1] <= timedelta(seconds=5)) or
           (profile_n[2]-indices[2] <= timedelta(seconds=5)
           and indices[2]-profile_n[2] <= timedelta(seconds=5))):
            return True
        # Check for overlapping
        if indices[1] > profile_n[0] and indices[1] < profile_n[2]:
            return True
    return False
