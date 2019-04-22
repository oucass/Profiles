"""
Manages data from a single flight or profile

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
from numpy import sin as sin
from numpy import cos as cos
import numpy as np
import utils
from Raw_Profile import Raw_Profile
from Thermo_Profile import Thermo_Profile


class Profile():
    """ A Profile object contains data from a profile (if altitude or pressure
    is specified under resolution) or flight (if the resolution is in units
    of time)

    :var tuple gps: location info as tuple(lat: list<float>, lon: list<float>,
       alt_msl: list<Quantity>, gps_time: list<Datetime>)
    :var bool dev: True if data is from developmental flights
    :var Location location: information about the flight location
    :var Quantity resolution: resolution of the data in units of time,
       altitude, or pressure
    """

    def __init__(self, file_path, resolution, res_units, profile_num,
                 ascent=True, dev=False):
        """ Creates a Profile object.

        :param string fpath: data file
        :param Quantity resolution: resolution to which data should be
           calculated in units of time, altitude, or pressure
        :param str res_units: units of resolution in a format which can \
           be parsed by pint
        :param bool dev: True if data is from a developmental flight
        """
        self._raw_profile = Raw_Profile(file_path, dev)
        self._units = self._raw_profile.get_units()
        self._pos = self._raw_profile.pos_data()
        # TODO pull out ground alt here to define AGL
        indices = utils.identify_profile(self._pos["alt_MSL"].magnitude,
                                         self._pos["time"])[profile_num - 1]
        print(indices)

        if ascent:
            self.indices = (indices[0], indices[1])
        else:
            self.indices = (indices[1], indices[2])
        self._wind_profile = None
        self._thermo_profile = None
        self._co2_profile = None
        self.dev = dev
        self.location = None
        # TODO altitude QC https://github.com/oucass/ISOBAR/blob/master/data_class.py p2alt
        self.resolution = resolution * self._units.parse_expression(res_units)
        self.ascent = ascent

    def get_wind_profile(self):
        if self._wind_profile is None:
            a = 2  # TODO Calculate it
        return self._wind_profile

    def get_thermo_profile(self):
        if self._thermo_profile is None:
            thermo_data = self._raw_profile.thermo_data()
            self._thermo_profile = \
                Thermo_Profile(thermo_data,
                               self.resolution, indices=self.indices,
                               ascent=self.ascent, units=self._units)
                # TODO alt QC in Thermo_Profile

        return self._thermo_profile

    def get_co2_profile(self):
        if self._co2_profile is None:
            a = 2  # TODO Calculate it
        return self._co2_profile


a = Profile("/home/jessica/GitHub/data_templates/00000136.json", 10, 'Pa', 1, ascent=False)
