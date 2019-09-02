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
import pandas as pd
from datetime import timedelta
from pandas.plotting import register_matplotlib_converters
from pint import UnitStrippedWarning


warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("error", category=UnitStrippedWarning)
register_matplotlib_converters()
coefs = None


def regrid_base(base=None, base_times=None, new_res=None, ascent=True,
                units=None):
    """ Calculates times at which data means should be calculated.

    :param np.array<Quantity> base: Measurements of the variable serving as \
       the vertical coordinate
    :param np.array<Datetime> base_times: Times coresponding to base
    :param Quantity new_res: The resolution to which base should be gridded. \
       This must have the same dimension as base.
    :param bool ascent: True if data from ascending leg of profile is to be \
       analyzed, false if descending
    :param pint.UnitRegistry units: The unit registry defined in Profile
    :rtype: (np.Array<Datetime>, np.Array<Quantity>)
    :return: times at which the craft is at vertical points z*res above \
       ground and the corrosponding base values
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
    new_base = np.array(new_base) * base.units

    # Find times corresponding to regridded base
    new_times = []
    for elem in new_base:
        if ascent:
            closest_base_val_ind = next(x for x, val in enumerate(base)
                                        if val > elem)
        else:
            closest_base_val_ind = next(x for x, val in enumerate(base)
                                        if val < elem)
        new_times.append(base_times[closest_base_val_ind])
    return (new_times, new_base)


def regrid_data(data=None, data_times=None, gridded_times=None, units=None):
    """ Returns data interpolated to an evenly spaced array based on
    gridded_times.

    :param np.array<Quantity> data: Measurements of the dependent variable
    :param np.array<Datetime> data_times: Times coresponding to data
    :param pint.UnitRegistry units: The unit registry defined in Profile
    :param np.Array<Datetime> gridded_times: The times returned by regrid_base
    :cite: https://www.geeksforgeeks.org/python-get-the-index-of-first- \
       element-greater-than-k/
    :rtype: np.Array<Quantity>
    :return: gridded_data
    """

    #
    # Average around selected points
    #
    data_index = 0  # This tracks the most recent data element processed

    gridded_data = []
    for i in range(len(gridded_times)-1):
        #
        # Find the data indicies in the specified time range
        #
        start_time = gridded_times[i]
        end_time = gridded_times[i+1]
        data_seg_start_ind = None
        data_seg_end_ind = None

        while(data_index < len(data)):
            if data_times[data_index] >= start_time:
                data_seg_start_ind = data_index
                break
            data_index += 1

        while(data_index < len(data)):
            if data_times[data_index] >= end_time:
                data_seg_end_ind = data_index
                break
            data_index += 1

        # Calculate and store the segment mean
        if (data_seg_start_ind is not None and data_seg_end_ind is not None):
            gridded_data.append(np.nanmean(data.magnitude[data_seg_start_ind:
                                           data_seg_end_ind]))

    gridded_data = np.array(gridded_data) * data.units

    return (gridded_data)


def temp_calib(resistance, sn):
    """ Converts voltage to temperatures using the given coefficients.

    :param list<Quantity> resistance: resistances recorded by temperature \
       sensors
    :param str nnumber: The platform identifier, used to determine which \
       coefficients should be pulled from the database
    :rtype: list<Quantity>
    :return: list of temperatures in K
    """

    coefs = pd.read_csv('./MasterCoefList.csv')
    a = float(coefs.A[coefs.SerialNumber == sn][coefs.SensorType == "Imet"])
    b = float(coefs.B[coefs.SerialNumber == sn][coefs.SensorType == "Imet"])
    c = float(coefs.C[coefs.SerialNumber == sn][coefs.SensorType == "Imet"])
    print("Temperature calculated from resistance using coefficients \n",
          coefs[coefs.SerialNumber == sn
                and 'IMet' in coefs.ShortSensorID])

    return np.power(np.add(np.add(b * np.log(resistance.magnitude), a),
                    c * np.power(np.log(resistance.magnitude), 3)), -1)


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

    isDone = False

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
                        isDone = True
                        break
                    elif valid in "nNnoNo":
                        plt.close()
                        to_return = identify_profile(alts, alt_times,
                                                     to_return)
                    else:
                        print("Invalid choice. Re-selecting profile...")
                        plt.close()
                        to_return = identify_profile(alts, alt_times,
                                                     to_return)
                else:
                    isDone = True

                ind += 1

    if(isDone):
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


def calc_winds(wind_data, isCopter=True):
    """ MUST BE COPTER
    Calculates wind data based on roll, pitch, and yaw of copter

    :param dict wind_data: dictionary from Raw_Profile.get_wind_data()
    :param bool isCopter: True if rotor-wing, false if fixed-wing
    :rtype: tuple<list>
    :return: (direction, speed)
    """

    # TODO find a way to do this with a fixed-wing

    units = wind_data["units"]

    # psi and az represent the copter's direction in spherical coordinates
    psi = np.zeros(len(wind_data["roll"])) * units.deg
    az = np.zeros(len(wind_data["roll"])) * units.deg

    for i in range(len(wind_data["roll"])):
        # croll is cos(roll), sroll is sin(roll)...
        croll = np.cos(wind_data["roll"][i] * np.pi / 180.)
        sroll = np.sin(wind_data["roll"][i] * np.pi / 180.)
        cpitch = np.cos(wind_data["pitch"][i] * np.pi / 180.)
        spitch = np.sin(wind_data["pitch"][i] * np.pi / 180.)
        cyaw = np.cos(wind_data["yaw"][i] * np.pi / 180.)
        syaw = np.sin(wind_data["yaw"][i] * np.pi / 180.)

        Rx = np.matrix([[1, 0, 0], [0, croll, sroll], [0, -sroll, croll]])
        Ry = np.matrix([[cpitch, 0, -spitch], [0, 1, 0], [spitch, 0, cpitch]])
        Rz = np.matrix([[cyaw, -syaw, 0], [syaw, cyaw, 0], [0, 0, 1]])
        R = Rz * Ry * Rx

        psi[i] = np.arccos(R[2, 2]) * 180. / np.pi
        az[i] = np.arctan2(R[1, 2], R[0, 2]) * 180. / np.pi

    # TODO read calibration values from file
    a_spd = 34.5
    b_spd = -6.4

    speed = a_spd * np.sqrt(np.tan(psi * np.pi / 180.)) + b_spd
    speed = speed * units.mps
    # Throw out negative speeds
    speed[speed.magnitude < 0.] = np.nan

    # Fix negative angles
    iNeg = np.squeeze(np.where(az.magnitude < 0.))
    az[iNeg] = az[iNeg] + 360. * units.deg

    # az is the wind direction, speed is the wind speed
    return (az, speed)
