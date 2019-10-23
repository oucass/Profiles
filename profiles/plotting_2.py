import os
import sys
import pandas as pd
from datetime import datetime as dt
from metpy.plots import SkewT, Hodograph
import cmocean
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as datenum
import matplotlib.ticker as ticker
import matplotlib.lines as mlines
from scipy.interpolate import interp1d
from profiles.UnitFormatter import UnitFormatter


vars = {'theta': ["Potential Temperature", 'theta', 'K', cmocean.cm.thermal,
                  1.0],
        'temp': ["Temperature", 'temp', '$^\circ$C', cmocean.cm.thermal, 1.0],
        'T_d': ["Dewpoint Temperature", 'T_d', '$^\circ$C', cmocean.cm.haline,
                1.0],
        'dewp': ["Dewpoint Temperature", 'T_d', '$^\circ$C', cmocean.cm.haline,
                 1.0],
        'r': ["Mixing Ratio", 'mixing_ratio', 'g Kg$^{-1}$', cmocean.cm.haline,
              0.5],
        'mr': ["Mixing Ratio", 'mixing_ratio', 'g Kg$^{-1}$', cmocean.cm.haline,
               0.5],
        'q': ["Specific Humidity", 'q', 'g Kg$^{-1}$', cmocean.cm.haline, 0.5],
        'rh': ["Relative Humidity", 'rh', '%', cmocean.cm.haline, 5.0],
        'ws': ["Wind Speed", 'speed', 'm s$^{-1}$', cmocean.cm.speed, 5.0],
        'u': ["U", 'u', 'm s$^{-1}$', cmocean.cm.speed, 5.0],
        'v': ["V", 'v', 'm s$^{-1}$', cmocean.cm.speed, 5.0],
        'dir': ["Wind Direction", 'dir', '$^\circ$', cmocean.cm.phase, 360.,
                'wind'],
        'pres': ["Pressure", 'pres', 'Pa', cmocean.cm.haline, 15.0],
        'p': ["Pressure", 'pres', 'Pa', cmocean.cm.haline, 15.0],
        'alt': ["Altitude", 'alt', 'm', cmocean.cm.haline, 10.0]}


# File path to logos added to plots
fpath_logos = os.path.join(os.getcwd(), 'resources', 'CircleLogos.png')


def contour_height_time(profiles, var=['temp'], use_pres=False):
    """ contourHeightTime creates a filled contour plot of the first element of
     var in a time-height coordinate system. If len(var) > 1, it also
    overlays unfilled contours of the remaining elements.
    Accepted variable names are:
       * 'theta'
       * 'temp'
       * 'T_d'
       * 'dewp'
       * 'r'
       * 'mr'
       * 'q'
       * 'rh'
       * 'ws':
       * 'u'
       * 'v'
       * 'dir'
       * 'pres'
       * 'p'
       * 'alt'

    :param list profiles: a list of all profiles to be included in the plot
    :param list<str> var: names of the variable to be plotted
    :rtype: matplotlib.figure.Figure
    :return: the contoured plot
    """

    legend_handles = []
    for var_i in var:
        if var_i not in vars.keys():
            print(var_i + " was not recognized. Try one of these:\n" +
                  str(vars.keys()))

    times = []  # datenum.date2num(list)
    z = []  # unitless
    data = {}  # also unitless
    data_units = {}
    for var_i in var:
        data[var_i] = []

    linestyles = ['solid', 'dashed', 'dashdot']
    style_ind = 0

    for i in range(len(profiles)):
        # Get data from Profile objects
        times.append(list(profiles[i].gridded_times))
        z.append(profiles[i].get("gridded_base").magnitude)
        for var_i in var:
            data[var_i].append(list(profiles[i].get(var_i).magnitude))
            if var_i not in data_units.keys():
                data_units[var_i] = profiles[i].get(var_i).units

    # Now there are 3 parallel lists for each profile.
    # Force them to share z
    max_len = 0
    which_i = -1
    for i in range(len(z)):
        if len(z[i]) > max_len:
            max_len = len(z[i])
            which_i = i

    z = z[which_i]
    # There is now only one list for z - all profiles have to share

    time_flat = np.array(times[0])
    for p in range(len(times)):
        if p > 0:
            time_flat = np.concatenate((time_flat, times[p]))
    timerange = datenum.drange(np.nanmin(time_flat),
                               np.nanmax(time_flat),
                               (np.nanmax(time_flat)
                                -np.nanmin(time_flat))/100)
    q = (np.nanmax(time_flat)-np.nanmin(time_flat))/100
    for i in range(len(times)):
        diff = max_len - len(times[i])
        for j in range(diff):
            times[i].append(None)
            for var_i in var:
                data[var_i][i].append(np.nan)

    # Convert datetime to datenum
    for p in range(len(times)):
        for i in range(len(times[p])):
            try:
                times[p][i] = datenum.date2num(times[p][i])
            except AttributeError:
                times[p][i] = np.nan

    # Switch to arrays to make indexing easier
    times = np.array(times, dtype=float)
    z = np.array(z)
    if use_pres:
        z *= 0.01
    XX, YY = np.meshgrid(timerange, z)

    # Prepare for interpolation
    data_grid = {}
    fig = None
    for var_i in var:
        data_grid[var_i] = np.full_like(XX, np.nan)
        data[var_i] = np.array(data[var_i])

    # For z in z interp1d with time as x and data as y
    # Force back into one grid
    for var_i in var:
        for i in range(len(z)):
            a = list(np.array(times[:, i]).ravel())
            j = 0
            while j < len(a):
                if np.isnan((a[j])):
                    a.remove(a[j])
                else:
                    j += 1
            if len(a) < 2:
                continue
            interp_fun = interp1d(np.array(times[:, i]).ravel(), data[var_i][:, i],
                                  fill_value='extrapolate', kind='cubic')
            data_grid[var_i][i, :] = interp_fun(XX[i, :])

        # Set up figure
        if fig is None:
            start = 0
            end = -1
            for r in range(len(data_grid[var_i])):
                if not np.isnan(data_grid[var_i][r][0]):
                    start = r
                    break
            for r in range(len(data_grid[var_i])):
                if r > start and np.isnan(data_grid[var_i][r][0]):
                    end = r
                    break
            fig, ax = plt.subplots(1, figsize=(16, 9))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            ax.xaxis.set_major_formatter(datenum.DateFormatter('%H:%M:%S'))
            plt.ylim((z[start], z[end]))
            if use_pres:
                plt.ylabel("Pressure (hPa)", fontsize=15)
            else:
                plt.ylabel("Altitude (m MSL)", fontsize=15)
            plt.xlabel("Time (UTC)", fontsize=15)
            ax.tick_params(labelsize=14)

            # Make filled contour plot
            cfax = ax.pcolormesh(XX[start:end], YY[start:end],
                                 data_grid[var_i][start:end],
                                 cmap=vars[var_i][3])
            cbar = plt.colorbar(cfax, ax=ax, pad=0.01, )
            cbar.set_label(vars[var_i][0] + " (" + str(data_units[var_i]) + ")",
                           rotation=270, fontsize=20, labelpad=30)
        else:
            # Make unfilled contour plot
            cfax = ax.contour(XX[start:end], YY[start:end],
                              data_grid[var_i][start:end],
                              np.linspace(np.nanmin(data[var_i]),
                                          np.nanmax(data[var_i]), 10),
                              colors='black', linestyles=linestyles[style_ind])
            legend_handles.append(
                mlines.Line2D([], [], color='black', label=vars[var_i][0],
                              linestyle=linestyles[style_ind], marker='.',
                              markersize=1))
            style_ind += 1
            plt.clabel(cfax, fontsize=12,
                       fmt=UnitFormatter(unit=vars[var_i][2],
                                               places=1))


    for p_times in times:
        ax.scatter(p_times.astype(float), z, c='black', s=0.5)
    legend_handles.append(mlines.Line2D([], [], color='black',
                          label="Data collection points",
                          linestyle='dotted'))
    ax.legend(handles=legend_handles, fontsize=14, framealpha=1.0, loc=4)

    return fig