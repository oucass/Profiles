from Profile import Profile
import matplotlib.pyplot as plt
import numpy as np

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
