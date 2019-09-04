#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:58:46 2019

@author: jessica
"""
from Profile_Set import Profile_Set
import matplotlib.pyplot as plt
from metpy.plots import Hodograph
import os

datadir = '/home/jessica/GitHub/data_templates/BIN'
# Example using Profiles
a = Profile_Set(resolution=10, res_units='m', ascent=True, dev=True,
                confirm_bounds=False, profile_start_height=400)
for file_name in os.listdir(datadir):
    a.add_all_profiles(os.path.join(datadir, file_name))


'''
# Example using Profile (singular)
b = Profile("/home/jessica/GitHub/data_templates/00000003.JSON", 10, 'm', 1,
            dev=True, ascent=True)
'''


"""
Calculate thermodynamic variables from raw data. The values returned have
already gone through a quality control process based on variance and bias. If
a Thermo_Profile object was already created from the same ".json" file AND the
same vertical resolution AND the same value of ascent (True/False) was used,
the pre-processed netCDF is read to save time and avoid redundant calculations.
"""

# Example using Profiles
at = []
for p in a.profiles:
    at.append(p.get_thermo_profile())

aw = []
for p in a.profiles:
    aw.append(p.get_wind_profile())

# Example using Profile
# bt = b.get_thermo_profile()

"""
Here's an example of one way to view the processed data. See the docs for a
full list of accessible variables.
"""

# Example using Profiles
plt.figure()
for t in at:
    plt.plot(t.temp, t.alt)
plt.show()

plt.figure()
for w in aw:
    # Create a hodograph
    h = Hodograph(component_range=5)
    h.add_grid(increment=20)
    h.plot(w.u, w.v)
plt.show()

'''
# Example using Profile
plt.figure()
plt.plot(bt.temp, bt.alt)
plt.show()
'''
"""
Now look in your data directory. There are .nc files that can be processed
faster than .json for the same result. Try replacing .json with .nc in lines
31-40 above.
"""
