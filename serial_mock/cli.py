import re

import sys
import threading
import traceback

from serial_mock import MockSerial,serial_query

import serial

from serial_mock.util import convertBridgeFileToInterface
import logging
log = logging.getLogger("serial_mock")

class EchoSerial(MockSerial):
    """
    simple example client
    """
    @serial_query(re.compile("(.*)"))
    def echo(self,what):
        log.debug("echo back:%r"%what)
        return what

class BridgeSerial(object):
    prompt = ""
    fLock = threading.Lock()
    def __init__(self,port1,port2,logfile,delimiter="\r",endline=">"):
        super(BridgeSerial,self).__init__()
        self.logfile = open(logfile,"wb",buffering=0)
        self.delimiter=delimiter
        self.endline = endline
        self.target = serial.Serial(port1)
        self.bridge = serial.Serial(port2)
    def safe_log(self,msg):
        print msg
        if self.logfile:
            self.fLock.acquire()
            try:
                self.logfile.write(msg)
            finally:
                self.fLock.release()
    def MainLoop2(self):
        while True:
            result = MockSerial._read_from_stream(self.bridge, self.endline)
            log.info("Forward(%s->%s):%r" % (self.bridge.port,self.target.port,result))
            self.safe_log(">%r\n" % result)
            self.target.write(result)

    def MainLoop(self):
        print "Forwarding %r->%r"%(self.target.port,self.bridge.port)
        th = threading.Thread(target=self.MainLoop2)
        th.start()
        while True:
            try:
                result = MockSerial._read_from_stream(self.target, self.delimiter)
                log.info("Forward(%s->%s):%r" % (self.target.port, self.bridge.port, result))
                self.safe_log("<%r\n" % result)
                self.bridge.write(result)
            except:
                traceback.print_exc()
                MockSerial._hard_exit = True
                th.join()
                break



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="sub-command help")

    g1 = subparsers.add_parser("echo",help="bind to a port and just echo back anything it gets ... with a prompt")
    g1.set_defaults(which="g1")
    g1.add_argument("COM1",help='the comport to bind to')

    g2 = subparsers.add_parser("bridge",help="create a bridge between two ports, this is useful for generating a logfile")
    g2.set_defaults(which="g2")
    g2.add_argument("COM1",help='the first comport to bind to')
    g2.add_argument("COM2",help='the port to bridge to')
    g2.add_argument("-d","--delimiter",help="the command delimiter for reads",default="\r")
    g2.add_argument("-e","--endline",help="the command delimiter for responses",default=">")
    g2.add_argument("-L",'--logfile',help='this will log all incomming and outgoing messages, this can be used with the build subcommand')
    g3 = subparsers.add_parser("build",help="build a serialport emulator from a logfile generated from the bridge utility")
    g2.set_defaults(which="g3")
    g3.add_argument("bridge_file",help="a logfile generated from the --bridge_to utility. this must be generated with the bridge logfile utility",type=file)
    g3.add_argument("--out",help="the output file to generate, defaults to stdout",default=sys.stdout)
    parser.add_argument("-v","--verbose",help="verbose mode enabled",choices=["ERROR","WARN","DEBUG","INFO"],nargs="?")
    args = parser.parse_args()
    if args.verbose:
        print "SET LOG LEVEL:",args.verbose
        log.setLevel(getattr(logging,args.verbose))
    if "COM1" in args and "COM2" in args:
        interface = BridgeSerial(args.COM1, args.COM2, logfile=args.logfile, delimiter=args.delimiter, endline=args.endline).MainLoop()
    elif "COM1" in args:
        interface=EchoSerial(args.COM1).MainLoop()
    elif "bridge_file" in args:
        convertBridgeFileToInterface(args.bridge_file,args.out)




    #
    # if args.bridge_to:
    #     BridgeSerial(args.COM,args.bridge_to,args.logfile,args.delimiter,args.endline).MainLoop()
    # else:
    #     EchoSerial(args.COM).MainLoop()
