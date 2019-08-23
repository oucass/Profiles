from Profile_Set import Profile_Set
from Profile import Profile
import matplotlib.pyplot as plt

"""
Read data. The raw data will be read in any case because ".json" was specified,
but pre-processed data can be read by replacing ".json" with ".nc".

You will be asked for a profile start height. This is the altidute above which
the data should be considered valid and part of a distinct profile. If multiple
profiles are flown in one flight, this profile start height MUST be above the
altitude the craft flies down to at the end of each profile.
   No units are needed, simply enter the appropriate y-value from the chart
of altitude vs. time shown, then hit "enter". You will be asked to confirm the
times that the profile selection algorithm has chosen for the start, peak, and
end of the profile. Simply hit "enter" if the times were correctly identified.
If they were not identified correctly, you will be asked to try again using a
different profile start height.
   Parameters:
       filepath
       vertical resolution desired as an integer
       units for vertical resolution specified
       profile number - this should be 1 unless your file contains multiple
          profiles
       dev should be False IFF (you are processing operational data AND not
                                working on code development)
       ascent - if True, data from the ascending leg of the flight will be
          used. If False, data from the descending leg will be used.
"""

# Example using Profiles
a = Profile_Set()
a.add_all_profiles("/home/jessica/GitHub/data_templates/00000010.JSON")

# Example using Profile (singular)
b = Profile("/home/jessica/GitHub/data_templates/00000010.JSON", 10, 'm', 1,
            dev=True, ascent=True)

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

# Example using Profile
bt = b.get_thermo_profile()

"""
Here's an example of one way to view the processed data. See the docs for a
full list of accessible variables.
"""

# Example using Profiles
plt.figure()
for t in at:
    plt.plot(t.temp, t.alt)
plt.show()

# Example using Profile
plt.figure()
plt.plot(bt.temp, bt.alt)
plt.show()

"""
Now look in your data directory. There are .nc files that can be processed
faster than .json for the same result. Try replacing .json with .nc in lines
31-40 above.
"""
