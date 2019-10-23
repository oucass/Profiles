"""
This version of matplotlib.ticker.EngFormatter was modified by Jessica
Blunt in October 2019. In accordance with the terms of use, the
original copyright is hereby listed as "Copyright (c) 2012-2013
Matplotlib Development Team; All Rights Reserved". The "brief summary
of changes made to matplotlib 3.1.1" is as follows:

* The engineering prefixes were removed
* fmt_engineering was removed
* Check was added to convert Pa to hPa
* Reduction factor was added to make later conversions easier to add
"""
import math
import numpy as np
from matplotlib import rcParams
from matplotlib.ticker import Formatter, ScalarFormatter

class UnitFormatter(Formatter):
    """
    Formats axis values using a specified unit
    """

    def __init__(self, unit="", places=None, sep=" ", *, usetex=None,
                 useMathText=None):
        """
        Parameters
        ----------
        unit : str (default: "")
            Unit symbol to use, suitable for use with single-letter
            representations of powers of 1000. For example, 'Hz' or 'm'.

        places : int (default: None)
            Precision with which to display the number, specified in
            digits after the decimal point (there will be between one
            and three digits before the decimal point). If it is None,
            the formatting falls back to the floating point format '%g',
            which displays up to 6 *significant* digits, i.e. the equivalent
            value for *places* varies between 0 and 5 (inclusive).

        sep : str (default: " ")
            Separator used between the value and the prefix/unit. For
            example, one get '3.14 mV' if ``sep`` is " " (default) and
            '3.14mV' if ``sep`` is "". Besides the default behavior, some
            other useful options may be:

            * ``sep=""`` to append directly the prefix/unit to the value;
            * ``sep="\\N{THIN SPACE}"`` (``U+2009``);
            * ``sep="\\N{NARROW NO-BREAK SPACE}"`` (``U+202F``);
            * ``sep="\\N{NO-BREAK SPACE}"`` (``U+00A0``).

        usetex : bool (default: None)
            To enable/disable the use of TeX's math mode for rendering the
            numbers in the formatter.

        useMathText : bool (default: None)
            To enable/disable the use mathtext for rendering the numbers in
            the formatter.
        """
        self.unit = unit
        self.places = places
        self.sep = sep
        self.set_usetex(usetex)
        self.set_useMathText(useMathText)
        self._reduction_factor = 1

        if unit in "Pa":
            self.unit = "hPa"
            self._reduction_factor = 100
        elif unit in "g Kg$^{-1}$":
            self._reduction_factor = 0.001

    def get_usetex(self):
        return self._usetex


    def set_usetex(self, val):
        if val is None:
            self._usetex = rcParams['text.usetex']
        else:
            self._usetex = val


    usetex = property(fget=get_usetex, fset=set_usetex)

    def get_useMathText(self):
        return self._useMathText


    def set_useMathText(self, val):
        if val is None:
            self._useMathText = rcParams['axes.formatter.use_mathtext']
        else:
            self._useMathText = val


    useMathText = property(fget=get_useMathText, fset=set_useMathText)

    def fix_minus(self, s):
        """
        Replace hyphens with a unicode minus.
        """
        return ScalarFormatter.fix_minus(self, s)


    def __call__(self, x, pos=None):
        x = x / self._reduction_factor
        fmt = "g" if self.places is None else ".{:d}f".format(self.places)
        s = "%s%s" % (format(x, fmt), self.unit)
        # Remove the trailing separator when there is neither prefix nor unit
        if self.sep and s.endswith(self.sep):
            s = s[:-len(self.sep)]
        return self.fix_minus(s)
