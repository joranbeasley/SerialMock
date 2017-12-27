import time
import argparse

from flask import Flask, request
import serial_mock
from serial_mock import serial_query
import logging
import threading

logger = logging.getLogger("serial_mock")

def xor_decrypts(strInput,XORKey="Does the name Pavlov ring a bell"):
    strOutput = ""
    cryptIndex = 0
    for i in range(len(strInput)):
        if ord(strInput[i]) > 0x20:
            strOutput = strOutput + chr((ord(strInput[i]) - 0x20) ^ ord(XORKey[cryptIndex&0x1F]))
            cryptIndex += 1
        else:
            strOutput = strOutput + strInput[i]
    return strOutput

# Encrypt a string
def xor_encrypts(strInput,XORKey="Does the name Pavlov ring a bell"):
    strOutput = ""
    cryptIndex = 0
    for i in range(len(strInput)):
        if ord(strInput[i]) > 0x20:
            strOutput = strOutput + chr((ord(strInput[i]) ^ ord(XORKey[cryptIndex&0x1F])) + 0x20)
            cryptIndex += 1
        else:
            strOutput = strOutput + strInput[i]
    return strOutput

class AQ1Base(serial_mock.MockSerial):
    prompt = '>'
    endline = '\r'
    terminal = '\r'
    _status = "Idle"
    _scan = '\x89~ tb2f\x7fr2 \x7fycp6\x88 pab\x7f`5 fy{r2 w6ls}}\x92'
    _timers = {}
    _reading_started = 0
    # for simple playback simple queries work well
    simple_queries = {
        'show': 'AQ1 0.00.5901 AQ1-0000004',
        'get -sn': 'AQ1-0000004',
        'get -ver': 'AQ1 0.00.5901',
        'get -usercal':'0.0000 0.00000'
    }

    @serial_query("scan 1")
    def get_scan(self):
        def get_reading(tSample=22.3, tLid=22.5, rhc=33659, aw=0.52):
            ctx = dict(tSample=tSample, tLid=tLid, rhc=rhc, aw=aw, elapsed=int(time.time() - self._reading_started))
            return "1 {elapsed} {tSample:0.1f} {tLid:0.1f} {rhc} {aw:0.4f}".format(**ctx)


        result = xor_encrypts({
            "Idle": "-1 0 22.3 23.1 99999 0.452",
            "Blinking": "-1 0 22.3 23.1 99999 0.452",
            "Reading": get_reading(),
            "Finished": "-1 %s 22.3 23.1 33789 0.5102"%self._reading_started,

        }.get(self._status))
        print repr(result), " => ", repr(xor_decrypts(result))
        return result

    @serial_query("get -status")
    def get_status(self):
        if self._status == "Blinking" and time.time() - self._reading_started > 10:
            self._status = "Reading"
            self._reading_started = time.time()
        elif self._status == "Reading" and time.time() - self._reading_started > 30:
            self._status = "Finished"
            self._reading_started = time.time() - self._reading_started
        return self._status
    @serial_query
    def reset(self):
        self._status = "Idle"

    @serial_query
    def start(self,now=False):
        self.reset()
        self._status = "Blinking"
        self._reading_started = time.time()
        return "OK"

    @serial_query("get -mockver")
    def get_mock_ver(self):
        '''
        just included as a sample to get you going
        '''
        return "RUNNING serial_mock %s" % serial_mock.__VERSION__

    def say(self,what):
        self._write_to_stream(what)
        return "OK will do!"
app = Flask(__name__)
if __name__ == "__main__":
    # global device
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("COM_PORT", help="the com port to bind this class to")
    parser.add_argument("-v", "--verbose", help="verbose mode enabled", choices=["ERROR", "WARN", "DEBUG", "INFO"],
                        nargs="?")
    args = parser.parse_args()
    if args.verbose:
        print "SET LOG LEVEL:", args.verbose
        logger.setLevel(getattr(logging, args.verbose, logging.WARN))
    # print threading.current_thread().getName()
    device = AQ1Base(args.COM_PORT)
    device.MainLoop()
    