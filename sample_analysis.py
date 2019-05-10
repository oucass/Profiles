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
       ascent - if True, data from the ascending leg of the flight will be
          used. If False, data from the descending leg will be used.
"""
a = Profile("/home/jessica/GitHub/data_templates/00000141.json", 10, 'm', 1,
            ascent=True)

"""
Calculate thermodynamic variables from raw data. The values returned have
already gone through a quality control process based on variance and bias. If
a Thermo_Profile object was already created from the same ".json" file AND the
same vertical resolution AND the same value of ascent (True/False) was used,
the pre-processed netCDF is read to save time and avoid redundant calculations.
"""
b = a.get_thermo_profile()

"""
Here's an example of one way to view the processed data. See the docs for a
full list of accessible variables.
"""
plt.plot(b.temp, b.alt)
plt.show()
