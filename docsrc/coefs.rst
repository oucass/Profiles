***************************
Set-Up: Sensor Coefficients
***************************

This page attempts to break down the
process of specifying your coefficients into manageable steps. If you get stuck,
send us a message using the contact form on our home page!

There are 2 ways to host your coefficients so that oucass-profiles can read them. 
The simplest is to use CSV files in your local file system. Larger teams are likely to 
prefer the instant updates possible when your coefficients are stored in Azure tables.

Local File System
============================

Step 1: Start your file structure
----------------------------------

First, you're going to want to make a folder somewhere named "coefs". It doesn't
matter where you put this folder, just that the name is correct.

::

   |coefs

Step 2: Assign each platform a unique numerical ID
---------------------------------------------------

Inside coefs, create a file named "copterID.csv". This file should contain
entries of the format

::

   1, name of copter 1
   2, name of copter 2
   3, name of copter 3
   ...

The numerical ID should be saved to the "SYSID_THISMAV" variable in your JSON
file so that each JSON file can be associated with a particular platform.

::

   |coefs
    |-copterID.csv

Step 3: Assign each sensor to a "scoop"
---------------------------------------

In profiles, a "scoop" is a collection of sensors. If your platforms have
interchangeable sensor loads, this can be really useful. If not, the "scoop"
will represent the platform itself.

Label each scoop (or platform) with a single uppercase letter. For each scoop,
create a file "scoop<letter>.csv" in coefs. For Scoop A, the file would be
called "scoopA.csv". The format should be similar to

....

.. csv-table::

   validFrom,imet1,imet2,imet3,rh1,rh2,rh3,wind
   2019-08-29,57562,57563,58821,1,2,3,944

....

Any time a sensor is changed, a new line should be added to this file with the
date of the change and the new sensor numbers.

::

   |coefs
    |-copterID.csv
    |-scoopA.csv
    |-scoopB.csv
    |-...

Step 4: Supply the coefficients
----------------------------------

Now that profiles will be able to identify which sensors you're using, it's
probably a good idea to tell it the coefficients of those sensors. We'll make
one more file in the coefs folder, this time named "MasterCoefList.csv". The
header for this file should be

....

.. csv-table::

  SensorType,SerialNumber,ScoopID,Equation,A,B,C,D,Offset,SensorStatus

....

Each sensor gets its own row. Any field that isn't applicable to a sensor should
be filled with "na". Profiles currently supports 3 types of sensors.

Wind
~~~~

"Wind" is recognized as a sensor type, although the "sensor" in this case is
the copter itself. The serial number is the copter's name. If you have
interchangeable scoops, the scoop field should be "na". Otherwise, you can set
it to the scoop letter associated with the platform.

The equation for wind should be "E1", unless you decide to write your own
calibration equation. The default calibration equation requires two
coefficients and no offset. The sensor status column is for your personal
records.

A row describing a wind sensor should look something like this:

....

.. csv-table::

   SensorType,SerialNumber,ScoopID,Equation,A,B,C,D,Offset,SensorStatus
   Wind,944,na,E1,3.28E+01,-4.50E+00,na,na,na,Active

....

IMet
~~~~

The IMet sensor handles temperature. A row describing an IMet sensor could look
like this:

....

.. csv-table::

   SensorType,SerialNumber,ScoopID,Equation,A,B,C,D,Offset,SensorStatus
   Imet,45363,na,E2,9.93118592E-04,2.63743049E-04,1.47415476E-07,na,na,Retired

....

RH
~~

There is not currently a calibration equation for relative humidity - instead,
an offset is accepted. A line for an RH sensor should look like this:

....

.. csv-table::

   SensorType,SerialNumber,ScoopID,Equation,A,B,C,D,Offset,SensorStatus
   RH,3,A,na,na,na,na,na,1843,Active

....

At this point, your coef folder should contain the following files:

::

   |coefs
    |-copterID.csv
    |-scoopA.csv
    |-scoopB.csv
    |-...
    |-MasterCoefList.csv

Azure Tables
==============

Step 1: Create an Azure "Storage Account"
-----------------------------------------

Make an account for your team at https://www.portal.azure.com. You can get set up with a free account, but will eventually need to transition to a paid account. Individual team members can make changes to the team account from personal, free accounts.

The easiest way to interact with your Storage Account is through Microsoft Azure Storage Explorer. 

Step 2: Assign each platform a unique numerical ID
--------------------------------------------------

Each platform (UAS) will need to have an ID, in addition to a name. The ID should be saved to the "SYSID_THISMAV" variable in your JSON file.

Create a new Table in your Storage Account named "Copters". The PartitionKey can be whatever you'd like, or you can leave it set to "default". The CopterID should be assigned to RowKey, with the name of the copter in a new Property (column) called "Name"

Step 3: Assign each sensor to a "scoop"
----------------------------------------

In oucass-profiles, a "scoop" is a collection of sensors that are used together. If your platforms have interchangable sensor loads, this can be really useful. If not, the "scoop" will represent the platform itself.

Using Azure allows you more freedom in chosing your scoop names. You can use single character names (such as "A") or descriptive names (like "ChemFW1"). Assign these names to the PartitionKey of each row in a new table called "Scoops". The RowKey must be a date in the format YYYYMMDD and should represent the day on which the listed sensors were installed on the scoop. Don't delete outdated entries - oucass-profiles will make sure to use the serial numbers associated with thelatest scoop entry BEFORE the flight date.

The Parameters of the Scoops table should be "Engineer", "IMET1", "IMET2", ..., "RH1", "RH2", ... The Engineer field can be used to identify the person who created an entry in the case of any discrepancies.

Step 4: Supply the coefficients
--------------------------------

The next Table to create in your Storage Account is "MasterCoef". There should be one row per sensor in your inventory. The PartitionKey identifies the type of sensor ("Imet", "RH", or "Wind"), while the RowKey specifies the sensor's serial number. The serial number "0" is used to specify default coefficients for rough calculations when specific coefficients are not available. 

The Parameters "A", "B", "C", "D", and "Offset" must exist in your table. The lettered columns hold the actual coefficients to convert resistance or voltage to some atmospheric property. "Offset" is used when a sensor (typically an RH sensor) is corrected for bias. Additional Parameters can be added according to your team's needs.
