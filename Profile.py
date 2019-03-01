"""
Manages data from a single flight or profile

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""


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

    def __init__(self, file_path, resolution, dev=False):
        """ Creates a Profile object.

        :param string fpath: data file
        :param Quantity resolution: resolution to which data should be
           calculated in units of time, altitude, or pressure
        :param bool dev: True if data is from a developmental flight
        """
        self._raw_profile = None
        self._wind_profile = None
        self._thermo_profile = None
        self._co2_profile = None
        self.gps = None
        self.dev = None
        self.location = None
        self.resolution = None

    def get_wind_profile(self):
        if self._wind_profile is None:
            a = 2  # TODO Calculate it
        return self._wind_profile

    def get_thermo_profile(self):
        if self._themo_profile is None:
            a = 2  # TODO Calculate it
        return self._thermo_profile

    def get_co2_profile(self):
        if self._co2_profile is None:
            a = 2  # TODO Calculate it
        return self._co2_profile
