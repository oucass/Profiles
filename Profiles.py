"""
Manages data from a collection of flights or profiles at a specific location

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
import datetime as dt


class Profiles():
    """ This class manages data (in the form of Profile objects) from one or
    many flights.

    :var Location location: information about the location of the flights
    :var list<Profile> profiles: list of Profile objects at this location
    :var bool descent: True if
       a) data is to be trimmed to single vertical profiles, and
       b) data from the descending (rather than ascending) leg is to be used.
    :var bool dev: True if data from developmental flights is to be uploaded
    """

    def __init__(self, descent=False, dev=False):
        """ Creates a Profiles object.

        :param bool descent: True if
           a) data is to be trimmed to single vertical profiles, and
           b) data from the descending (rather than ascending) leg is to be
           used.
        :param bool dev: True if data from developmental flights is to be
           uploaded
        """

    def add_all_profiles(self, file_path):
        """ Reads a file, splits it in to several vertical profiles, and adds
        all Profiles to profiles

        :param string file_path: the data file
        """

    def add_profile(self, file_path, time=dt.datetime(dt.MINYEAR, 1, 1,
                                                      tzinfo=None)):
        """ Reads a file and creates a Profile for the first vertical profile
        after time.

        :param string file_path: the data file
        :param datetime time: the time after which the profile begins
        :rtype: bool
        :return: True if a profile was found and added
        """

    def add_flight(self, file_path):
        """ Reads a file and adds a Profile object, which may not be a vertical
        profile, which contains all data after the sensors stablize.

        :param string file_path: the data file
        :rtype: bool
        :return: True if a Profile object was succesfully added
        """

    def merge(self, to_add):
        """ Loads all Profile objects from a pre-existing Profiles into this
        Profiles. All flights must be from the same location.

        :param Profiles to_add: the Profiles object to be merged in
        :rtype: bool
        :return: True if all Profile objects from to_add are successfully
           copied over
        """

    def read_netCDF(self, file_path):
        """ Re-creates a Profiles object which has been saved as a NetCDF

        :param string file_path: the NetCDF file
        :rtype: bool
        :return: True if no errors were encountered and all information was
           successfully copied
        """

    def save_netCDF(self, file_path):
        """ Stores all attributes of this Profiles object as a NetCDF

        :param string file_path: the file name to which attributes should be
           saved
        :rtype: bool
        :return: True if no issues were encountered
        """

    def make_skewT(self):
        """ Create a Skew-T diagram using all available data.

        :rtype: matplotlib.Figure
        :return: the Skew-T diagram
        """
