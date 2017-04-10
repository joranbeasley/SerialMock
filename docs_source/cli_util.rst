Using the include CLI tool
==========================

In order to use the CLI tool, you must first create a null modem.

to execute the cli command simply invoke

.. code-block:: bash

    python -m serial_mock.cli COMMAND`

the available commands are detailed below

CLI commands
------------

to view help on a given command simply invoke the command with the :code:`-h` or :code:`--help` switch

echo directive
______________

the :code:`echo` cli directive will bind a simple echo device to the specified bind port

.. code-block:: bash

    python -m serial_mock.cli echo COMPORT

where **COMPORT** is one half of a pair of ports specified when you created a null modem.


bridge directive
________________

the :code:`bridge` cli directive will create a bridge between two points, optionally capturing the traffic to a log file for use with the :code:`build` directive

.. image:: _static/bridge_diagram.png

.. code-block:: bash

    python -m serial_mock.cli bridge COMPORT1 COMPORT2 <options>


where **COMPORT1** and **COMPORT2** are the two ports you wish to bridge, typically one port will be an actual connected device and the 2nd port will be one end of a null modem that you created.

.. seealso::

  .. toctree::
     :maxdepth: 2

     nullmodem


build directive
_______________

the build directive can convert a logfile created with the :code:`bridge` directive, and convert it into a "playback" device, that will play back the responses from the bridged session

.. code-block:: bash

    python -m serial_mock.cli build serial_output.txt --out=MySerialDevice.py



* :ref:`genindex`
* :ref:`search`