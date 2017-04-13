"""
fake_serial.Serial provides our interface to our fake serial (suprise!).

note that **data** is a special attribute and any keys passed into it will automatically have getters and setters provided for it
"""
import random
import threading
import traceback

import serial
import re
import time

import sys

from serial_mock.decorators import QueryStore
from serial_mock.kb_listen import KBListen
import logging
logging.basicConfig(stream=sys.stdout,format="%(levelname)s:%(funcName)s %(lineno)d:  %(message)s")
logger = logging.getLogger("serial_mock")




class Serial(object):
    """
    >>> Serial("COM99").MainLoop() # run forever on COM99
    
    
    """
    _hard_exit = False
    _LOCK = threading.Lock()
    #: any keys defined in **data** will automatically have getters or setters created for them
    data = {}
    #: the prefix to use with data auto generated routes
    data_prefix="-"
    #: the **baudrate** we should operate at
    baudrate=9600
    #: the **prompt** to display to the user
    prompt=">"
    #: **user_terminal** defines the character(or characters, or regexp, or list) of items that indicate our user has finished a command
    delimiter="\r"
    #:**endline** defines the character to output after our response but before our prompt
    endline="\r"

    logfile = None



    def __init__(self,stream,logfile=None,**kwargs):
        """
            **Serial(stream:string)** instanciates a new MockStreamTunnel, stream should point to the comm port to listen on. 
            *in general this class should not be directly invoked but should be subclassed, you can find some examples in the examples folder, or in the cli.py file*

            :param stream: a path to a pipe (ie "/dev/ttyS99","COM11")
            
           
        """
        QueryStore.target = self
        self.kb = None
            #keyboard.Listener(self._process_keydown).start()
        super(Serial,self).__init__()
        for key in "data_prefix baudrate prompt delimiter endline".split():
            if key in kwargs:
                setattr(self,key,kwargs.pop(key))

        self.stream = None
        if logfile:
            self.logfile = open(logfile,"wb")
        if isinstance(stream,basestring):
            try:
                self.stream = serial.Serial(stream,self.baudrate)
            except:
                raise Exception("Unable To Bind To %r"%stream)
        for k in self.data:
            QueryStore.register(lambda self,k=k:self.data.get(k,"None"),"get -%s"%k)
            QueryStore.register(lambda self,value,k=k:self.data.update({k:value}) or "OK","set -%s"%k)

        assert hasattr(self.stream,"read") and hasattr(self.stream,"write"),"STREAM must provide a minimum of read and write"
    @staticmethod
    def _read_from_stream(stream,terminal):
        def check_term(s,check_item):
            if isinstance(check_item,basestring):
                return s.endswith(check_item)
            elif isinstance(check_item,re._pattern_type):
                return check_item.match(s)
            elif isinstance(check_item,(list,tuple)):
                return any(check_term(s,itm) for itm in check_item)
            else:
                raise Exception("Unknown Terminal Condition:%r"%check_item)

        def my_iter():
            s = ""
            while True:
                if stream.inWaiting():
                    Serial._LOCK.acquire()
                    try:
                        s += stream.read(stream.inWaiting())
                        if check_term(s,terminal):
                            logger.debug("Response Complete(%s): %r (returning value)" % (stream.port, s))
                            return s

                        logger.debug("Incomplete MSG(%s)(%r not found): %r (keep waiting)"%(stream.port,terminal,s))

                    finally:
                        Serial._LOCK.release()
                else:
                    if Serial._hard_exit:
                        sys.exit(0)
                    time.sleep(0.25)

        return my_iter()


    def _process_cmd(self,cmd):
        cmd = re.sub(".\x08","",cmd.strip())
        if self.logfile:
            self.logfile.write("<%r\n"%(cmd,))
        if not cmd:
            return ""
        try:
            method,rest = QueryStore._find(cmd)

        except KeyError:
            traceback.print_exc()
            return "ERROR %r Not Found"%cmd
        try:
            logger.debug("calling function: %r"%method.__name__)
            result = method(self,*rest)
            logger.debug("%s returns: %r"%(method.__name__,result))
            return result
        except:
            traceback.print_exc()
            return "ERROR %r"%cmd
    def _process_keydown(self,key):
        result =  QueryStore._find_key_binding(key)
        if not result:
            return
        result(self)
    def _write_to_stream(self,response):
        if not response:return
        if self.logfile:
            self.logfile.write(">%r\n"%(response,))
        self._LOCK.acquire()
        try:
            self.stream.write("%s%s"%(response,self.endline))
        finally:
            self._LOCK.release()

    def MainLoop(self):
        """
        Mainloop will run forever serving the rules provided in the subclass to the bound pipe
        
        """
        if QueryStore.__keybinds__:
            self.kb = KBListen(self._process_keydown)
            self.kb.Listen()
        print "LISTENING ON:",self.stream
        while True:
            self.stream.write(self.prompt)
            try:
                cmd = self._process_cmd(self._read_from_stream(self.stream,self.delimiter))
            except:
                self.kb.halt = True
                return
            self._write_to_stream(cmd)


class EmittingSerial(Serial):
    emit = "EMIT MSG"
    delay = 5,35
    interval = 15,35
    def _on_start_emit(self):
        threading.Timer(random.uniform(*self.interval),self._on_emit).start()
    def _on_emit(self):
        self._write_to_stream(self.emit)
        self._on_start_emit()
    def MainLoop(self):
        print "MainLoop"
        threading.Timer(random.uniform(*self.delay), self._on_start_emit).start()
        Serial.MainLoop(self)



