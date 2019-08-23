Thermo_Profile
===================================================================================

.. automodule:: Thermo_Profile
   :members:
   :special-members:
   :private-members:
   :exclude-members: __weakref__

Temperature Calibration
=======================

Resistance (R) to temperature (T)

.. math::

   \begin{aligned}
   T &= \frac{1}{A + B (log{R}) + C (log{R})^3}
   \end{aligned}

Coefficients are pulled from ./coefs.csv on your computer.
