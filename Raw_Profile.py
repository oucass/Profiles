"""
Reads data file (JSON or netCDF) and stores the raw data

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import pint
import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

units = pint.UnitRegistry()


class Raw_Profile():
    """ Contains data from one file. Data is stored as a pandas DataFrame.

    :var tuple temp: temperature as (voltage1, voltage2, ..., time: ms)
    :var tuple rh: relative humidity as (rh1, T1, rh2, T2, ..., time: ms)
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
        self._read_JSON(file_path)

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

    def _read_JSON(self, file_path):
        """ Reads data from a .JSON file. Called by the constructor.
        """

        # Read the file into a list which pandas can normalize and read
        full_data = []
        for line in open(file_path, 'r'):
            full_data.append(json.loads(line))

        """
        Now full_data is a list of JSON element with 2 dictionaries each. If
        we refer to one JSON element as "tweet", the structure can be described
        as follows:

        tweet["meta"] contains "timestamp" and "type".

        tweet["data"] depends on tweet["meta"]["type"]. IMET, for example,
        could contain
            Temp1, float, 1, 286.2941589355469
            Temp2, float, 1, 286.27020263671875
            Temp3, float, 1, 286.0711364746094
            Temp4, float, 1, 0.0
            Time, int, 1, 60898080
            Volt1, float, 1, 4441.3125
            Volt2, float, 1, 4431.5625
            Volt3, float, 1, 4429.875
            Volt4, float, 1, 0.0

        Next, we iterate through full_data and identify line containing the
        types we want to keep. We then extract the data from each element
        using a different code for each type.
        """
        temp_list = None
        rh_list = None
        # sensor_names will be dictionary of dictionaries formatted
        # {
        #     "IMET": {name: index, name: index, ...},
        #     "RHUM": {name: index, name: index, ...},
        #     ...
        # }
        sensor_names = {}
        for elem in full_data:

            # IMET
            if elem["meta"]["type"] == "IMET":

                # First time only - setup temp_list
                if temp_list is None:
                    # Create array of lists with one list per temperature
                    # sensor reported in the data file, plus one for times
                    temp_list = [[] for x in range(sum('Volt' in s for s in
                                 elem["data"].keys())+1)]

                    sensor_names["IMET"] = {}
                    # Determine field names
                    sensor_numbers = np.add(range(len(temp_list)-1), 1)
                    for num in sensor_numbers:
                        sensor_names["IMET"]["Volt"+str(num)] = num - 1
                    sensor_names["IMET"]["Time"] = -1

                # Read fields into temp_list, including Time
                for key, value in sensor_names["IMET"].items():
                    try:
                        temp_list[value].append(elem["data"][key])
                    except KeyError:
                        temp_list[value].append(np.nan)

            elif elem["meta"]["type"] == "RHUM":

                # First time only - setup rh_list and temp_rh_list
                if rh_list is None:
                    # Create array of lists with one list per RH
                    # sensor reported in the data file, plus one for times
                    rh_list = [[] for x in range(sum('Humi' in s for s in
                               elem["data"].keys()) * 2 + 1)]
    
                    sensor_names["RHUM"] = {}
                    # Determine field names
                    sensor_numbers = np.add(range(int((len(rh_list)-1)/2)), 1)
                    for num in sensor_numbers:
                        sensor_names["RHUM"]["Humi"+str(num)] = 2*num - 2
                        sensor_names["RHUM"]["Temp"+str(num)] = 2*num - 1
                    sensor_names["RHUM"]["Time"] = -1

                # Read fields into temp_list, including Time
                for key, value in sensor_names["RHUM"].items():
                    try:
                        rh_list[value].append(elem["data"][key])
                    except KeyError:
                        temp_list[value].append(np.nan)

        self.temp = tuple(temp_list)
        self.rh = tuple(rh_list)

    def _read_netCDF(self):
        """ Reads data from a NetCDF file. Called by the constructor.
        """

    def _save_netCDF(self):
        """ Save a NetCDF file to facilitate future processing if a .JSON was
        read.
        """
