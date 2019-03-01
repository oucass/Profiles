"""
Corrects and stores CO2 parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import pint

units = pint.UnitRegistry()


class CO2_Profile():
    """ Contains data from one file.

    :var list<Quantity> co2: CO2 in ppm
    :var list<Datetime> time: time of each point
    """

    def __init__(self, co2_raw, temp_raw, rh_raw, resolution):
        """ Creates CO2_Profile object based on CO2, temperature, and humidity
        data at the specified resolution.
        """

        self.co2 = None
        self.time = None

    def _adjust_for_temp_rh(co2_raw, temp_raw, rh_raw, time):
        """ Corrects CO2 reported by PIXHAWK using temperature and RH inside
        and outside of the sensor.
        """
