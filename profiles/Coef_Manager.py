import os
import pandas as pd
from abc import abstractmethod

class Coef_Manager_Base:
    @abstractmethod
    def get_tail_n(self, copterID):
        """ Get the tail number corresponding to a short ID number.

        :param int copterID: the short ID number of the copter
        :rtype: str
        :return: the tail number
        """
        pass

    @abstractmethod
    def get_sensors(self, scoopID):
        """ Get the sensor serial numbers for the given scoop.

        :param str scoopID: The scoop's identifier
        :rtype: dict
        :return: sensor numbers as {"imet1":"", "imet2":"", "imet3":"", "imet4":"",\
                                    "rh1":"", "rh2":"", "rh3":"", "rh4":""}
        """
        pass

    @abstractmethod
    def get_coefs(self, type, serial_number):
        """ Get the coefs for the sensor with the given type and serial number.

        :param str type: "Imet" or "RH" or "Wind"
        :param str serial_number: the sensor's serial number
        :rtype: dict
        :return: information about the sensor, including offset OR coefs and calibration equation
        """
        pass


class Coef_Manager(Coef_Manager_Base):
    """ Reads the .profilesrc file to determine if the coefs are in the \
       local file system or on Azure and to determine the file path \
       or connection string, then ingests the data from the proper source. \
       This object can then be queried by scoop number (to get sensor numbers), \
       by sensor numbers (to get coefs), or by copter number (to get tail \
       number).
    """

    def __init__(self):
        """ Create Coef_Manager
        """
        # The sub_manager will implement all abstract methods
        self.sub_manager = None
        if coef_info.USE_AZURE.upper() in "YES":
            try:
                table_service = Table_Service(connection_string=coef_info.CONNECTION_STRING_1)
            except Exception:
                try:
                    table_service = Table_Service(connection_string=coef_info.CONNECTION_STRING_2)
                except Exception:
                    raise Exception("There are no valid connection strings in __init__.py")
            # If this point has been reached, we have an active table_service to pull data from
            self.sub_manager = Azure_Coef_Manager(table_service)
        elif coef_info.USE_AZURE.upper() in "NO":
            if len(coef_info.FILE_PATH) > 0:
                if os.exists(coef_info.FILE_PATH):
                    self.sub_manager = CSV_Coef_Manager(coef_info.FILE_PATH)
                else:
                    raise Exception("The FILE_PATH in __init__.py is not valid")
            else:
                raise Exception("When USE_AZURE is NO, the FILE_PATH must be set in __init__.py.")
        else:
            raise Exception("USE_AZURE in __init__.py must be YES or NO")

    def get_tail_n(self, copterID):
        """ Get the tail number corresponding to a short ID number.

        :param int copterID: the short ID number of the copter
        :rtype: str
        :return: the tail number
        """
        return self.sub_manager.get_tail_n(copterID)

    def get_sensors(self, scoopID):
        """ Get the sensor serial numbers for the given scoop.

        :param str scoopID: The scoop's identifier
        :rtype: dict
        :return: sensor numbers as {"imet1":"", "imet2":"", "imet3":"", "imet4":"",\
                                    "rh1":"", "rh2":"", "rh3":"", "rh4":""}
        """
        return self.sub_manager.get_sensors(scoopID)

    def get_coefs(self, type, serial_number):
        """ Get the coefs for the sensor with the given type and serial number.

        :param str type: "Imet" or "RH" or "Wind"
        :param str serial_number: the sensor's serial number
        :rtype: dict
        :return: information about the sensor, including offset OR coefs and calibration equation
        """
        return self.sub_manager.get_coefs(type, serial_number)


class Azure_Coef_Manager:
    """ interface with Azure
    """

    def __init__(table_service):
        """ Create Azure_Coef_Manager

        :param azure.cosmosdb.table.tableservice.TableService table_service: TableService connected \
           to storage account containing coef tables
        """
        self.table_service = table_service

    def get_tail_n(self, copterID):
        """ Get the tail number corresponding to a short ID number.

        :param int copterID: the short ID number of the copter
        :rtype: str
        :return: the tail number
        """
        copter_entity = self.table_service.query_entities('Copters', filter="PartitionKey eq \'"+str(copterID)+"\'")
        # TODO there has to be a more elegant way to do this...
        for entity in copter_entity:
            return entity.RowKey

    def get_sensors(self, scoopID):
        """ Get the sensor serial numbers for the given scoop.

        :param str scoopID: The scoop's identifier
        :rtype: dict
        :return: sensor numbers as {"imet1":"", "imet2":"", "imet3":"", "imet4":"",\
                                    "rh1":"", "rh2":"", "rh3":"", "rh4":""}
        """
        all_id_entries = self.table_service.query_entities('Scoops', filter="PartitionKey eq \'"+str(scoopID)+"\'")

        max_date=0
        for entry in all_id_entries:
            if int(entry.RowKey) > max_date:
                max_date = int(entry.RowKey)

        sns = self.table_service.get_entity('Scoops', str(scoopID), str(max_date))
        return {"imet1":sns.IMET1, "imet2":sns.IMET2, "imet3":sns.IMET3, "imet4":sns.IMET4,
                "rh1":sns.RH1, "rh2":sns.RH2, "rh3":sns.RH3, "rh4":sns.RH4}

    def get_coefs(self, type, serial_number):
        """ Get the coefs for the sensor with the given type and serial number.

        :param str type: "Imet" or "RH" or "Wind"
        :param str serial_number: the sensor's serial number
        :rtype: dict
        :return: information about the sensor, including offset OR coefs and calibration equation
        """
        coefs = self.table_service.get_entity('MasterCoef', type, str(serial_number))

        return {"A":coefs.A, "B":coefs.B, "C":coefs.C, "D":coefs.D, "Equation":coefs.Equation,
                "Offset":coefs.Offset}


class CSV_Coef_Manager(Coef_Manager_Base):

    def __init__(self, file_path):
        self.coefs = pd.read_csv(os.path.join(file_path, 'MasterCoefList.csv'))
        self.copternums = pd.read_csv(os.path.join(file_path, 'copterID.csv'), header=0)

    def get_tail_n(self, copterID):
        """ Get the tail number corresponding to a short ID number.

        :param int copterID: the short ID number of the copter
        :rtype: str
        :return: the tail number
        """
        return self.copternums[2][int(self.copternums[1]) == (copterID)]

    def get_sensors(self, scoopID):
        """ Get the sensor serial numbers for the given scoop.

        :param str scoopID: The scoop's identifier
        :rtype: dict
        :return: sensor numbers as {"imet1":"", "imet2":"", "imet3":"", "imet4":"",\
                                    "rh1":"", "rh2":"", "rh3":"", "rh4":""}
        """
        scoop_info = pd.read_csv(os.path.join(file_path, 'scoop'+str(scoopID)+'.csv'))
        max_date="0000-00-00"
        for row in scoop_info:
            if row.validFrom > max_date:
                max_date = row.validFrom

        most_recent = scoop_info[scoop_info.validFrom == max_date]
        return {"imet1":str(most_recent.imet1), "imet2":str(most_recent.imet2),
                "imet3":str(most_recent.imet3), "imet4":None, "rh1":str(most_recent.rh1),
                "rh2":str(most_recent.rh2),  "rh3":str(most_recent.rh3), "rh4":None}

    def get_coefs(self, type, serial_number):
        """ Get the coefs for the sensor with the given type and serial number.

        :param str type: "Imet" or "RH" or "Wind"
        :param str serial_number: the sensor's serial number
        :rtype: dict
        :return: information about the sensor, including offset OR coefs and calibration equation
        """
        coefs = self.coefs
        a = float(coefs.A[coefs.SerialNumber == serial_number][coefs.SensorType == type])
        b = float(coefs.B[coefs.SerialNumber == serial_number][coefs.SensorType == type])
        c = float(coefs.C[coefs.SerialNumber == serial_number][coefs.SensorType == type])
        d = float(coefs.D[coefs.SerialNumber == serial_number][coefs.SensorType == type])
        eq = float(coefs.Equation[coefs.SerialNumber == serial_number][coefs.SensorType == type])
        offset = float(coefs.Offset[coefs.SerialNumber == serial_number][coefs.SensorType == type])

        return {"A":a, "B":b, "C":c, "D":d, "Equation":eq, "Offset":offset}
