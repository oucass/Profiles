"""
Calculates and stores wind parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
import numpy as np

class Wind_Profile():
    """ Contains data from one file.

    :var list<Quantity> u: U component of wind
    :var list<Quantity> v: V-component of wind
    :var list<Datetime> time: time of each point
    """

    def __init__(self, wind_data, resolution, isCopter=True):
        """ Creates Wind_Profile object based on rotation data at the specified
        resolution.
        """
        self.u = None
        self.v = None
        self.dir = None
        self.speed = None
        self.time = None
        self._calc_winds(wind_data) # TODO integrate result

    def _calc_winds(self, wind_data):
        """ Calculate wind direction, speed, u, and v
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

            Rx = np.matrix([[1, 0, 0],
                            [0, croll, sroll],
                            [0, -sroll, croll]])
            Ry = np.matrix([[cpitch, 0, -spitch],
                            [0, 1, 0],
                            [spitch, 0, cpitch]])
            Rz = np.matrix([[cyaw, -syaw, 0],
                            [syaw, cyaw, 0],
                            [0, 0, 1]])
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
