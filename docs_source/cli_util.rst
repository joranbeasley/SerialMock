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

echo command
____________

the :code:`echo` cli command will bind a simple echo device to the specified bind port

.. code-block:: bash

    python -m serial_mock.cli echo COMPORT

where **COMPORT** is one half of a pair of ports specified when you created a null modem.


bridge command
______________

the :code:`bridge` cli command will bind a simple echo device to the specified bind port

.. code-block:: bash

    python -m serial_mock.cli bridge COMPORT1 COMPORT2 <options>


where **COMPORT1** and **COMPORT2** are the two ports you wish to bridge, typically one port will be an actual connected device and the 2nd port will be one end of a null modem that you created.

.. seealso::

  .. toctree::
     :maxdepth: 2

     nullmodem







* :ref:`genindex`
* :ref:`search`