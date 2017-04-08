"""
fake_serial.Serial provides our interface to our fake serial (suprise!)
"""
import random
import threading
import traceback

import serial
import re
import time
from serial_mock.decorators import serial_query as SerialQuery, QueryStore


class Serial(object):
    """
    >>> Serial("COM99").MainLoop() # run forever on COM99
    
    
    """
    _LOCK = threading.Lock()
    #: the **baudrate** we should operate at
    baudrate=9600
    #: the **prompt** to display to the user
    prompt=">"
    #: **user_terminal** defines the character(or characters, or regexp, or list) of items that indicate our user has finished a command
    user_terminal="\r"
    #:**endline** defines the character to output after our response but before our prompt
    endline="\r"
    #:any keys defined in **data** will automatically have getters or setters created for them
    data = {}

    def __init__(self,stream):
        """
            **Serial(stream:string)** instanciates a new MockStreamTunnel, stream should point to the comm port to listen on. 
            *in general this class should not be directly invoked but should be subclassed*

            :param stream: a path to a pipe (ie "/dev/ttyS99","COM11")
            
            .. seealso:: examples
        """
        super(Serial,self).__init__()
        self.stream = None
        if isinstance(stream,basestring):
            try:
                self.stream = serial.Serial(stream,self.baudrate)
            except:
                raise Exception("Unable To Bind To %r"%stream)
        for k in self.data:
            QueryStore.register(lambda self,k=k:self.data.get(k,"None"),"get -%s"%k)
            QueryStore.register(lambda self,value,k=k:self.data.update({k:value}) or "OK","set -%s"%k)

        assert hasattr(self.stream,"read") and hasattr(self.stream,"write"),"STREAM must provide a minimum of read and write"
    def _read_from_stream(self):
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
                if self.stream.inWaiting():
                    self._LOCK.acquire()
                    try:
                        s += self.stream.read(self.stream.inWaiting())
                        if check_term(s,self.user_terminal):
                            return s
                    finally:
                        self._LOCK.release()
                else:
                    time.sleep(0.25)
        return my_iter()


    def _process_cmd(self,cmd):
        cmd = re.sub(".\x08","",cmd.strip())
        if not cmd:
            return ""
        try:
            method,rest = QueryStore.find(cmd)

        except KeyError:
            return "ERROR %r Not Found"%cmd
        try:
            return method(self,*rest)
        except:
            traceback.print_exc()
            return "ERROR %r"%cmd
    def _write_to_stream(self,response):
        if not response:return
        self._LOCK.acquire()
        try:
            self.stream.write("%s%s"%(response,self.endline))
        finally:
            self._LOCK.release()

    def MainLoop(self):
        """
        Mainloop will run forever serving the rules provided in the subclass to the bound pipe
        
        """
        while True:
            self.stream.write(self.prompt)
            cmd = self._process_cmd(self._read_from_stream())
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
if __name__ == "__main__":
    s = EmitingSerial("COM106")
    s.MainLoop()