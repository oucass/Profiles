"""
Manages data from a collection of flights or profiles at a specific location

Authors Brian Greene, Jessica Blunt, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019

Component of Profiles v1.0.0
"""
import os
import utils
import netCDF4
import datetime as dt
import numpy as np
from Profile import Profile
from Raw_Profile import Raw_Profile
from Thermo_Profile import Thermo_Profile


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
                 dev=False, confirm_bounds=True, profile_start_height=None,
                 nc_level='none'):
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
        :param str nc_level: either 'low', or 'none'. This parameter \
           is used when processing non-NetCDF files to determine which types \
           of NetCDF files will be generated. For individual files for each \
           Raw, Thermo, \
           and Wind Profile, specify 'low'. For no NetCDF files, specify \
           'none'. To generate a single, Profile_Set-level file, call \
           Profile_Set.save_netCDF where you are done adding data.
        """
        self.resolution = resolution
        self.res_units = res_units
        self.ascent = ascent
        self.dev = dev
        self.confirm_bounds = confirm_bounds
        self.profiles = []
        self.profile_start_height = profile_start_height
        self._nc_level = nc_level
        self.root_dir = ""

    def add_all_profiles(self, file_path, scoop_id=None):
        """ Reads a file, splits it in to several vertical profiles, and adds
        all Profiles to profiles

        :param str file_path: the data file
        :param str scoop_id: the identifier of the sensor package used
        """
        file_dir = os.path.dirname(file_path)
        if(self.root_dir is ""):
            self.root_dir = file_dir
        else:
            match_up_to = -1
            for i in range(len(self.root_dir)):
                if i < len(file_dir):
                    if self.root_dir[i] == file_dir[i]:
                        match_up_to = i
                    else:
                        print(self.root_dir[i], file_dir[i])
                        break
                else:
                    print(self.root_dir[:i-1], file_dir[:i-1])
                    break
            self.root_dir = self.root_dir[:match_up_to+1]
            self.root_dir = self.root_dir[:self.root_dir.rindex("/")+1]

        # Process altitude data for profile identification
        raw_profile_set = Raw_Profile(file_path, self.dev, scoop_id,
                                      nc_level=self._nc_level)
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
                                         .profile_start_height,
                                         nc_level=self._nc_level))
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

        file_dir = os.path.dirname(file_path)
        if(self.root_dir is ""):
            self.root_dir = file_dir
        else:
            match_up_to = -1
            for i in range(len(self.root_dir)):
                if i < len(file_dir):
                    if self.root_dir[i] == file_dir[i]:
                        match_up_to = i
                    else:
                        print(self.root_dir[i], file_dir[i])
                        break
                else:
                    print(self.root_dir[:i-1], file_dir[:i-1])
                    break
            self.root_dir = os.path.dirname(self.root_dir[0:match_up_to+1])

        # Process altitude data for profile identification
        raw_profile = Raw_Profile(file_path, self.dev, scoop_id,
                                  nc_level=self._nc_level)
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
                                         .profile_start_height,
                                         nc_level=self._nc_level))
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
                                         .profile_start_height,
                                         nc_level=self._nc_level))

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
        """ Re-creates a Profile_Set object which has been saved as a NetCDF

        :param string file_path: the NetCDF file
        """

        main_file = netCDF4.Dataset(file_path, "r", format="NETCDF4",
                                    mmap=False)
        self.dev = bool(main_file.dev)

        for profile_name in main_file.groups:
            profile_group = main_file.groups[profile_name]
            raw_group = profile_group.groups["Raw_Profile"]
            wind_group = profile_group.groups["Wind_Profile"]
            thermo_group = profile_group.groups["Thermo_Profile"]

            self.profiles.append(Profile())  # This circumvents the real
            # constructor - we are now responsible for ALL instance
            # variables here.

            #
            # Raw
            #
            


    def save_netCDF(self, file_path):
        """ Stores all attributes of this Profile_Set object as a NetCDF

        :param string file_path: the file name to which attributes should be
           saved
        """
        main_file = netCDF4.Dataset(os.path.join(self.root_dir, file_path),
                                    "w", format="NETCDF4", mmap=False)

        for i in range(len(self.profiles)):
            profile_group = main_file.createGroup("Profile" + str(i))
            raw_group = profile_group.createGroup("Raw_Profile")
            wind_group = profile_group.createGroup("Wind_Profile")
            thermo_group = profile_group.createGroup("Thermo_Profile")

            #
            # Raw
            #

            raw = self.profiles[i]._raw_profile

            # TEMP
            temp_grp = raw_group.createGroup("/temp")
            temp_grp.createDimension("temp_time", None)
            # temp_grp.base_time = date2num(raw.temp[-1][0])
            temp_sensor_numbers = np.add(range(int((len(raw.temp)-1)/2)), 1)
            for num in temp_sensor_numbers:
                new_var = temp_grp.createVariable("volt" + str(num), "f8",
                                                  ("temp_time",))
                try:
                    new_var[:] = raw.temp[2*num-2].magnitude
                except AttributeError:
                    # This sensor didn't report
                    continue
                new_var.units = "mV"
            new_var = temp_grp.createVariable("time", "f8", ("temp_time",))
            new_var[:] = netCDF4.date2num(raw.temp[-1],
                                          units="microseconds since \
                                          2010-01-01 00:00:00:00")
            new_var.units = "microseconds since 2010-01-01 00:00:00:00"

            # RH
            rh_grp = raw_group.createGroup("/rh")
            rh_grp.createDimension("rh_time", None)
            rh_sensor_numbers = np.add(range(int((len(raw.rh)-1)/2)), 1)
            for num in rh_sensor_numbers:
                new_rh = rh_grp.createVariable("rh" + str(num),
                                               "f8", ("rh_time", ))
                new_temp = rh_grp.createVariable("temp" + str(num),
                                                 "f8", ("rh_time", ))
                new_rh[:] = raw.rh[2*num-2].magnitude
                new_temp[:] = raw.rh[2*num-1].magnitude
                new_rh.units = "%"
                new_temp.units = "F"
            new_var = rh_grp.createVariable("time", "i8", ("rh_time",))
            new_var[:] = netCDF4.date2num(raw.rh[-1],
                                          units="microseconds since \
                                          2010-01-01 00:00:00:00")
            new_var.units = "microseconds since 2010-01-01 00:00:00:00"

            # POS
            pos_grp = raw_group.createGroup("/pos")
            pos_grp.createDimension("pos_time", None)
            lat = pos_grp.createVariable("lat", "f8", ("pos_time", ))
            lng = pos_grp.createVariable("lng", "f8", ("pos_time", ))
            alt = pos_grp.createVariable("alt", "f8", ("pos_time", ))
            alt_rel_home = pos_grp.createVariable("alt_rel_home", "f8",
                                                  ("pos_time", ))
            alt_rel_orig = pos_grp.createVariable("alt_rel_orig", "f8",
                                                  ("pos_time", ))
            time = pos_grp.createVariable("time", "i8", ("pos_time",))

            lat[:] = raw.pos[0].magnitude
            lng[:] = raw.pos[1].magnitude
            alt[:] = raw.pos[2].magnitude
            alt_rel_home[:] = raw.pos[3].magnitude
            alt_rel_orig[:] = raw.pos[4].magnitude
            time[:] = netCDF4.date2num(raw.pos[-1], units="microseconds \
                since 2010-01-01 00:00:00:00")

            lat.units = "deg"
            lng.units = "deg"
            alt.units = "m MSL"
            alt_rel_home.units = "m"
            alt_rel_orig.units = "m"
            time.units = "microseconds since 2010-01-01 00:00:00:00"

            # PRES
            pres_grp = raw_group.createGroup("/pres")
            pres_grp.createDimension("pres_time", None)
            pres = pres_grp.createVariable("pres", "f8", ("pres_time", ))
            temp = pres_grp.createVariable("temp", "f8", ("pres_time", ))
            temp_gnd = pres_grp.createVariable("temp_ground", "f8",
                                               ("pres_time", ))
            alt = pres_grp.createVariable("alt", "f8", ("pres_time", ))
            time = pres_grp.createVariable("time", "i8", ("pres_time", ))

            pres[:] = raw.pres[0].magnitude
            temp[:] = raw.pres[1].magnitude
            temp_gnd[:] = raw.pres[2].magnitude
            alt[:] = raw.pres[3].magnitude
            time[:] = netCDF4.date2num(raw.pres[-1], units="microseconds \
                since 2010-01-01 00:00:00:00")

            pres.units = "Pa"
            temp.units = "F"
            temp_gnd.units = "F"
            alt.units = "m (MSL)"
            time.units = "microseconds since 2010-01-01 00:00:00:00"

            # ROTATION
            rot_grp = raw_group.createGroup("/rotation")
            rot_grp.createDimension("rot_time", None)
            ve = rot_grp.createVariable("VE", "f8", ("rot_time", ))
            vn = rot_grp.createVariable("VN", "f8", ("rot_time", ))
            vd = rot_grp.createVariable("VD", "f8", ("rot_time", ))
            roll = rot_grp.createVariable("roll", "f8", ("rot_time", ))
            pitch = rot_grp.createVariable("pitch", "f8", ("rot_time", ))
            yaw = rot_grp.createVariable("yaw", "f8", ("rot_time", ))
            time = rot_grp.createVariable("time", "i8", ("rot_time", ))

            ve[:] = raw.rotation[0].magnitude
            vn[:] = raw.rotation[1].magnitude
            vd[:] = raw.rotation[2].magnitude
            roll[:] = raw.rotation[3].magnitude
            pitch[:] = raw.rotation[4].magnitude
            yaw[:] = raw.rotation[5].magnitude
            time[:] = netCDF4.date2num(raw.rotation[-1], units="microseconds \
                                       since 2010-01-01 00:00:00:00")

            ve.units = "m/s"
            vn.units = "m/s"
            vd.units = "m/s"
            roll.units = "deg"
            pitch.units = "deg"
            yaw.units = "deg"
            time.units = "microseconds since 2010-01-01 00:00:00:00"

            raw_group.baro = raw.baro

            #
            # Thermo
            #

            thermo = self.profiles[i].get_thermo_profile()

            thermo_group.createDimension("time", None)
            # PRES
            pres_var = thermo_group.createVariable("pres", "f8", ("time",))
            pres_var[:] = thermo.pres.magnitude
            pres_var.units = str(thermo.pres.units)
            # RH
            rh_var = thermo_group.createVariable("rh", "f8", ("time",))
            rh_var[:] = thermo.rh.magnitude
            rh_var.units = str(thermo.rh.units)
            # ALT
            alt_var = thermo_group.createVariable("alt", "f8", ("time",))
            alt_var[:] = thermo.alt.magnitude
            alt_var.units = str(thermo.alt.units)
            # TEMP
            temp_var = thermo_group.createVariable("temp", "f8", ("time",))
            temp_var[:] = thermo.temp.magnitude
            temp_var.units = str(thermo.temp.units)
            # MIXING RATIO
            mr_var = thermo_group.createVariable("mr", "f8", ("time",))
            mr_var[:] = thermo.mixing_ratio.magnitude
            mr_var.units = str(thermo.mixing_ratio.units)
            # TIME
            time_var = thermo_group.createVariable("time", "f8", ("time",))
            time_var[:] = netCDF4.date2num(thermo.gridded_times,
                                           units='microseconds since \
                                           2010-01-01 00:00:00:00')
            time_var.units = 'microseconds since 2010-01-01 00:00:00:00'

            #
            # Wind
            #

            wind = self.profiles[i].get_wind_profile()

            minlen = min([len(wind.u), len(wind.v), len(wind.dir),
                          len(wind.speed), len(wind.alt), len(wind.pres),
                          len(wind.gridded_times)])

            wind_group.createDimension("time", None)
            # DIRECTION
            dir_var = wind_group.createVariable("dir", "f8", ("time",))
            dir_var[:] = wind.dir[:minlen-1].magnitude
            dir_var.units = str(wind.dir.units)
            # SPEED
            spd_var = wind_group.createVariable("speed", "f8", ("time",))
            spd_var[:] = wind.speed[:minlen-1].magnitude
            spd_var.units = str(wind.speed.units)
            # U
            u_var = wind_group.createVariable("u", "f8", ("time",))
            u_var[:] = wind.u[:minlen-1].magnitude
            u_var.units = str(wind.u.units)
            # V
            v_var = wind_group.createVariable("v", "f8", ("time",))
            v_var[:] = wind.v[:minlen-1].magnitude
            v_var.units = str(wind.v.units)
            # ALT
            alt_var = wind_group.createVariable("alt", "f8", ("time",))
            alt_var[:] = wind.alt[:minlen-1].magnitude
            alt_var.units = str(wind.alt.units)
            # PRES
            pres_var = wind_group.createVariable("pres", "f8", ("time",))
            pres_var[:] = wind.pres[:minlen-1].magnitude
            pres_var.units = str(wind.pres.units)

            # TIME
            time_var = wind_group.createVariable("time", "f8", ("time",))
            time_var[:] = netCDF4.date2num(wind.gridded_times[:minlen-1],
                                           units='microseconds since \
                                           2010-01-01 00:00:00:00')
            time_var.units = 'microseconds since 2010-01-01 00:00:00:00'

        main_file.dev = str(self.dev)

        main_file.close()

    def __str__(self):
        to_return = "=====================================================\n" \
                    + "Profile Set with " + str(len(self.profiles)) + \
                    " Profiles\n"
        for profile in self.profiles:
            to_return = to_return + "\t" + str(profile) + "\n"
        return to_return
