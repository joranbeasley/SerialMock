
serial_mock `serial_query` Decorator
====================================

.. py:decoratormethod:: serial_mock.serial_query(route=None,delay=None)

   :param str route: the serial instruction to recieve
   :param delay: How long this command takes to return
   :type delay: int or float

   specify a class function as a serial interface... if you do not specify a route, it will default to a "normalized" version of the function name that would be a reasonable serial directive
    *the method MUST accept at least one argument, the instance of the* :class:`serial_mock.mock.Serial` *that is being run.*

the route argument
------------------

The **route** argument is the primary argument to this decorator and it is very flexible. by default it will convert the function name into a "serial query"

default behavior
________________

for most use cases the default behavior should be sufficient to meet your needs, if it doesnt, have no fear, explicitly declaring the route gives you near unlimmited flexibility

>>> @serial_query
... def show(self):
...    return "Info to show"

in this instance the route manager exposes the serial command "show" to this method.

>>> @serial_query
... def get_sn(self):
...     return self.sn
...
>>> @serial_query
... def set_sn(self,new_sn):
...     self.sn = new_sn
...     return "OK" # in general you always want serial queries to respond with some data

in the above example we expose 2 new routes, we expose "get sn" which accepts no additional data, and also a "set sn" which expects one addition argument of the new serial number, it would be triggered with a command like "set sn SN123123"
this is effectively what happens with any variables defined in your :class:`serial_mock.Serial` subclass' :attr:`data <serial_mock.Serial.data>` attribute

you could also accept multiple arguments

>>> @serial_query
... def set_usercal(self,offset,slope=0)
...     return "OK"

in this example this method would be invoced with "set usercal 4" or "set usercal 4 6", allowing you to optionally pass in a second variable, you could of coarse require the second variable or 3 variables, etc.

explicitly declared routes
__________________________

perhaps you are emulating a device that has commands that are not part of legal function names in python, consider something like "#00x53"

>>> @serial_query("#00x53")
... def show_info():
...     return "blah i am info"

in this example the user can pass "#00x53" to the serial port and it will trigger this method., anything that follows will be split on spaces and passed in as arguments

complex routes
______________

you can also pass in a compiled regex to match against ... any groups will be passed as arguments to function that is bound to this trigger

>>> @serial_query(re.compile("(.*)"))
... def echo_function(self,user_msg):
        return user_msg

this is a regex that will match anything and pass it into this function, of coarse you can use much more complex regular expressions, though you rarely need to.

Examples
--------
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


serial_mock `bind_key_down` Decorator
=====================================

the :code:`@bind_key_down` decorator allows you to bind a function to a keypress, this can be usefull to perform sporatic actions (like incrementing an id)

.. code-block:: python

    class MyInterface(SerialMock):
         current_id = 1
         @serial_query("get -record_id")
         def get_id(self):
             return "%s"%self.current_id

         @bind_key_down("a")
         def increment_id(self):
             self.current_id += 1

in this example when the user presses 'a' the current_id attribute will increase by one. and the next time "get -record_id" is invoked the new current_id is returned to the client.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`