"""
Calculates and stores wind parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
import numpy as np
import pandas as pd
import os
import utils
import metpy.calc


class Wind_Profile():
    """ Contains data from one file.

    :var list<Quantity> u: U component of wind
    :var list<Quantity> v: V-component of wind
    :var list<Datetime> gridded_times: time of each point
    """

    def __init__(self, wind_dict, resolution, gridded_times=None,
                 indices=(None, None), ascent=True, units=None, filepath='',
                 vertical_coord_times=[], tail_number=None):
        """ Creates Wind_Profile object based on rotation data at the specified
        resolution.
        """

        self.gridded_times = gridded_times

        filepath_nc = filepath + "wind_" + str(resolution.magnitude) + \
            str(resolution.units) + self._ascent_filename_tag + ".nc"

        if os.path.basename(filepath_nc) in os.listdir(self._datadir):
            print("Reading wind_profile from pre-processed netCDF")
            self._read_netCDF(filepath_nc)
            return
        else:
            time_raw = wind_dict["time"]
            # If no indices given, use entire file
            if not indices[0] is None:
                # trim profile

                selection = np.where(np.array(time_raw) > indices[0],
                                     np.array(time_raw) < indices[1], False)

                roll = np.array(wind_dict["roll"].magnitude)[selection] * \
                    wind_dict["roll"].units
                pitch = np.array(wind_dict["pitch"].magnitude)[selection] * \
                    wind_dict["pitch"].units
                yaw = np.array(wind_dict["yaw"].magnitude)[selection] * \
                    wind_dict["yaw"].units
                vE = np.array(wind_dict["speed_east"].magnitude)[selection] * \
                    wind_dict["speed_east"].units
                vN = np.array(wind_dict["speed_north"].magnitude)[selection] \
                    * wind_dict["speed_north"].units
                vD = np.array(wind_dict["speed_down"].magnitude)[selection] * \
                    wind_dict["speed_down"].units
                time_raw = np.array(time_raw)[selection]
            else:
                roll = wind_dict["roll"]
                pitch = wind_dict["pitch"]
                yaw = wind_dict["yaw"]
                vE = wind_dict["speed_east"]
                vN = wind_dict["speed_north"]
                vD = wind_dict["speed_down"]

        wind_data = {'roll': roll,
                     'pitch': pitch,
                     'yaw': yaw,
                     'vE': vE,
                     'vN': vN,
                     'vD': vD}

        direction, speed, time = self._calc_winds(wind_data, tail_number)

        #
        # Regrid to res
        #
        self.dir = utils.regrid_data(data=direction, data_times=time,
                                     gridded_times=self.gridded_times,
                                     units=self._units)
        self.speed = utils.regrid_data(data=speed, data_times=time,
                                       gridded_times=self.gridded_times,
                                       units=self._units)
        self.u, self.v = metpy.calc.get_wind_components(self.speed, self.dir)

        #
        # save NC
        #
        self._save_NetCDF()

    def _calc_winds(self, wind_data, tail_num):
        """ Calculate wind direction, speed, u, and v. Currently, this only
        works when the craft is HORIZONTALLY STATIONARY.
        :param dict wind_data: dictionary from Raw_Profile.get_wind_data()
        :param bool isCopter: True if rotor-wing, false if fixed-wing
        :rtype: tuple<list>
        :return: (direction, speed)
        """

        # TODO find a way to do this with a fixed-wing
        # TODO account for moving platform
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

        coefs = pd.read_csv('./MasterCoefList.csv')
        a_spd = float(coefs.A[coefs.SerialNumber == tail_num])
        b_spd = float(coefs.B[coefs.SerialNumber == tail_num])

        speed = a_spd * np.sqrt(np.tan(psi * np.pi / 180.)) + b_spd
        speed = speed * units.mps
        # Throw out negative speeds
        speed[speed.magnitude < 0.] = np.nan

        # Fix negative angles
        iNeg = np.squeeze(np.where(az.magnitude < 0.))
        az[iNeg] = az[iNeg] + 360. * units.deg

        # az is the wind direction, speed is the wind speed
        return (az, speed, wind_data["time"])

    def _read_NetCDF(self, filepath_nc):
        # TODO make real version
        print("Finish implementing Wind_Profile")

    def _save_NetCDF(self, filepath):
        # TODO make real version
        print("Finish implementing Wind_Profile")
