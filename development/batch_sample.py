#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 12:58:46 2019

@author: jessica
"""
from profiles.Profile_Set import Profile_Set
import matplotlib.pyplot as plt
from metpy.plots import Hodograph
import os
from profiles import plotting

datadir = '/home/jessicablunt/data_templates/CS_N935UA_KAEFS_flights'
MFP = '/home/jessicablunt/Logs/20200710_XXXXN935UA_CS_2.5_flight_log.csv'
MHP = '/home/jessicablunt/Logs/20200710_1500N935UA_CS_2.5_log_header.csv'
# Example using Profiles
a = Profile_Set(resolution=5, res_units='m', ascent=True, dev=True, confirm_bounds=False,
                nc_level="low", profile_start_height=400)

"""
for file_name in os.listdir(datadir):
    if ".BIN" in file_name and "thermo" not in file_name and "wind" not in file_name:
        if "15" in file_name:
            time = "1500"
        elif "16" in file_name:
            time = "1600"
        elif "17" in file_name:
            time = "1800"
        elif "18" in file_name:
            time = "1900"
        single_mfp = MFP.replace("XXXX", time)
        a.add_all_profiles(os.path.join(datadir, file_name), meta_flight_path=single_mfp, meta_header_path=MHP)
"""
a.add_all_profiles(os.path.join(datadir, "20200710_1541.json"), meta_flight_path=MFP.replace("XXXX", "1500"), meta_header_path=MHP)
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

# fig = plotting.contour_height_time(a.profiles,
#                                     var=['theta', 'temp', 'p', 'ws'],
#                                     use_pres=False)
# fig.show()
# plt.figure()
fig2 = plotting.plot_skewT(a.profiles, wind_barbs=True)
plt.show()
plt.savefig("/home/jessicablunt/skewt.png")