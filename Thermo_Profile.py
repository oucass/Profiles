"""
Calculates and stores basic thermodynamic parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
from metpy import calc
import utils
import numpy as np
import netCDF4
import os

coeff = {"N955":
         {"IMET1": (1.02777010e-03, 2.59349232e-04, 1.56043078e-07),  # 57562
          "IMET2": (9.91077399e-04, 2.64646362e-04, 1.43596294e-07),  # 57563
          "IMET3": (1.00786813e-03, 2.61722397e-04, 1.48476183e-07)  # 58821
          }}

"""
More coefficients can be found at https://github.com/oucass/CASS-ardupilot/
blob/Copter-3.6/ArduCopter/sensors.cpp
"""


class Thermo_Profile():
    """ Contains data from one file.

    :var tuple<list<Quantity>, Datetime> temp: QC'd and averaged temperature
    :var tuple<list<Quantity>, Datetime> mixing_ratio: calculated mixing ratio
    :var tuple<list<Quantity>, Datetime> pres: QC'd pressure
    :var list<Datetime> time: times at which processed data exists
    :var Quantity resolution: vertical resolution in units of time,
           altitude, or pressure to which the data is calculated
    """

    def __init__(self, temp_dict, resolution, indices=(None, None),
                 ascent=True, units=None, filepath=None, nnumber=None):
        """ Creates Thermo_Profile object from raw data at the specified
        resolution.

        :param dict temp_dict: A dictionary of the format \
           {"temp1":, "temp2":, ..., "tempj":, \
            "resi1":, "resi2":, ..., "resij", "time_temp":, \
            "rh1":, "rh2":, ..., "rhk":, "time_rh":, \
            "temp_rh1":, "temp_rh2":, ..., "temp_rhk":, \
            "pres":, "temp_pres":, "ground_temp_pres":, \
            "alt_pres":, "time_pres"}, which is returned by \
            Raw_Profile.thermo_data
        :param Quantity resoltion: vertical resolution in units of time,
           altitude, or pressure to which the data should be calculated
        :param str filepath: the path to the original data file WITHOUT the \
           suffix .nc or .json
        """

        self.resolution = resolution
        self.time = None
        self.rh = None
        self.pres = None
        self.temp = None
        self.alt = None
        self._units = units
        self._sb_CAPE = None  # calculate upon access
        self._datadir = os.path.dirname(filepath + ".json")
        temp = []
        rh = []

        if os.path.basename(filepath + "thermo.nc") in \
           os.listdir(self._datadir):
            print("Reading thermo_profile from pre-processed netCDF")
            self._read_netCDF(filepath)
            return
        elif False in np.isnan(temp_dict["resi1"]):  # if resistances logged
            resi_raw = []  # List of lists, each containing data from a sensor

            # Fill resi_raw
            for key in temp_dict.keys():
                if "resi" in key:
                    resi_raw.append(temp_dict[key].magnitude)

            # Calculate temperature
            temp_raw = np.pow(np.add(np.add(
                        np.multiply(np.log(resi_raw), coeff[nnumber][1])),
                        np.multiply(np.pow(resi_raw, 3), coeff[nnumber][2])),
                                       -1)

            print("Temperature calculated from resistance using coefficients ",
                  coeff[nnumber])

        else:  # Use logged temperatures
            temp_raw = []  # List of lists, each containing data from a sensor

            # Fill temp_raw
            for key in temp_dict.keys():

                if "temp" in key and "_" not in key:
                    temp_raw.append(temp_dict[key].magnitude)

        # End if-else blocks

        rh_raw = []
        # Fill rh_raw
        for key in temp_dict.keys():
            # Ensure only humidity is processed here
            if "rh" in key and "temp" not in key and "time" not in key:
                rh_raw.append(temp_dict[key].magnitude)

        alts = (np.array(temp_dict["alt_pres"].magnitude)
                * temp_dict["alt_pres"].units)
        pres = (np.array(temp_dict["pres"].magnitude)
                * temp_dict["pres"].units)

        # If no indices given, use entire file
        if not indices[0] is None:
            # trim rh, temp_dict["time_rh"], pres, temp_dict["time_pres"],
            # temp, temp_dict["time_temp"], alt
            time_rh = temp_dict["time_rh"]
            selection_rh = np.where(np.array(time_rh) > indices[0],
                                    np.array(time_rh) < indices[1], False)
            rh_raw = np.array(rh_raw)[:, selection_rh] * temp_dict["rh1"].units
            time_rh = np.array(time_rh)[selection_rh]

            time_pres = temp_dict["time_pres"]
            selection_pres = np.where(np.array(time_pres) > indices[0],
                                      np.array(time_pres) < indices[1],
                                      False)
            pres = np.array(pres.magnitude)[selection_pres] * pres.units
            alts = np.array(alts.magnitude)[selection_pres] * alts.units
            time_pres = np.array(time_pres)[selection_pres]

            time_temp = temp_dict["time_temp"]
            selection_temp = np.where(np.array(time_temp) > indices[0],
                                      np.array(time_temp) < indices[1],
                                      False)
            temp_raw = np.array(temp_raw)[:, selection_temp] * \
                temp_dict["temp1"].units
            time_temp = np.array(time_temp)[selection_temp]
        else:
            time_rh = temp_dict["time_rh"]
            time_pres = temp_dict["time_pres"]
            time_temp = temp_dict["time_temp"]
        # Determine bad sensors
        rh_flags = utils.qc(rh_raw, 0.4, 0.2)

        # Remove bad sensors
        for flags_ind in range(len(rh_flags)):
            if rh_flags[flags_ind] != 0:
                rh_raw[flags_ind] = np.NaN

        # Average the sensors
        for i in range(len(rh_raw[0])):
            rh.append(np.nanmean([rh_raw[a][i].magnitude for a in
                                  range(len(rh_raw))]))

        rh = np.array(rh) * rh_raw.units

        # Determine which sensors are "bad"
        temp_flags = utils.qc(temp_raw, 0.25, 0.1)

        # Remove bad sensors
        temp_ind = 0  # track index in temp_raw  after items are removed.
        for flags_ind in range(len(temp_flags)):
            if temp_flags[flags_ind] != 0:
                temp_raw.pop(temp_ind)
            else:
                temp_ind += 1

        # Average the sensors
        for i in range(len(temp_raw[0])):

            temp.append(np.nanmean([temp_raw[a][i].magnitude for a in
                                   range(len(temp_raw))]))

        temp = np.array(temp) * temp_raw.units

        #
        # Regrid to res
        #
        if resolution.dimensionality == alts.dimensionality:
            base = alts
            base_time = time_pres
        elif resolution.to_base_units().units == pres.to_base_units().units:
            base = pres
            base_time = time_pres

        # grid rh
        base, base_time, self.pres = utils.regrid(base=base,
                                                  base_times=base_time,
                                                  data=pres,
                                                  data_times=time_pres,
                                                  new_res=resolution,
                                                  ascent=ascent,
                                                  units=self._units)

        self.rh = utils.regrid(base=base, base_times=base_time,
                               data=rh,
                               data_times=time_rh,
                               new_res=resolution,
                               ascent=ascent,
                               units=self._units)[2]

        # grid temp
        self.temp = utils.regrid(base=base, base_times=base_time,
                                 data=temp,
                                 data_times=time_temp,
                                 new_res=resolution, ascent=ascent,
                                 units=self._units)[2]

        # grid alt
        self.alt = utils.regrid(base=base, base_times=base_time,
                                data=alts,
                                data_times=time_pres,
                                new_res=resolution, ascent=ascent,
                                units=self._units)[2]

        minlen = min(len(base), len(base_time), len(self.rh),
                     len(self.pres), len(self.temp), len(self.alt))
        self.pres = self.pres[0:minlen-1]
        self.temp = self.temp[0:minlen-1]
        self.rh = self.rh[0:minlen-1]
        self.alt = self.alt[0:minlen-1]
        self.time = base_time[0:minlen-1]

        # Calculate mixing ratio
        self.mixing_ratio = calc.mixing_ratio_from_relative_humidity(
                            np.divide(self.rh.magnitude, 100), self.temp,
                            self.pres)
        self._save_netCDF(filepath)

    def _save_netCDF(self, file_path):
        """ Save a NetCDF file to facilitate future processing if a .JSON was
        read.

        :param string file_path: file name
        """
        main_file = netCDF4.Dataset(file_path + "thermo.nc", "w",
                                    format="NETCDF4", mmap=False)

        main_file.createDimension("time", None)
        # PRES
        pres_var = main_file.createVariable("pres", "f8", ("time",))
        pres_var[:] = self.pres.magnitude
        pres_var.units = str(self.pres.units)
        # RH
        rh_var = main_file.createVariable("rh", "f8", ("time",))
        rh_var[:] = self.rh.magnitude
        rh_var.units = str(self.rh.units)
        # ALT
        alt_var = main_file.createVariable("alt", "f8", ("time",))
        alt_var[:] = self.alt.magnitude
        alt_var.units = str(self.alt.units)
        # TEMP
        temp_var = main_file.createVariable("temp", "f8", ("time",))
        temp_var[:] = self.temp.magnitude
        temp_var.units = str(self.temp.units)
        # MIXING RATIO
        mr_var = main_file.createVariable("mr", "f8", ("time",))
        mr_var[:] = self.mixing_ratio.magnitude
        mr_var.units = str(self.mixing_ratio.units)
        # TIME
        time_var = main_file.createVariable("time", "f8", ("time",))
        time_var[:] = netCDF4.date2num(self.time, units='microseconds since \
                2010-01-01 00:00:00:00')
        time_var.units = 'microseconds since 2010-01-01 00:00:00:00'

        main_file.close()

    def _read_netCDF(self, file_path):
        """ Reads data from a NetCDF file. Called by the constructor.

        :param string file_path: file name
        """
        main_file = netCDF4.Dataset(file_path + "thermo.nc", "r",
                                    format="NETCDF4", mmap=False)
        # Note: each data chunk is converted to an np array. This is not a
        # superfluous conversion; a Variable object is incompatible with pint.

        self.pres = np.array(main_file.variables["pres"]) * \
                    self._units.parse_expression(main_file.variables["pres"]\
                                                 .units)
        self.rh = np.array(main_file.variables["rh"]) * \
                    self._units.parse_expression(main_file.variables["rh"]\
                                                 .units)
        self.alt = np.array(main_file.variables["alt"]) * \
                    self._units.parse_expression(main_file.variables["alt"]\
                                                 .units)
        self.temp = np.array(main_file.variables["temp"]) * \
                    self._units.parse_expression(main_file.variables["temp"]\
                                                 .units)
        self.mixing_ratio = np.array(main_file.variables["mr"]) * \
                    self._units.parse_expression(main_file.variables["mr"]\
                                                 .units)
        self.time = np.array(netCDF4.num2date(main_file.variables["time"][:],
                                              units=main_file.variables\
                                              ["time"].units))
        main_file.close()

    def get_surface_based_CAPE():
        """ Either calculates (the first call) or retrieves (later calls) the
        value of surface based CAPE.

        :rtype: Quantity
        :return: surface-based CAPE
        """
