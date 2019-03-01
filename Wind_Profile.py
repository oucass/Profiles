"""
Calculates and stores wind parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import pint

units = pint.UnitRegistry()


class Wind_Profile():
    """ Contains data from one file.

    :var list<Quantity> u: U component of wind
    :var list<Quantity> v: V-component of wind
    :var list<Datetime> time: time of each point
    """

    def __init__(self, rotation, resolution):
        """ Creates Wind_Profile object based on rotation data at the specified
        resolution.
        """
        self.u = None
        self.v = None
        self.time = None

    def _calc_winds(TBD):
        """ Math-y stuff in wind calculations that I don't understand
        """
