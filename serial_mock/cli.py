import re

import sys

from mock import Serial
from decorators import serial_query


class EchoSerial(Serial):
    """
    simple example client
    """
    @serial_query(re.compile("(.*)"))
    def echo(self,what):
        return what

if __name__ == "__main__":
    EchoSerial(sys.argv[1]).MainLoop()