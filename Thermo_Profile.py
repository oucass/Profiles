"""
Calculates and stores basic thermodynamic parameters

Authors Brian Greene, Jessica Wiedemeier, Tyler Bell, Gus Azevedo \n
Copyright University of Oklahoma Center for Autonomous Sensing and Sampling
2019
"""
from metpy import calc
import utils
import numpy as np


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
                 ascent=True, units=None):
        """ Creates Thermo_Profile object from raw data at the specified
        resolution.

        :param dict temp_dict: A dictionary of the format \
           {"temp1":, "temp2":, ..., "tempj":, "time_temp":, \
            "rh1":, "rh2":, ..., "rhk":, "time_rh":, \
            "temp_rh1":, "temp_rh2":, ..., "temp_rhk":, \
            "pres":, "temp_pres":, "ground_temp_pres":, \
            "alt_pres":, "time_pres"}, which is returned by \
            Raw_Profile.thermo_data
        :param Quantity resoltion: vertical resolution in units of time,
           altitude, or pressure to which the data should be calculated
        """

        self.resolution = resolution
        self.time = None
        self.rh = None
        self.pres = None
        self.temp = None
        self.alt = None
        self._units = units
        self._sb_CAPE = None  # calculate the first time get_surface_based_CAPE
        # is called

        # QC temperatures reported as voltage
        # TODO: determine max_bias and max_variance. Right now both are 3.
        temp_raw = []  # List of lists, each one containing data from a sensor
        temp = []  # Average of qc'd data at each timestamp

        # Fill temp_raw
        for key in temp_dict.keys():
            # Ensure only humidity is processed here
            if "temp" in key and "_" not in key:
                temp_raw.append(temp_dict[key].magnitude)

        # Determine bad sensors
        temp_flags = utils.qc(temp_raw, 0.4, 0.2)

        # Remove bad sensors
        temp_ind = 0  # tracks the index in temp_raw after items are removed.
        for flags_ind in range(len(temp_flags)):
            if temp_flags[flags_ind] != 0:
                temp_raw.pop(temp_ind)
            else:
                temp_ind += 1

        # Average the sensors
        for i in range(len(temp_raw[0])):
            temp.append(np.nanmean(np.array([temp_raw[a][i] for a in
                                   range(len(temp_raw))])))
        temp = temp

        # TODO convert to K from mV

        rh_raw = []  # List of lists, each one containing data from a sensor
        rh = []  # Average of qc'd data at each timestamp

        # Fill rh_raw
        for key in temp_dict.keys():
            # Ensure only humidity is processed here
            if "rh" in key and "temp" not in key and "time" not in key:
                rh_raw.append(temp_dict[key].magnitude)

        # Determine bad sensors
        rh_flags = utils.qc(rh_raw, 0.4, 0.2)

        # Remove bad sensors
        rh_ind = 0  # tracks the index in rh_raw even after items are removed.
        for flags_ind in range(len(rh_flags)):
            if rh_flags[flags_ind] != 0:
                rh_raw.pop(rh_ind)
            else:
                rh_ind += 1

        # Average the sensors
        for i in range(len(rh_raw[0])):
            rh.append(np.nanmean([rh_raw[a][i] for a in
                                  range(len(rh_raw))]))

        alts = (np.array(temp_dict["alt_pres"].magnitude)
                * temp_dict["alt_pres"].units)
        # TODO Pressure QC
        pres = (np.array(temp_dict["pres"].magnitude)
                * temp_dict["pres"].units)

        # If no indices given, use entire file
        if not indices[0] is None:
            # trim rh, temp_dict["time_rh"], pres, temp_dict["time_pres"],
            # temp, temp_dict["time_temp"], alt
            time_rh = temp_dict["time_rh"]
            selection_rh = np.where(np.array(time_rh) > indices[0],
                                    np.array(time_rh) < indices[1], False)
            rh = np.array(rh)[selection_rh] * temp_dict["rh1"].units
            time_rh = np.array(time_rh)[selection_rh]

            time_pres = temp_dict["time_pres"]
            selection_pres = np.where(np.array(time_pres) > indices[0],
                                      np.array(time_pres) < indices[1], False)
            pres = np.array(pres.magnitude)[selection_pres] * pres.units
            alts = np.array(alts.magnitude)[selection_pres] * alts.units
            time_pres = np.array(time_pres)[selection_pres]

            time_temp = temp_dict["time_temp"]
            selection_temp = np.where(np.array(time_temp) > indices[0],
                                      np.array(time_temp) < indices[1], False)
            temp = np.array(temp)[selection_temp] * temp_dict["temp1"].units
            time_temp = np.array(time_temp)[selection_temp]
        else:
            time_rh = temp_dict["time_rh"]
            time_pres = temp_dict["time_pres"]
            time_temp = temp_dict["time_temp"]

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
        # TODO this line only works with temp in temperature units, not mV
        # self.mixing_ratio = calc.mixing_ratio_from_relative_humidity(
        #                    self.rh, self.temp, self.pres)

    def get_surface_based_CAPE():
        """ Either calculates (the first call) or retrieves (later calls) the
        value of surface based CAPE.

        :rtype: Quantity
        :return: surface-based CAPE
        """
