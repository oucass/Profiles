"""
Object for location data management.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import numpy as np
import os
from geopy import distance
import pint

units = pint.UnitRegistry()

nextcloudContentsPath = os.path.join(os.path.expanduser("~"), 'Nextcloud',
                                     'Projects', 'contents.txt')


class Location():
    def __init__(self, lat, lon):
        """ Reads contents from ~/Nextcloud/Projects

        :rtype: location.Location
        :return: a filled Location object
        """
        self._site_short = None
        self._site_long = None
        self._elevation = None
        self._in_Oklahoma = None

        # load contents.txt into a dictionary locDic
        locDic = {}
        with open(nextcloudContentsPath) as ff:
            next(ff)
            for line in ff:
                a = line.split('=')
                key = a[0].strip()
                vals = a[1].strip().split(',')
                locDic[key] = vals

        # isolate data used to determine location
        site_shorts = locDic.keys()
        loclats = []
        loclons = []
        for key in site_shorts:
            loclats.append(float(locDic[key][1]))
            loclons.append(float(locDic[key][2]))

        # find closest location
        distances = np.array(
            [distance.vincenty((lat[-1], lon[-1]),
                               (iPos)).km for iPos in zip(loclats, loclons)])

        # isolate attributes for this closest location
        iclosest = distances.argmin()
        self._site_short = site_shorts[iclosest]
        self._site_long = locDic[self._site_short][0]
        self._elevation = float(locDic[self._site_short][3]) * units.meter

        print('Location: {}'.format(self.site_long))
        self._in_Oklahoma = (self.site_short in ['WASH', 'ARRC', 'MRSH'])

    def identifier(self):
        """ Get _site_short

        :rtype: string
        :return: the location's identifier
        """
        return self.site_short

    def site_name(self):
        """ Get _site_long

        :rtype: string
        :return: the name of the flight site
        """
        return self._site_long

    def elevation(self):
        """ get _elevation

        :rtype: number
        :return: height of surface above mean sea level
        """
        return self._elevation

    def in_oklahoma(self):
        """ get _in_oklahoma

        :rtype: bool
        :return: True if site is in Oklahoma, False otherwise
        """
        return self._in_Oklahoma
