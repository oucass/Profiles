Thermo_Profile
===================================================================================

.. automodule:: Thermo_Profile
   :members:
   :special-members:
   :private-members:
   :exclude-members: __weakref__

.. raw:: html

   <script type="text/javascript">
   var methods = document.getElementsByClassName("method");
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

Temperature Calibration
-----------------------

Resistance (R) to temperature (T)

.. math::

   \begin{aligned}
   T &= \frac{1}{A + B (log{R}) + C (log{R})^3}
   \end{aligned}

Coefficients are pulled from ./coefs/MasterCoefList.csv on your computer.

Equation from: Greene, B.R. Boundary Layer Profiling Using Rotary-Wing Unmanned Aircraft Systems: Filling the Atmospheric Data Gap. Master’s Thesis, The University of Oklahoma, Norman, OK, USA, 2018.
