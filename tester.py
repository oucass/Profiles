from Profile import Profile
from Profile_Set import Profile_Set
import matplotlib.pyplot as plt
import numpy as np
import os

"""
b = Profile("/home/jessica/GitHub/data_templates/"
            + "DL_Data_20190627_to_20190628/00000014.JSON", 10, 'm', 1,
            dev=True, ascent=True)

bw = b.get_wind_profile()

# Example using Profile
bt = b.get_thermo_profile()
bw = b.get_wind_profile()
# Create a hodograph
fig1 = plt.figure()
ax1 = fig1.add_axes([0.1, 0.1, 0.8, 0.8], polar=True, theta_direction=-1,
                    theta_offset=-np.pi/2)
ax1.set_ylim(0, 20)
ax1.set_rticks(np.arange(0, 20, 2.5))
ax1.set_rlabel_position(270)
ax1.tick_params('y', labelrotation=-45, labelsize='x-small')
ax1.yaxis.set_label_coords(-0.15, 0.5)
ax1.plot(bw.dir*np.pi/180, bw.speed, lw=2.5)
plt.show()
"""

"""
a = Profile_Set(resolution=10, res_units='m', ascent=True, dev=True,
                confirm_bounds=False, profile_start_height=400)
datadir_a = "/home/jessica/GitHub/data_templates/datadir_a/"
for file_name in os.listdir(datadir_a):
    if ".json" in file_name or ".JSON" in file_name:
        a.add_all_profiles(os.path.join(datadir_a, file_name))

b = Profile_Set(resolution=10, res_units='m', ascent=True, dev=True,
                confirm_bounds=False, profile_start_height=400)
datadir_b = "/home/jessica/GitHub/data_templates/datadir_b/"
for file_name in os.listdir(datadir_b):
    if ".json" in file_name or ".JSON" in file_name:
        b.add_all_profiles(os.path.join(datadir_b, file_name))

for profile in a.profiles:
    w = profile.get_wind_profile()
for profile in b.profiles:
    w = profile.get_wind_profile()
for profile in a.profiles:
    t = profile.get_thermo_profile()
for profile in b.profiles:
    t = profile.get_thermo_profile()

print(a)
print("\n\n\n")
print(b)
print("\n\n\n\n\n")

plt.figure()
for profile in a.profiles:
    w = profile.get_wind_profile()
    plt.plot(w.speed, w.dir)
for profile in b.profiles:
    w = profile.get_wind_profile()
    plt.plot(w.speed, w.dir)

plt.figure()
for profile in a.profiles:
    t = profile.get_thermo_profile()
    plt.plot(t.temp, t.pres)
for profile in b.profiles:
    t = profile.get_thermo_profile()
    plt.plot(t.temp, t.pres)

a.merge(b)
a.save_netCDF("tester.nc")

print(a)
print("\n\n\n\n\n")
plt.figure()
for profile in a.profiles:
    w = profile.get_wind_profile()
    plt.plot(w.speed, w.dir)


plt.figure()
for profile in a.profiles:
    t = profile.get_thermo_profile()
    plt.plot(t.temp, t.pres)
"""
print("help")
q = Profile_Set()
print("can print")
q.read_netCDF("/home/jessica/GitHub/data_templates/tester.nc")
print("can still print")
plt.figure()
for profile in q.profiles:
    w = profile.get_wind_profile()
    plt.plot(w.speed, w.dir)
for profile in q.profiles:
    w = profile.get_wind_profile()
    plt.plot(w.speed, w.dir)
plt.show()
plt.figure()
for profile in q.profiles:
    t = profile.get_thermo_profile()
    plt.plot(t.temp, t.pres)
for profile in q.profiles:
    t = profile.get_thermo_profile()
    plt.plot(t.temp, t.pres)
plt.show()
