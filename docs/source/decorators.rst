
SerialMock `SerialQuery` Decorator
==================================

.. py:decoratormethod:: serial_mock.serial_query(route=None,delay=None)

   :param str route: the serial instruction to recieve
   :param delay: How long this command takes to return
   :type delay: int or float

   specify a class function as a serial interface... if you do not specify a route, it will default to a "normalized" version of the function name that would be a reasonable serial directive
    *the method MUST accept at least one argument, the instance of the* :class:`serial_mock.mock.Serial` *that is being run.*

.. code-block:: python
    :linenos:

    from serial_mock import Serial
    from serial_mock import serial_query

    class MySerial(Serial):
        ...
        @serial_query # since we did not specify an explicit route,this will default to a rout of "get name"
        def get_name(self):
             return self.name

        @serial_query # again this will default to "set name" and will expect one argument (the name to set)
        def set_name(self,name):
             self.name = name
             return "OK"

        @serial_query("quick scan") # this time we will override the command, if we did not the route would be "do scan"
        def do_scan():
            return " ".join(map(str,range(9)))

        @serial_query("long scan",delay=5) # this time we will do a long scan with a delay of 5 seconds
        def do_long_scan(): # the decorator will take care of the delay for us
            return self.do_scan() # note that the decorator leaves the original function unaffected

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`