"""
Utils contains misc. functions to aid in data analysis.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright U of Oklahoma Center for Autonomous Sensing and Sampling 2019
"""


from numpy import sin as sin
from numpy import cos as cos
import numpy as np


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


def qc(data):
    """ Determines which sensors are not reliable from a given set. Be sure
       to only include like sensors (not both temperature inside and outside
                                     the CO2 sensor) in Data.

    :param list<Quantity> data: a list containing one list for each sensor
       in the ensemble, i.e. all external RH sensors
    :rtype: list of length len(data)
    :return: list containing 1 in the position of each "good" sensor, 2 in the
       position of each sensor flagged for bias, and 3 in the position of each
       sensor flagged for response time.
    """


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
