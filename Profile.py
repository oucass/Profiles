"""
Manages data from a single flight or profile

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
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
                 ascent=True, dev=False, confirm_bounds=True):
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
        indices = utils.identify_profile(self._pos["alt_MSL"].magnitude,
                                         self._pos["time"], confirm_bounds
                                         )[profile_num - 1]

        if ascent:
            self.indices = (indices[0], indices[1])
        else:
            self.indices = (indices[1], indices[2])
        self._wind_profile = None
        self._thermo_profile = None
        self._co2_profile = None
        self.dev = dev
        self.location = None
        self.resolution = resolution * self._units.parse_expression(res_units)
        self.ascent = ascent
        if ".nc" in file_path:
            self.file_path = file_path[:-3]
        elif ".json" in file_path:
            self.file_path = file_path[:-5]

    def get_wind_profile(self):
        """ If a Wind_Profile object does not already exist, it is created when
        this method is called.

        :return: the Wind_Profile object
        :rtype: Wind_Profile
        """
        if self._wind_profile is None:
            a = 2  # TODO Calculate it
        return self._wind_profile

    def get_thermo_profile(self):
        """ If a Thermo_Profile object does not already exist, it is created
        when this method is called.

        :return: the Thermo_Profile object
        :rtype: Thermo_Profile
        """
        if self._thermo_profile is None:
            thermo_data = self._raw_profile.thermo_data()
            self._thermo_profile = \
                Thermo_Profile(thermo_data,
                               self.resolution, indices=self.indices,
                               ascent=self.ascent, units=self._units,
                               filepath=self.file_path)

        return self._thermo_profile

    def get_co2_profile(self):
        """ If a CO2_Profile object does not already exist, it is created when
        this method is called.

        :return: the CO2_Profile object
        :rtype: CO2_Profile
        """
        if self._co2_profile is None:
            a = 2  # TODO Calculate it
        return self._co2_profile
