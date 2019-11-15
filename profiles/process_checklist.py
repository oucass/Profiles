import pandas as pd
import numpy as np

class Meta:
    """ Processes, stores, and writes metadata files (JSON-LD for public, CSV for private) for a flight

       :var dict<str: Object> all_fields: Dictionary containing all information to be written to metadata files
       :var list<str> private_fields: List of fields to be included in the CSV file
       :var list<str> public_fields: List of fields to be included in the JSON file
    """

    def __init__(self, header_path, flight_path):

        self.private_fields = ["timestamp", "checklist_operator", "location", "PIC", "objective", "authorization_type",
                               "platform_id", "max_planned_alt", "battery_id", "scoop_id", "battery_voltage_initial",
                               "launch_time_utc", "max_achieved_alt", "land_time_utc", "battery_voltage_final",
                               "emergency_landing", "emergency_remarks", "private_remarks"]
        self.public_fields = ["date_utc", "region", "location", "objective", "cloud", "rain", "wind_from_direction",
                              "wind_speed", "wind_speed_of_gust", "surface_altitude", "launch_time_utc",
                              "max_achieved_alt", "land_time_utc", "remarks", "variables", "platform_id",
                              "platform_name"]
        self.all_fields = {}

        if not ".csv" in header_path and not ".csv" in flight_path:
            self.combine_files(header_path, flight_path)
            return


        self.all_fields = {"timestamp": None,
                           "checklist_operator": None,
                           "location": None,
                           "PIC": None,
                           "objective": None,  # space-delimited list of wind, thermo, chem, ...
                           "authorization_type": None,
                           "platform_id": None,  # tail number
                           "max_planned_alt": None,
                           "battery_id": None,
                           "scoop_id": None,
                           "battery_voltage_initial": None,
                           "launch_time_utc": None,
                           "max_achieved_alt": None,
                           "land_time_utc": None,
                           "battery_voltage_final": None,
                           "emergency_landing": None,  # Y/N
                           "emergency_remarks": None,
                           "private_remarks": None,
                           "region": None,  # default is north_america
                           "cloud": None,  # cloud cover in percent
                           "rain": None,  # Y or N
                           "wind_from_direction": None,
                           "wind_speed": None,
                           "wind_speed_of_gust": None,
                           "surface_altitude": None,
                           "launch_time_utc": None,
                           "max_achieved_alt": None,
                           "land_time_utc": None,
                           "remarks": None,
                           "variables": None,
                           "platform_id": None,  # tail number
                           "platform_name": None,  # copter type (i.e. TonyShark3)
                           }

        self.read_file(header_path)
        self.read_file(flight_path)

    def read_file(self, csv_path):
        file = pd.read_csv(csv_path)
        for field in self.all_fields.keys():
            if field in file.keys():
                if field is not None and self.all_fields[field] is not None:
                    print("Replaced " + str(self.all_fields[field] + " with " + str(file[field])))
                    self.all_fields[field] = np.array(file[field])[0]
                    return
                else:
                    self.all_fields[field] = np.array(file[field])[0]

    def combine_files(self, file1, file2):
        file1 = open(file1, 'r')
        file2 = open(file2, 'r')
        lines1 = file1.readlines()
        lines2 = file2.readlines()
        for line in lines1:
            if line in lines2:
                # This line is the same in both files - use it
                parts = line.partition(": ")
                self.all_fields[parts[0]] = parts[1]

    def write_public_meta(self, out_path):  # for the flight
        file = open(out_path, 'w')
        order = self.public_fields.sort()
        i = 0
        while i < len(order):
            file.write(order[i] + ": " + str(self.all_fields[order[i]]) + "\n")
            i += 1

        return

    def get(self, field):
        return self.all_fields[field]
