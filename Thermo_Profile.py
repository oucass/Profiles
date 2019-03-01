"""
Calculates and stores basic thermodynamic parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import pint

units = pint.UnitRegistry()


class Thermo_Profile():
    """ Contains data from one file.

    :var tuple<list<Quantity>, Datetime> temp: QC'd and averaged temperature
    :var tuple<list<Quantity>, Datetime> mixing_ratio: calculated mixing ratio
    :var tuple<list<Quantity>, Datetime> pres: QC'd pressure
    :var list<Datetime> time: times at which processed data exists
    :var Quantity resolution: vertical resolution in units of time,
           altitude, or pressure to which the data is calculated
    """

    def __init__(self, temp_raw, rh_raw, pres_raw, resolution):
        """ Creates Thermo_Profile object from raw data at the specified
        resolution.

        :param tuple temp_raw: temperature as
           (voltage1, voltage2, ..., time: ms)
        :param tuple rh_raw: relative humidity as (rh1, rh2, ..., time: ms)
        :param tuple pres_raw: barometer data as (pres, time: ms)
        :param Quantity resoltion: vertical resolution in units of time,
           altitude, or pressure to which the data should be calculated
        """
        self.temp = None
        self.mixing_ratio = None
        self.pres = None
        self.time = None
        self.resolution = None
        self._sb_CAPE = None  # calculate the first time get_surface_based_CAPE
        # is called

    def get_surface_based_CAPE():
        """ Either calculates (the first call) or retrieves (later calls) the
        value of surface based CAPE.

        :rtype: Quantity
        :return: surface-based CAPE
        """
