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








* :ref:`genindex`
* :ref:`search`