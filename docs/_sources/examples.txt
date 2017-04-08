EXAMPLES
=========


simple gps example
------------------

.. code-block:: python
   :linenos:

   from serial_mock import Serial,serial_query

   class GPSSerial(Serial):
        baudrate=115200
        position={'x':1,'y':2,'z':3}
        @serial_query("get -p")
        def get_position():
            return struct.pack("BBB",[position['x'],position['y'],position['z']])


   GPSSerial("COM99").MainLoop()

real life example: Omega PH METER
---------------------------------

http://www.omega.com/manuals/manualpdf/M4278.pdf

.. code-block:: python
   :linenos:

   from serial_mock import Serial,serial_query

   class Omega_PHH37(Serial):
        baudrate=115200
        user_terminal="\r\n"
        prompt=""
        reading={'ph':7.2,'status':'OK','mv':3.1}
        @serial_query("#001N")
        def get_reading(self):
            return "\xff\xfe\x02\x06\x06"+"{status}{ph:0.4f}{mv:0.4f}\xaa\xbb".format(**self.reading)

    Omega_PHH37("COM99").MainLoop()

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`