"""
Reads data file (JSON or netCDF) and stores the raw data

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import pint

units = pint.UnitRegistry()


class Raw_Profile():
    """ Contains data from one file.

    :var tuple temp: temperature as (voltage1, voltage2, ..., time: ms)
    :var tuple rh: relative humidity as (rh1, rh2, ..., time: ms)
    :var tuple temp_rh: temperature as (voltage1, voltage2, ..., time: ms)
    :var tuple co2: CO2 data as (CO2, CO2, ..., time: ms)
    :var tuple gps: GPS data as (lat, lon, alt_MSL, time: Datetime)
    :var tuple pres: barometer data as (pres, time: ms)
    :var tuple rotation: UAS position data as (roll, pitch, yaw, time:ms)
    :var bool dev: True if the data is from a developmental flight
    """

    def __init__(self, file_path, dev=False):
        """ Creates a Raw_Profile object and reads in data in the appropiate
        format.
        """
        self.temp = None
        self.rh = None
        self.temp_rh = None
        self.co2 = None
        self.gps = None
        self.pres = None
        self.rotation = None
        self.dev = None

    def thermo_data(self):
        """ Gets data needed by the Thermo_Profile constructor.

        rtype: list
        return: [temp, rh, pres]
        """

    def co2_data(self):
        """ Gets data needed by the CO2_Profile constructor.

        rtype: list
        return: [co2, temp, rh]
        """

    def wind_data(self):
        """ Gets data needed by the Wind_Profile constructor.

        rtype: list
        return: [rotation]
        """

    def _read_JSON(self):
        """ Reads data from a .JSON file. Called by the constructor.
        """

    def read_netCDF(self):
        """ Reads data from a NetCDF file. Called by the constructor.
        """

    def _save_netCDF(self):
        """ Save a NetCDF file to facilitate future processing if a .JSON was
        read.
        """