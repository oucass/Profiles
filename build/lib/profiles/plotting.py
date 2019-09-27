"""
Plotting contains several functions which display profile
data as stored in uas format.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import os
from metpy.plots import SkewT, Hodograph
import matplotlib.image as mpimg

__all__ = ['contour_height_time', 'meteogram', 'plot_var_time', 'plot_skewT',
           'summary']

# File path to logos added to plots
fpath_logos = os.path.join(os.getcwd(), 'resources', 'CircleLogos.png')


def contour_height_time_helper(profiles, var1):
    """ This creates a filled contour plot of var1 in a time-height
    coordinate system.

    :param list profiles: a list of all profiles to be included in the plot
    :param Var var1: the name of the variable to be contoured
    :raises TypeError: if var1 is not a valid instance of Var
    :rtype: matplotlib.figure.Figure
    :return: the contoured plot
    """

    return


def contour_height_time(profiles, var1='temp', var2=None):
    """ contourHeightTime creates a filled contour plot of var1 in a
    time-height coordinate system. If var2 is not None, it also
    overlays unfilled contours of var2.

    :param list profiles: a list of all profiles to be included in the plot
    :param Var var1: the name of the variable to be filled
    :param Var var2: the name of the variable to be drawn
    :raises TypeError: if var1 is not a valid instance of Var
    :rtype: matplotlib.figure.Figure
    :return: the contoured plot
    """

    fig = contour_height_time_helper(profiles, var1)

    if var2 is not None:
        print('add overlaid contours here')

    return fig


def meteogram(fpath):
    """ Graphically displays Mesonet data.

    Four subplots are created, each with time on the horizontal axis. The top
    plot is of T and Td, the second of P, the third of wind speed and
    direction, and the bottom of solar radiation.

    :param string fpath: the file path for the Mesonet timeseries data
    :rtype: matplotlib.figure.Figure
    :return: figure containing four horizontal subplots
    """

    return


def plot_var_time(var=None, t=None, times=None):
    """ Plots var vs time.

    :param list<list<Quantity>> var: the variables to be plotted
    :param list<datetime> t: times corresponding to the data
    :param tuple<datetime> times: start and end times to highlight
    :rtype: matplotlib.figure.Figure
    :return: plot of var vs. time
    """

    return


def plot_skewT(temp=None, pres=None, t_d=None, u=None, v=None, time=None,
               **kwargs):
    r""" Plots a SkewT diagram.
    :param list<number> temp: Temperatures in C
    :param list<number> pres: Pressures in ?
    :param list<number> t_d: Dewpoint temperatures in C
    :param list<number> u: U-component of wind in kts
    :param list<number> v: V-component of wind in kts
    :param datetime time: The starting time of the flight
    :param \**kwargs: see below

    :Keyword Arguments:
       * *parcel* (``???``) --
         the parcel path (based on lapse rate)
       * *lcl_pres* (``number``) --
         the pressure at the LCL in hPa
       * *lcl_temp* (``number``) --
         the temperature at the LCL in degrees C
       * *surface_based_CAPE* (``number``) --
         the value of surface-based CAPE in J/kg
       * *meso* (``Meso``) --
         information from the ground station
       * *location* (``Location``) --
          information about the mission and location
       * *platform_ID* (``int``) --
          the platform's unique identification number

    :rtype: matplotlib.figure.Figure
    :return: fig containing a SkewT diagram of the data
    """

    # Create plot
    fig = SkewT()

    # Set limits

    return fig


def summary(temp=None, pres=None, t_d=None, u=None, v=None, dt=None,
            loc=(None, None), flight_name=None):
    """ Creates a figure with a SkewT, hodograph, map, and logos. The plot
    title will be <flight_name> at <loc>, <time>. Logos can be
    changed by altering the contents of directory resources.

    :param list<number> temp: Temperatures to plot in C
    :param list<number> pres: Pressures to plot in ?
    :param list<number> t_d: Dewpoints to plot in C
    :param list<number> u: U-component of wind in kts
    :param list<number> v: V-component of wind in kts
    :param datetime dt: start time of flight (for title)
    :param tuple<number> loc: lat, lon pair of location data
    :param string flight_name: name of the flight (for title)
    :rtype: matplotlib.figure.Figure
    :return: the summary figure (described above)
    """

    # Create hodograph
    h = Hodograph()

    # Create SkewT
    s = plot_skewT()

    # Create map

    # Create logos
    logos = mpimg.imread()

    # Draw all

    return h, s, logos  # change to subplots format


def rh_comp_co2(rh):
    """ Plot averaged, QC'd relative humidity against time for sensors inside
       and sensors outside of the CO2 box.

    :param tuple rh: relative humidity as (rh1, rh2, ..., time: ms)
    """
