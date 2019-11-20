Meta
===================================================================================

.. automodule:: Meta
   :members:
   :special-members:
   :private-members:
   :exclude-members: __weakref__

Header and Flight files
-----------------------

The *header file* can contain information applicable to multiple flights to minimize data entry in the field. The columns should be labeled as shown, and there should only be one data row per file. Additional fields may be present, but will not be processed without modification of the source code. No field is required, but it must be a CSV file.

   **timestamp,  operator,  location_id,  location_name,  surface_altitude,  mesonet_id,  region,  pilots_on_site,  objective,  authorization_type,  platform_id,  scoop_id**

The *flight file* contains information relevant only to one specific flight. If you would like, you can have all of the header fields in the flight file and omit the header_path parameter in the Meta constructor. The columns should be labeled as shown and there should only be one data row per file. Additional fields may be present, but will not be processed without modification of the source code. No field is required, but it must be a CSV file.

   **timestamp,  operator,  PIC,  battery_id,  cloud,  rain,  battery_voltage_initial,  max_planned_alt,  launch_time_utc,  max_achieved_alt,  land_time_utc,  battery_voltage_final,  emergency_landing,  emergency_remarks,  private_remarks,  remarks**


