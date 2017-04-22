SerialMock
==========

[![Build Status](https://travis-ci.org/joranbeasley/SerialMock.svg?branch=master)](https://travis-ci.org/joranbeasley/SerialMock)

[READ THE DOCS](http://serialmock.rtfd.org)
--------------------------------------------

A library to mock serial ports... designed with developers in mind.

In order to create a mock serial port you must know enough about its protocol to replicate it to some extent

```python
import sys
from serial_mock import Serial,serial_query

class MyRS232Device(Serial):
     #this will provide interfaces "get offset","set offset <value>"
     data = {"offset":0.5}
     current_reading = 3.1
     @serial_query
     def get_reading(self,output="mV"):
        """
        this provices a serial interface for "get reading\r" or "get reading pH\r"
        it will return the current_reading+offset
        :param str output: one of "mV" or "pH" or None
        """
        return self.current_reading + float(self.offset)
if __name__ == "__main__":
    # pass in "COM99" or something on the command line
    MyRS232Device(sys.argv[1]).MainLoop()
     
```