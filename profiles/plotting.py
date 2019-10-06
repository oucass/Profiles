"""
Plotting contains several functions which display profile
data as stored in uas format.

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""

import os
from typing import Dict, List

from metpy.plots import SkewT, Hodograph
import matplotlib.image as mpimg
import cmocean
import numpy as np
import matplotlib.pyplot as plt


# File path to logos added to plots
fpath_logos = os.path.join(os.getcwd(), 'resources', 'CircleLogos.png')


def contour_height_time_helper(var_info, data, time, z, fig=None):
    """ This creates a filled contour plot of the specified variable in a time-height
    coordinate system or adds an unfilled contour plot to fig.

    :param list profiles: a list of all profiles to be included in the plot
    :param list var_info: the name, color scheme, label info, etc. of the variable to be contoured
    :rtype: matplotlib.figure.Figure
    :return: the contoured plot
    """

    if fig is None:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        TIME, Z = np.meshgrid(time, z)
        print(TIME.shape)
        print(Z.shape)
        print(data.shape)
        cfax = ax.pcolormesh(TIME, Z, data, cmap=var_info[3])
    #             cfax.set_edgecolor('face')
    #             cax = ax.contour(self.dt_interp, self.z, self.data_interp,
    #                              levels=c_levels, colors='white', zorder=1)
    #             plt.clabel(cax, fontsize=10, inline=1, fmt='%3.1f')
    #             cbar = fig.colorbar(cfax)
    #             cbar.ax.set_ylabel(self.label + ' (' + self.units + ')', fontsize=16)
    #
    #         ax.xaxis.set_major_locator(mpdates.MinuteLocator(byminute=[0, 30]))
    #         ax.xaxis.set_major_formatter(mpdates.DateFormatter('%H:%M'))
    #         ax.tick_params(axis='both', labelsize=14)
    #         plt.xlabel('Time UTC', fontsize=16)
    #         plt.ylabel('Altitude AGL (m)', fontsize=16)
    #         plt.title(self.label + ' ' + self.dt[0].strftime('%d %B %Y') + ' ' +
    #                   self.loc, fontsize=22)
    #         # cbar.ax.set_yticklabels(fontsize=14)
    #         [plt.axvline(t, linestyle='--', color='k') for t in self.t]
    #         [plt.plot(i, j, 'k*') for (i, j) in zip(self.t, self.maxZ)]
    #
    #         fig.tight_layout()
    #         # return fig
    #         return fig

    return fig


def contour_height_time(profiles, var=['temp'], use_pres=False):
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

    vars = {'theta': ["Potential Temperature", None, 'K', cmocean.cm.thermal, 1.0, 'thermo'],  # TODO
            'temp': ["Temperature", 'temp', '$^\circ$C', cmocean.cm.thermal, 1.0, 'thermo'],
            'T_d': ["Dewpoint Temperature", None, '$^\circ$C', cmocean.cm.haline, 1.0, 'thermo'],  # TODO
            'dewp': ["Dewpoint Temperature", None, '$^\circ$C', cmocean.cm.haline, 1.0, 'thermo'],  # TODO
            'r': ["Mixing Ratio", 'mixing_ratio', 'g Kg$^{-1}$', cmocean.cm.haline, 0.5, 'thermo'],
            'mr': ["Mixing Ratio", 'mixing_ratio', 'g Kg$^{-1}$', cmocean.cm.haline, 0.5, 'thermo'],
            'q': ["Specific Humidity", None, 'g Kg$^{-1}$', cmocean.cm.haline, 0.5, 'thermo'],  # TODO
            'rh': ["Relative Humidity", 'rh', '%', cmocean.cm.haline, 5.0, 'thermo'],
            'ws': ["Wind Speed", 'speed', 'm s$^{-1}$', cmocean.cm.speed, 5.0, 'wind'],
            'u': ["U", 'u', 'm s$^{-1}$', cmocean.cm.speed, 5.0, 'wind'],
            'v': ["V", 'v', 'm s$^{-1}$', cmocean.cm.speed, 5.0, 'wind'],
            'dir': ["Wind Direction", 'dir', '$^\circ$', cmocean.cm.phase, 360., 'wind'],
            'pres': ["Pressure", 'pres', None, None, None, 'all'],
            'p': ["Pressure", 'pres', None, None, None, 'all'],
            'alt': ["Altitude", 'alt', None, None, None, 'all']}

    labels = []
    attrs = []
    units = []
    shades = []
    cont_ints = []
    sources = []

    for var_i in var:
        if var_i not in vars.keys():
            print(var_i + " was not recognized. Try one of these:\n" + str(vars.keys()))
        else:
            if vars[var_i][-1] not in sources:
                sources.append(vars[var_i][-1])

    subprofiles = {}

    for source in sources:
        if source not in subprofiles.keys() and source not in 'all':
            subprofiles[source] = []
            for profile in profiles:
                if source in 'wind':
                    subprofiles[source].append(profile.get_wind_profile())
                elif source in 'thermo':
                    subprofiles[source].append(profile.get_thermo_profile())

    for source in sources:
        if source in 'all':
            if 'thermo' in subprofiles.keys():
                source = 'thermo'
            elif 'wind' in subprofiles.keys():
                source = 'wind'
            else:
                subprofiles[source].append(profile.get_thermo_profile())

    # Pull info from Profile objects
    time = []
    z = []
    data = []
    for source_type in subprofiles:
        for subprofile in subprofiles[source_type]:
            if len(time) <= len(data):  # don't double-add time and z when both wind and thermo vars are used
                time.append(subprofile.gridded_times)
                z.append(subprofile.alt)
            for var_i in var:
                if source_type in vars[var_i][-1]:  # get the data from where it belongs
                    data.append(subprofile.__getattribute__(vars[var_i][1]))
    fig = None
    for i in range(len(var)):
        if fig is None:
            fig = contour_height_time_helper(vars[var[i]], data[i], time, z)
        else:
            fig = contour_height_time_helper(vars[var[i]], data[i], time, z, fig=fig)

    return fig

    '''
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

########################################################################################################################
# class plotSkewT():
#     def __init__(self, T=None, pres=None, Td=None, u=None, v=None,
#                  dt_start=None, **kwargs):
#         self.T = T
#         self.pres = pres
#         self.Td = Td
#         self.u = u
#         self.v = v
#         self.dt_start = dt_start
#         argDict = {'parcel': None,
#                    'lclpres': None,
#                    'lcltemp': None,
#                    'SBCAPE': None,
#                    'pmeso': None,
#                    'T2meso': None,
#                    'T9meso': None,
#                    'RH2meso': None,
#                    'Td2meso': None,
#                    'umeso': None,
#                    'vmeso': None,
#                    'radmeso': None,
#                    'tmeso': None,
#                    'loc': None,
#                    'copnum': None,
#                    'lat': None,
#                    'lon': None}
#
#         argDict.update(kwargs)
#         self.argDict = argDict
#         self.windkts = np.sqrt(u ** 2 + v ** 2)
#
#         # convert RH to Td if not defined
#         if (self.argDict['Td2meso'] is None) & \
#                 (self.argDict['RH2meso'] is not None):
#             self.argDict['Td2meso'] = np.array(
#                 mcalc.dewpoint_rh(self.argDict['T2meso'] * units.degC,
#                                   self.argDict['RH2meso'] / 100.))
#
#     def plot(self):
#         fig = plt.figure(figsize=(9, 8))
#         gs0 = gridspec.GridSpec(1, 2)
#         gs1 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs0[0],
#                                                wspace=0)
#         gs2 = gridspec.GridSpecFromSubplotSpec(6, 1, subplot_spec=gs0[1],
#                                                wspace=0, hspace=0.4)
#         # fig.subplots_adjust(wspace=0.1, hspace=0.4)
#         skew = SkewT(fig, rotation=20, subplot=gs1[:, :])
#
#         skew.plot(self.pres, self.T, 'r', linewidth=2)
#         skew.plot(self.pres, self.Td, 'g', linewidth=2)
#         skew.plot_barbs(self.pres[0::4], self.u[0::4], self.v[0::4],
#                         x_clip_radius=0.12, y_clip_radius=0.12)
#
#         # if mesonet data exist, plot
#         if self.argDict['pmeso'] is not None:
#             # plot mesonet data
#             p9meso = self.argDict['pmeso'] * (1. - (7. * 9.8) / (
#                 287. * (self.argDict['T2meso'] + 273.15)))
#             skew.plot(self.argDict['pmeso'], self.argDict['T2meso'], 'k*',
#                       linewidth=2, label='Mesonet 2 m T')
#             skew.plot(p9meso, self.argDict['T9meso'], 'r*',
#                       linewidth=2, label='Mesonet 9 m T')
#             skew.plot(self.argDict['pmeso'], self.argDict['Td2meso'], 'g*',
#                       linewidth=2, label='Mesonet 2 m Td')
#             skew.plot_barbs(self.pres[0], self.argDict['umeso'],
#                             self.argDict['vmeso'], barbcolor='r')  # , label='Mesonet 10 m Wind')
#
#         hand, lab = skew.ax.get_legend_handles_labels()
#
#         # if parcel data exist, plot with lcl
#         if self.argDict['lclpres'] is not None:
#             skew.plot(self.argDict['lclpres'],
#                       self.argDict['lcltemp'], 'ko',
#                       markerfacecolor='black')
#             skew.plot(self.pres, self.argDict['parcel'], 'k',
#                       linewidth=2)
#
#         # axis limits
#         # check temperature range - if below 0C, use range -20 to +10
#         # if all above 0C, use range 0 to +30
#         # if straddling 0C, use range -10 to +20
#         if (np.nanmax(self.T) <= 0.):
#             self.xmin = -30.
#             self.xmax = 10.
#         elif (np.nanmin(self.Td) <= 0.) & (np.nanmax(self.T) >= 0.):
#             self.xmin = -10.
#             self.xmax = 30.
#         elif (np.nanmin(self.Td) >= 0.):
#             self.xmin = 0.
#             self.xmax = 40.
#         else:
#             print '>>x axis limits error '
#             self.xmin = -10.
#             self.xmax = 30.
#         # y limits - use LCL as max if higher than profile
#         if (self.argDict['lclpres']) < np.nanmin(self.pres):
#             self.ymin = round((self.argDict['lclpres']), -1) - 10
#         else:
#             self.ymin = round(np.nanmin(self.pres), -1) - 10
#         self.ymax = round(np.nanmax(self.pres), -1) + 10
#
#         skew.ax.set_ylim(self.ymax, self.ymin)
#         skew.ax.set_xlim(self.xmin, self.xmax)
#         skew.ax.set_yticks(np.arange(self.ymin, self.ymax + 10, 10))
#         skew.ax.set_xlabel('Temperature ($^\circ$C)')
#         skew.ax.set_ylabel('Pressure (hPa)')
#         self.titleName = '{0} {1} UTC - {2}'.format(
#             self.argDict['copnum'],
#             self.dt_start.strftime('%d-%b-%Y %H:%M:%S'),
#             self.argDict['loc'])
#         skew.ax.set_title(self.titleName)
#
#         skew.plot_dry_adiabats(linewidth=0.75)
#         skew.plot_moist_adiabats(linewidth=0.75)
#         skew.plot_mixing_lines(linewidth=0.75)
#
#         ## Hodograph
#         ax_hod = fig.add_subplot(gs2[:2, 0])
#         if np.nanmax(self.windkts) > 18.:
#             comprange = 35
#         else:
#             comprange = 20
#
#         h = Hodograph(ax_hod, component_range=comprange)
#         h.add_grid(increment=5)
#         h.plot_colormapped(self.u, self.v, self.pres, cmap=cmocean.cm.deep_r)
#         ax_hod.set_title('Hodograph (kts)')
#         ax_hod.yaxis.set_ticklabels([])
#
#         ## Map
#         if self.argDict['loc'] == 'HAIL':
#             lllat = 55.34
#             urlat = 70.54
#             lat_0 = 65.
#             lon_0 = 24.
#             ax_map = fig.add_subplot(gs2[3:5, 0])
#             m = Basemap(width=1600000, height=900000, projection='lcc',
#                         resolution='l', lat_1=lllat, lat_2=urlat, lat_0=lat_0,
#                         lon_0=lon_0)
#             m.drawcountries()
#             m.shadedrelief()
#             x, y = m(24.555, 65.038)
#             plt.plot(x, y, 'b.')
#
#         elif self.argDict['loc'] in ['K04V', 'CRES', 'MOFF', 'SAGF', 'K1V8']:
#             lllat = 30.
#             urlat = 50.
#             lat_0 = 37.9
#             lon_0 = -105.7
#             ax_map = fig.add_subplot(gs2[3:5, 0])
#             m = Basemap(width=1600000, height=900000, projection='lcc',
#                         resolution='l', lat_1=lllat, lat_2=urlat, lat_0=lat_0,
#                         lon_0=lon_0)
#             m.drawstates()
#             m.shadedrelief()
#             x, y = m(self.argDict['lon'], self.argDict['lat'])
#             plt.plot(x, y, 'b.')
#
#         else:
#             lllat = 33.6
#             urlat = 37.3
#             lat_0 = 35.45
#             lon_0 = -97.5
#             ax_map = fig.add_subplot(gs2[3:5, 0])
#             m = Basemap(width=1600000, height=900000, projection='lcc',
#                         resolution='l', lat_1=lllat, lat_2=urlat, lat_0=lat_0,
#                         lon_0=lon_0)
#             m.drawstates()
#             #	m.drawcounties()
#             m.shadedrelief()
#             x, y = m(self.argDict['lon'], self.argDict['lat'])
#             plt.plot(x, y, 'b.')
#
#         # Data readings
#         ax_data = fig.add_subplot(gs2[2, 0])
#         plt.axis('off')
#         datastr = ('LCL: %.0f hPa, %.0f$^\circ$C\n' + \
#                    'Parcel Buoyancy: %.0f J kg$^{-1}$\n' + \
#                    # '0-%.0f m bulk shear: %.0f kts\n' + \
#                    '10 m T: %.0f$^\circ$C, Td: %.0f$^\circ$C') % \
#                   (self.argDict['lclpres'], self.argDict['lcltemp'],
#                    self.argDict['SBCAPE'].magnitude,
#                    # sampleHeights_m[-3], bulkshear,
#                    self.T[0], self.Td[0])
#         boxprops = dict(boxstyle='round', facecolor='none')
#         ax_data.text(0.5, 0.95, datastr, transform=ax_data.transAxes,
#                      fontsize=14,
#                      va='top', ha='center', bbox=boxprops)
#         # Legend for mesonet data
#         if self.argDict['loc'] not in ['K04V', 'CRES', 'MOFF', 'SAGF', 'K1V8']:
#             ax_data.legend(hand, lab, loc='upper center', \
#                            bbox_to_anchor=(0.5, 0.15), ncol=2, frameon=False)
#
#         ## Logos
#         ax_png = fig.add_subplot(gs2[5, 0])
#         img = mpimg.imread(fpath_logos, format='png')
#         plt.axis('off')
#         plt.imshow(img, aspect='equal')
#
#         fig.tight_layout()
#         return fig
#
#
# class plotTimeHeight():
#     def __init__(self, t=None, z=None, z2d=None, data=None, label=None,
#                  loc=None, **kwargs):
#         '''
#         t: 1d array of flight times
#         z: 1d array of max alt range
#         z2d: 2d array of altitudes for each flight
#         data: 2d array of any paramater to be plotted
#         label: data name string
#         loc: location where data collected
#         kwargs: data_cont: additional data to overlay with contour
#                 data_cont_label: name of contoured data
#         '''
#         self.t = t
#         self.z = z
#         self.z2d = z2d
#         self.data = data
#         self.label = label
#         self.loc = loc
#         argDict = {'data_cont': None,
#                    'data_cont_label': None,
#                    't_cont': None,
#                    'z_cont': None,
#                    'z2d_cont': None
#                    }
#
#         argDict.update(kwargs)
#         self.argDict = argDict
#         labelDict = {
#             'Potential Temperature': ['K', cmocean.cm.thermal, 1.0],
#             'Temperature': ['$^\circ$C', cmocean.cm.thermal, 1.0],
#             'Dewpoint Temperature': ['$^\circ$C', cmocean.cm.haline, 1.0],
#             'Mixing Ratio': ['g Kg$^{-1}$', cmocean.cm.haline, 0.5],
#             'Specific Humidity': ['g Kg$^{-1}$', cmocean.cm.haline, 0.5],
#             'Relative Humidity': ['%', cmocean.cm.haline, 5.0],
#             'Wind Speed': ['m s$^{-1}$', gist_stern_r, 5.0],
#             'Sensible Heat Flux': ['W m$^{-2}$', cmocean.cm.balance, 50.0],
#             'Latent Heat Flux': ['W m$^{-2}$', cmocean.cm.balance, 50.0],
#             'Wind Direction': ['$^\circ$', cmocean.cm.phase, 360.]
#         }
#         self.units = labelDict[self.label][0]
#         self.shade = labelDict[self.label][1]
#         self.contint = labelDict[self.label][2]
#         if self.argDict['data_cont'] is not None:
#             self.extraContour = True
#             self.units_extra = labelDict[self.argDict['data_cont_label']][0]
#         else:
#             self.extraContour = False
#             self.units_extra = ''
#
#         # interpolate new t
#         self.dt = [mpdates.num2date(i) for i in self.t]
#         self.dt_interp = mpdates.drange(self.dt[0], self.dt[-1],
#                                         timedelta(seconds=60.))
#
#         # interpolate t_cont
#         if self.extraContour:
#             self.dt_ex = [mpdates.num2date(i) for i in self.argDict['t_cont']]
#             self.dt_ex_int = mpdates.drange(self.dt_ex[0], self.dt_ex[-1],
#                                             timedelta(seconds=60.))
#
#         # maximum altitude
#         maxZ = []
#         for i in range(len(self.t)):
#             maxZ.append(np.nanmax(self.z2d[:, i]))
#         self.maxZ = np.array(maxZ)
#
#         # max altitude extra
#         if self.extraContour:
#             maxZex = []
#             for i in range(len(self.argDict['t_cont'])):
#                 maxZex.append(np.nanmax(self.argDict['z2d_cont'][:, i]))
#             self.maxZex = np.array(maxZex)
#
#     def interpTime(self):
#         '''
#         To preserve data from higher altitudes, do custom interpolation:
#         At each level, create arrays data that are not nans and are spaced less
#         than 20 minutes apart
#         Interpolate that array in t
#         Insert back into
#         '''
#         data_interp = np.full((len(self.z), len(self.dt_interp)), np.nan)
#         for i in np.arange(len(self.z)):
#             f = interp1d(self.t, self.data[i, :])
#             fnew = f(self.dt_interp)
#             data_interp[i, :] = fnew
#
#         self.data_interp = ma.masked_invalid(data_interp)
#         # mask negative wind speeds
#         if self.label == 'Wind Speed':
#             self.data_interp = ma.masked_where(self.data_interp < 0.,
#                                                self.data_interp)
#
#         # Interpolate contours
#         if self.extraContour:
#             data_interp_ex = np.full((len(self.argDict['z_cont']), len(
#                 self.dt_ex_int)), np.nan)
#             for i in np.arange(len(self.argDict['z_cont'])):
#                 f_ex = interp1d(self.argDict['t_cont'],
#                                 self.argDict['data_cont'][i, :])
#                 fnew_ex = f_ex(self.dt_ex_int)
#                 data_interp_ex[i, :] = fnew_ex
#
#             self.data_interp_ex = ma.masked_invalid(data_interp_ex)
#
#     def plot(self):
#         self.interpTime()
#         c_levels = np.arange(np.floor(np.nanmin(self.data_interp)),
#                              np.ceil(np.nanmax(self.data_interp)) + 1.0, self.contint)
#
#         fig, ax = plt.subplots(1, figsize=(16, 9))
#         plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
#         if self.extraContour:
#             vmax = max([abs(np.nanmin(self.data_interp_ex)),
#                         np.nanmax(self.data_interp_ex)])
#             vmax = round(vmax, 0)
#
#             cfax = ax.pcolormesh(self.dt_ex_int, self.argDict['z_cont'],
#                                  self.data_interp_ex, cmap=cmocean.cm.balance,
#                                  vmin=-vmax, vmax=vmax)
#             cfax.set_edgecolor('face')
#             cax = ax.contour(self.dt_interp, self.z, self.data_interp,
#                              levels=c_levels, colors='k')
#             plt.clabel(cax, fontsize=10, inline=1, fmt='%3.1f')
#             cbar = fig.colorbar(cfax)
#             cbar.ax.set_ylabel(self.argDict['data_cont_label'] + \
#                                ' (' + self.units_extra + ')', fontsize=16)
#
#         else:
#             cfax = ax.pcolormesh(self.dt_interp, self.z, self.data_interp,
#                                  cmap=self.shade)
#             cfax.set_edgecolor('face')
#             cax = ax.contour(self.dt_interp, self.z, self.data_interp,
#                              levels=c_levels, colors='white', zorder=1)
#             plt.clabel(cax, fontsize=10, inline=1, fmt='%3.1f')
#             cbar = fig.colorbar(cfax)
#             cbar.ax.set_ylabel(self.label + ' (' + self.units + ')', fontsize=16)
#
#         ax.xaxis.set_major_locator(mpdates.MinuteLocator(byminute=[0, 30]))
#         ax.xaxis.set_major_formatter(mpdates.DateFormatter('%H:%M'))
#         ax.tick_params(axis='both', labelsize=14)
#         plt.xlabel('Time UTC', fontsize=16)
#         plt.ylabel('Altitude AGL (m)', fontsize=16)
#         plt.title(self.label + ' ' + self.dt[0].strftime('%d %B %Y') + ' ' +
#                   self.loc, fontsize=22)
#         # cbar.ax.set_yticklabels(fontsize=14)
#         [plt.axvline(t, linestyle='--', color='k') for t in self.t]
#         [plt.plot(i, j, 'k*') for (i, j) in zip(self.t, self.maxZ)]
#
#         fig.tight_layout()
#         # return fig
#         return fig
#
#
# class meteogram():
#     def __init__(self, fmeso, tstart, tend, tsunrise):
#         mesodata = np.genfromtxt(fmeso, delimiter=',')
#         mesotimes_str = np.genfromtxt(fmeso, delimiter=',',
#                                       dtype=str, usecols=2)
#         self.fname = fmeso.split(os.sep)[-1]
#
#         self.p = (mesodata[:, 9] + 700.)
#         self.RH2m = mesodata[:, 4]
#         self.T2m = mesodata[:, 5]
#         self.u2m = mesodata[:, 15]
#         self.T9m = mesodata[:, 14]
#         self.u10m = mesodata[:, 12]
#         self.dir10m = mesodata[:, 13]
#         self.srad = mesodata[:, 6]
#
#         self.Rd = 287.
#         self.rho = self.p / ((self.T2m + 273.15) * self.Rd)
#         self.Td2m = np.array(mcalc.dewpoint_rh(self.T2m * units.degC,
#                                                self.RH2m / 100.))
#
#         self.mesotimes_dt = [datetime.strptime(t,
#                                                '"%Y-%m-%d %H:%M:%S"') for t in mesotimes_str]
#         self.mesotimes_t = mpdates.date2num(self.mesotimes_dt)
#
#         # self.tstart = tstart
#         # self.tend = tend
#         self.tsunrise = tsunrise
#
#         count = 0
#         for i in self.mesotimes_dt:
#             if (i.hour == int(tstart[0][:2])) & (i.minute == int(tstart[0][2:])):
#                 istart = count
#             elif (i.hour == int(tend[0][:2])) & (i.minute == int(tstart[0][2:])):
#                 iend = count
#             count += 1
#         self.irange = range(istart, iend)
#
#     def plot(self):
#         fig, axarr = plt.subplots(nrows=2, ncols=2, sharex='col',
#                                   figsize=(16, 9))
#         figtitle = '{0:s} Meteogram {1:s}'.format(self.fname.split('.')[1],
#                                                   self.fname.split('.')[0])
#         plt.suptitle(figtitle, fontsize=20)
#
#         # T & Td
#         axarr[0, 0].plot(self.mesotimes_t[self.irange], self.T2m[self.irange],
#                          color=(213./255, 94./255, 0), label='Temperature 2m',
#                          linewidth=2)
#         axarr[0, 0].plot(self.mesotimes_t[self.irange], self.T9m[self.irange],
#                          color=(204./255, 121./255, 167./255), label='Temperature 9m',
#                          linewidth=2)
#         axarr[0, 0].plot(self.mesotimes_t[self.irange], self.Td2m[self.irange],
#                          color=(0, 114./255, 178./255), label='Dewpoint Temperature',
#                          linewidth=2)
#         axarr[0, 0].set_title('Temperature and Dewpoint', fontsize=20)
#         axarr[0, 0].tick_params(labeltop=False, right=True, labelright=True, labelsize=16)
#         axarr[0, 0].set_ylabel('Temperature [$^\circ$C]', fontsize=18)
#         axarr[0, 0].grid(axis='y')
#         axarr[0, 0].legend(loc=0, fontsize=14)
#
#         # p
#         axarr[0, 1].plot(self.mesotimes_t[self.irange], self.p[self.irange], 'k', linewidth=2)
#         axarr[0, 1].set_title('Pressure', fontsize=20)
#         axarr[0, 1].tick_params(labeltop=False, right=True, labelright=True, labelsize=16)
#         axarr[0, 1].set_ylabel('Pressure [hPa]', fontsize=18)
#         axarr[0, 1].grid(axis='y')
#
#         # wind speed and direction
#         axarr_2 = axarr[1, 0].twinx()
#         axarr[1, 0].plot(self.mesotimes_t[self.irange], self.u10m[self.irange],
#                          color=(0, 158./255, 115./255), linewidth=2)
#         axarr_2.plot(self.mesotimes_t[self.irange], self.dir10m[self.irange],
#                      color=(213./255, 94./255, 0), marker='o', markersize=3,
#                      linestyle='')
#         axarr[1, 0].set_title('Wind Speed and Direction', fontsize=20)
#         axarr[1, 0].set_ylabel('Wind Speed [m s$^{-1}$]', color=(0, 158./255, 115./255), fontsize=18)
#         axarr_2.set_ylabel('Wind Direction [$^\circ$]', color=(213./255, 94./255, 0), fontsize=18)
#         axarr_2.set_yticks(range(0, 405, 45))
#         axarr_2.set_yticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
#         axarr_2.tick_params(labelsize=16)
#         axarr[1, 0].grid(axis='y')
#         axarr[1, 0].xaxis.set_major_locator(mpdates.HourLocator(interval=1))
#         axarr[1, 0].xaxis.set_major_formatter(mpdates.DateFormatter('%H'))
#         axarr[1, 0].set_xlabel('Time [UTC]', fontsize=18)
#         axarr[1, 0].tick_params(labelsize=16)
#
#         # solar radiation
#         axarr[1, 1].plot(self.mesotimes_t[self.irange], self.srad[self.irange],
#                          color=(230./255, 159./255, 0), linewidth=2)
#         axarr[1, 1].set_title('Solar Radiation', fontsize=20)
#         axarr[1, 1].set_ylabel('Solar Radiation [W m$^{-2}$]', fontsize=18)
#         axarr[1, 1].xaxis.set_major_locator(mpdates.HourLocator(interval=1))
#         axarr[1, 1].xaxis.set_major_formatter(mpdates.DateFormatter('%H'))
#         axarr[1, 1].set_xlabel('Time [UTC]', fontsize=18)
#         axarr[1, 1].grid(axis='y')
#         axarr[1, 1].tick_params(labeltop=False, right=True, labelright=True, labelsize=16)
#
#         # vertical lines
#         # for i in range(len(axarr)):
#         #     for j in range(len(axarr)):
#         #         axarr[j, i].axvline(self.tstart, color='k', linestyle='--')
#         #         axarr[j, i].axvline(self.tend, color='k', linestyle='--')
#         #         axarr[j, i].axvline(self.tsunrise, color='r', linestyle='-')
#
#        return fig, axarr