"""
Utils contains misc. functions to aid in data analysis.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright U of Oklahoma Center for Autonomous Sensing and Sampling 2019
"""

import numpy as np
import matplotlib.pyplot as plt
import pint
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
units = pint.UnitRegistry()


def regrid(base=None, base_times=None, data=None, data_times=None,
           new_res=None):
    """ Returns data interpolated to an evenly spaced array with resolution
        new_res.

        :cite: https://www.geeksforgeeks.org/python-get-the-index-of-first- \
           element-greater-than-k/
    """
    data = data.to_base_units()
    base = base.to_base_units()
    new_res = new_res.to_base_units()

    # Use negative pressure so that the max of the data list is the peak
    if new_res.dimensionality == units.Pa.dimensionality:
        data = -1*data

    #
    # Create new base list
    #

    # Find a starting base index at least 1 resolution step above the ground.
    base_start_ind = next(x for x, val in enumerate(base)
                          if val > base[0] + new_res)
    # Round the starting index to a multiple of new_res.
    base_start_val = new_res * round(base[base_start_ind] / new_res)
    # move starting index to match sbase_start_val
    base_start_ind = next(x for x, val in enumerate(base)
                          if val > base_start_val)
    # find highest usable index
    base_end_ind = next(x for x, val in enumerate(base)
                        if val > max(base) - 2*new_res)
    # round highest usable alt
    base_end_val = new_res * round(base[base_end_ind] / new_res)

    new_base = np.arange(base_start_val.magnitude, base_end_val.magnitude,
                         new_res.magnitude) * new_res.units

    #
    # Find corresponding times
    #
    new_times = []
    for elem in new_base:
        closest_base_val_ind = next(x for x, val in enumerate(base)
                                    if val > elem)
        new_times.append(base_times[closest_base_val_ind])

    #
    # Average around selected points
    #

    # prepare for 1st iteration
    base_seg_start_ind = next(x for x, val in enumerate(base)
                              if val > new_base[0] - 0.5 * new_res)
    data_seg_start_ind = next(x for x, val in enumerate(data_times)
                              if val > base_times[base_seg_start_ind])

    new_data = []
    for i in range(len(new_base)):
        # prepare for this iteration
        base_seg_end_ind = next(x for x, val in enumerate(base)
                                if val > new_base[i] + 0.5 * new_res)
        data_seg_end_ind = next(x for x, val in enumerate(data_times)
                                if val > base_times[base_seg_end_ind])

        #
        #
        new_data.append(np.nanmean(data.magnitude[data_seg_start_ind:
                                                  data_seg_end_ind]))
        #
        #

        # prepare for next iteration
        base_seg_start_ind = base_seg_end_ind
        data_seg_start_ind = data_seg_end_ind

    new_data = new_data * data.units

    if new_res.dimensionality == units.Pa.dimensionality:
        new_data = -1*new_data

    return (new_base, new_times, new_data)


def trim_to_profile():
    """ Returns time bounds of a vertical profile
    """


def temp_calib(temp, coefs):
    """ Converts voltage to temperatures using the given coefficients.

    :param list<Quantity> temp: voltages recorded by temperature sensors
    :param list<Quantity> coefs: coefficients to convert voltage to
       temperature. The coefficients should be determined seperately for
       each sensor
    :rtype: list<Quantity>
    :return: list of temperatures in K
    """


def correct_alt_pres(gps, pres):
    """ Uses pressure data to correct altitude data.

    :param tuple gps: GPS data as (lat, lon, alt_MSL, time: Datetime)
    :param tuple pres: barometer data as (pres, time: ms)
    :rtype: tuple
    :return: gps with corrected altitudes
    """


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

    # TODO: Test this function and downstream functions (_bias, _s_dev)
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

    :param list<Quantity> data: a list containing one list for each sensor
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
        means[i] = np.nanmean(data[i])

    while(True):
        # Identify the sensor with the mean farthest from the mean of means
        max_diff = 0  # TODO this should be the same type of Quantity as Data
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

    :param list<Quantity> data: a list containing one list for each sensor
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
        sdevs[i] = np.nanstd(data[i])

    while(True):
        # Identify the sensor with the mean farthest from the mean of means
        max_diff = 0  # TODO this should be the same type of Quantity as Data
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


def identify_profile(alts, alt_times, profile_start_height=None,
                     toReturn=[], ind=0):
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

        fig1.gca().tick_params(axis='x', which='both', bottom=False,
                               labelbottom=False)

        plt.show(block=False)

        profile_start_height = int(input('Profile start height: '))
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
                if(not (start_ind_asc, peak_ind, end_ind_des) in toReturn):
                    toReturn.append((alt_times[start_ind_asc],
                                     alt_times[peak_ind],
                                     alt_times[end_ind_des]))
                if end_ind_des is None:
                    print("Could not find end time des (LineTag B)")  # B
                if alts[ind] > profile_start_height:
                    # There is another profile before the end of the file -
                    # find it.
                    identify_profile(alts, profile_start_height, toReturn,
                                     ind=ind + 10)
                    # Break because the rest of the file will be processed by
                    # the previous call.
                    break

                ind += 1

    return toReturn
