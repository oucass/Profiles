"""
Manages data from a collection of flights or profiles at a specific location

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
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
    :var bool descent: True if
       a) data is to be trimmed to single vertical profiles, and
       b) data from the descending (rather than ascending) leg is to be used.
    :var bool dev: True if data from developmental flights is to be uploaded
    """

    def __init__(self, resolution=10, res_units='m', ascent=True,
                 dev=False, confirm_bounds=True):
        """ Creates a Profiles object.

        :param Quantity resolution: resolution to which data should be
           calculated in units of time, altitude, or pressure
        :param str res_units: units of resolution in a format which can \
           be parsed by pint
        :param bool ascent: True to use ascending leg of flight, False to use \
           descending leg
        :param bool dev: True if data is from a developmental flight
        :param confirm_bounds: False to bypass user confirmation of \
           automatically identified start, peak, and end times
        """
        self.resolution = resolution
        self.res_units = res_units
        self.ascent = ascent
        self.dev = dev
        self.confirm_bounds = confirm_bounds
        self.profiles = []

    def add_all_profiles(self, file_path):
        """ Reads a file, splits it in to several vertical profiles, and adds
        all Profiles to profiles

        :param string file_path: the data file
        """
        # Process altitude data for profile identification
        raw_profile_set = Raw_Profile(file_path, self.dev)
        pos = raw_profile_set.pos_data()

        # Identify the start, peak, and end indices of each profile
        index_list = utils.identify_profile(pos["alt_MSL"].magnitude,
                                            pos["time"], self.confirm_bounds,
                                            to_return=[])

        # Create a Profile object for each profile identified
        for profile_num in np.add(range(len(index_list)), 1):
            self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, profile_num,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list))
        print(len(self.profiles), "profiles including those added from file",
              file_path)

    def add_profile(self, file_path,
                    time=dt.datetime(dt.MINYEAR, 1, 1, tzinfo=None),
                    profile_num=None):
        """ Reads a file and creates a Profile for the first vertical profile
        after time OR for the profile_numth profile.

        :param string file_path: the data file
        :param datetime time: the time after which the profile begins
           (used only if profile_num is not specified)
        :param int profile_num: use the nth profile in the file
        :rtype: bool
        :return: True if a profile was found and added
        """

        # Process altitude data for profile identification
        raw_profile = Raw_Profile(file_path, self.dev)
        pos = raw_profile.pos_data()

        # Identify the start, peak, and end indices of each profile
        index_list = utils.identify_profile(pos["alt_MSL"].magnitude,
                                            pos["time"], self.confirm_bounds,
                                            to_return=[])

        if(profile_num is None):
            self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, profile_num,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list))
        else:
            for profile_num_guess in range(len(index_list)):
                # Check if this profile is the first to start after time
                if (index_list[profile_num_guess][0] >= time):
                    profile_num = profile_num_guess + 1
                    self.profiles.append(Profile(file_path, self.resolution,
                                         self.res_units, profile_num,
                                         self.ascent, self.dev,
                                         self.confirm_bounds,
                                         index_list=index_list))

                # No need to add any more profiles from this file
                break

        print(len(self.profiles), "profiles including profile number ",
              str(profile_num), " added from file", file_path)

    def add_flight(self, file_path):
        """ Reads a file and adds a Profile object, which may not be a vertical
        profile, which contains all data after the sensors stablize. COMING
        SOON

        :param string file_path: the data file
        :rtype: bool
        :return: True if a Profile object was succesfully added
        """

    def merge(self, to_add):
        """ Loads all Profile objects from a pre-existing Profiles into this
        Profiles. All flights must be from the same location. COMING SOON

        :param Profiles to_add: the Profiles object to be merged in
        :rtype: bool
        :return: True if all Profile objects from to_add are successfully
           copied over
        """

    def read_netCDF(self, file_path):
        """ Re-creates a Profiles object which has been saved as a NetCDF
        COMING SOON

        :param string file_path: the NetCDF file
        :rtype: bool
        :return: True if no errors were encountered and all information was
           successfully copied
        """

    def save_netCDF(self, file_path):
        """ Stores all attributes of this Profiles object as a NetCDF COMING
        SOON

        :param string file_path: the file name to which attributes should be
           saved
        :rtype: bool
        :return: True if no issues were encountered
        """

    def make_skewT(self):
        """ Create a Skew-T diagram using all available data. COMING SOON
        (after plotting)

        :rtype: matplotlib.Figure
        :return: the Skew-T diagram
        """
