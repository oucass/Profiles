utils
=====================
.. module:: profiles.utils
.. autofunction:: profiles.utils.regrid_base
.. autofunction:: profiles.utils.regrid_data
.. function:: profiles.utils.temp_calib
      Converts resistance to temperature using the coefficients for the \
      sensor specified OR generalized coefficients if the serial number (sn)\
      is not recognized.

   :param list<Quantity> resistance: resistances recorded by temperature \
      sensors
   :param int sn: the serial number of the sensor reporting
   :rtype: list<Quantity>
   :return: list of temperatures in K

   **Temperature Calibration**

   Resistance (R) to temperature (T)

   .. math::

      \begin{aligned}
      T &= \frac{1}{A + B (log{R}) + C (log{R})^3}
      \end{aligned}

   Coefficients are pulled from ./coefs/MasterCoefList.csv on your computer.

   Equation from: Greene, B.R. Boundary Layer Profiling Using Rotary-Wing \
      Unmanned Aircraft Systems: Filling the Atmospheric Data Gap. Master’s \
      Thesis, The University of Oklahoma, Norman, OK, USA, 2018.
.. autofunction:: profiles.utils.identify_profile
.. autofunction:: profiles.utils.qc
.. autofunction:: profiles.utils.temp_calib

.. raw:: html

   <script type="text/javascript">
   var methods = document.getElementsByClassName("function");
   var i;
   for (i=0; i<methods.length; i++)
   {
      methods[i].addEventListener("click", function()
         {
            this.classList.toggle("active");
            var content = this.lastElementChild;
            if (content.style.display == "block")
            {
               content.style.display = "none";
            }
            else
            {
               content.style.display = "block";
            }
         });
      // Initially set all to hidden
      methods[i].lastElementChild.style.display = "none";
   }
   </script>
