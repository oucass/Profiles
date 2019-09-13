"""
Manages data from a collection of flights or profiles at a specific location

Authors Brian Greene, Jessica Blunt, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019

Component of Profiles v1.0.0
"""
import utils
import datetime as dt
import numpy as np
from Profile import Profile
from Raw_Profile import Raw_Profile


class Profile_Set():
    """ This class manages data (in the form of Profile objects) from one or
    many flights.

    :var Location location: information about the location of the flights
    :var list<Profile> profiles: list of Profile objects at this location
    :var bool ascent: True if data from the ascending leg of the profile is \
       to be used. If False, the descending leg will be processed instead
    :var bool dev: True if data from developmental flights is to be uploaded
    :var int resolution: the vertical resolution desired
    :var str res_units: the units in which the vertical resolution is given
    :var bool confirm_bounds: if True, the user will be asked to verify the \
       automatically-determined start, peak, and end times of each profile
    :var int profile_start_height: either passed to the constructor or \
       provided by the user during processing
    """

    def __init__(self, resolution=10, res_units='m', ascent=True,
                 dev=False, confirm_bounds=True, profile_start_height=None):
        """ Creates a Profiles object.

        :param int resolution: resolution to which data should be
           calculated in units of altitude or pressure
        :param str res_units: units of resolution in a format which can \
           be parsed by pint
        :param bool ascent: True to use ascending leg of flight, False to use \
           descending leg
        :param bool dev: True if data is from a developmental flight
        :param confirm_bounds: False to bypass user confirmation of \
           automatically identified start, peak, and end times
        :param int profile_start_height: if provided, the user will not be \
           prompted to enter the starting height for each profile separately.\
           This can be usefull when processing many profiles from the same \
           mission, but at least one profile should be processed without this \
           parameter to determine its correct value.
        """
        self.resolution = resolution
        self.res_units = res_units
        self.ascent = ascent
        self.dev = dev
        self.confirm_bounds = confirm_bounds
        self.profiles = []
        self.profile_start_height = profile_start_height

    def add_all_profiles(self, file_path, scoop_id=None):
        """ Reads a file, splits it in to several vertical profiles, and adds
        all Profiles to profiles

        :param str file_path: the data file
        :param str scoop_id: the identifier of the sensor package used
        """
        # Process altitude data for profile identification
        raw_profile_set = Raw_Profile(file_path, self.dev, scoop_id)
        pos = raw_profile_set.pos_data()

        # Identify the start, peak, and end indices of each profile
        index_list = utils.identify_profile(pos["alt_MSL"].magnitude,
                                            pos["time"], self.confirm_bounds,
                                            to_return=[],
                                            profile_start_height=self
                                            .profile_start_height)

        # Create a Profile object for each profile identified
        for profile_num in np.add(range(len(index_list)), 1):
            self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, profile_num,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list,
                                         raw_profile=raw_profile_set,
                                         profile_start_height=self
                                         .profile_start_height))
        print(len(self.profiles), "profile(s) including those added from file",
              file_path)

    def add_profile(self, file_path,
                    time=dt.datetime(dt.MINYEAR, 1, 1, tzinfo=None),
                    profile_num=None, scoop_id=None):
        """ Reads a file and creates a Profile for the first vertical profile
        after time OR for the profile_numth profile.

        :param string file_path: the data file
        :param datetime time: the time after which the profile begins
           (used only if profile_num is not specified)
        :param int profile_num: use the nth profile in the file
        :param str scoop_id: the identifier of the sensor package used
        """

        # Process altitude data for profile identification
        raw_profile = Raw_Profile(file_path, self.dev, scoop_id)
        pos = raw_profile.pos_data()

        # Identify the start, peak, and end indices of each profile
        index_list = utils.identify_profile(pos["alt_MSL"].magnitude,
                                            pos["time"], self.confirm_bounds,
                                            to_return=[])

        if(profile_num is None):
            self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, 1,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list,
                                         raw_profile=raw_profile,
                                         profile_start_height=self
                                         .profile_start_height))
        else:
            for profile_num_guess in range(len(index_list)):
                # Check if this profile is the first to start after time
                if (index_list[profile_num_guess][0] >= time):
                    profile_num = profile_num_guess + 1
                    self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, profile_num,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list,
                                         raw_profile=raw_profile,
                                         profile_start_height=self
                                         .profile_start_height))

                # No need to add any more profiles from this file
                break

        print(len(self.profiles), "profiles including profile number ",
              str(profile_num), " added from file", file_path)

    def merge(self, to_add):
        """ Loads all Profile objects from a pre-existing Profiles into this
        Profiles. All flights must be from the same location.

        :param Profiles to_add: the Profiles object to be merged in
        """

        if to_add.resolution != self.resolution or \
           to_add.res_units != self.res_units:
            print("NOTICE: All future Profiles added will have resolution "
                  + str(self.resolution*self.res_units))

        if to_add.ascent != self.ascent:
            if self.ascent:
                print("NOTICE: All future Profiles added will be treated as \
                      ascending")
            else:
                print("NOTICE: All future Profiles added will be treated as \
                      descending")

        if to_add.profile_start_height != self.profile_start_height:
            print("NOTICE: All future Profiles added will start at height "
                  + str(self.profile_start_height))

        if to_add.dev != self.dev:
            if self.dev:
                print("NOTICE: All future Profiles added will be considered \
                      developmental")
            else:
                print("NOTICE: All future Profiles added will be considered \
                      operational")

        if len(self.profiles) > 0:
            units = self.profiles[0]._units

        for new_profile in to_add.profiles:

            new_profile._pos["alt_MSL"] = new_profile._pos["alt_MSL"]\
                .to_base_units().magnitude * units.m
            new_profile._pos["units"] = units
            if new_profile.resolution.to_base_units().units == \
               new_profile._units.m:
                new_profile.resolution = \
                   new_profile.resolution.to_base_units().magnitude \
                   * units.m

            else:
                new_profile.resolution = \
                   new_profile.resolution.to_base_units().magnitude \
                   * units.N / units.m / units.m

            new_profile.gridded_base = new_profile.gridded_base\
                .to_base_units().magnitude * new_profile.resolution.units

            if new_profile._wind_profile is not None:
                new_w = new_profile._wind_profile
                new_w.u = new_w.u.to_base_units().magnitude \
                    * units.m / units.s
                new_w.v = new_w.v.to_base_units().magnitude \
                    * units.m / units.s
                new_w.dir = new_w.dir.to(new_w._units.deg)\
                    .magnitude * units.deg
                new_w.speed = new_w.speed.to_base_units()\
                    .magnitude * units.m / units.s
                new_w.pres = new_w.pres.to_base_units().magnitude \
                    * units.N / units.m / units.m
                new_w.alt = new_w.alt.to_base_units().magnitude \
                    * units.m
                new_w.resolution = new_profile.resolution
                new_w._units = units
                new_profile._wind_profile = new_w

            if new_profile._thermo_profile is not None:
                new_t = new_profile._thermo_profile
                new_t.resolution = new_profile.resolution
                new_t.rh = new_t.rh.magnitude * units.percent
                new_t.pres = new_t.pres.magnitude * units.N / units.m / units.m
                new_t.temp = new_t.temp.to_base_units().magnitude \
                    * units.kelvin
                new_t.alt = new_w.alt.to_base_units().magnitude \
                    * units.m
                new_t._units = units
                new_profile._thermo_profile = new_t

            new_profile._units = units

            self.profiles.append(new_profile)

    def read_netCDF(self, file_path):
        """ Re-creates a Profiles object which has been saved as a NetCDF
        COMING SOON

        :param string file_path: the NetCDF file
        """

    def save_netCDF(self, file_path):
        """ Stores all attributes of this Profiles object as a NetCDF COMING
        SOON

        :param string file_path: the file name to which attributes should be
           saved
        """

    def __str__(self):
        to_return = "=====================================================\n" \
                    + "Profile Set with " + str(len(self.profiles)) + \
                    " Profiles\n"
        for profile in self.profiles:
            to_return = to_return + "\t" + str(profile) + "\n"
        return to_return
