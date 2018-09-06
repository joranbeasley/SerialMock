"""
fake_serial.Serial provides our interface to our fake serial (suprise!).

note that **data** is a special attribute and any keys passed into it will automatically have getters and setters provided for it
"""
import random
import threading
import traceback

from itertools import cycle

import serial
import re
import time

import sys
try:
    from cStringIO import StringIO
except:
    from io import StringIO

if int(sys.version[0]) >= 3:
    basestring=(str,bytes)

from serial_mock.decorators import QueryStore
from serial_mock.kb_listen import KBListen
import logging
logging.basicConfig(stream=sys.stdout,format="%(levelname)s:%(funcName)s %(lineno)d:  %(message)s")
logger = logging.getLogger("serial_mock")


class _StreamHelper(object):
    _exit = False
    @staticmethod
    def check_term(s, check_item):
        r"""
        >>> _StreamHelper.check_term("asdasdaQ","Q")
        True
        >>> _StreamHelper.check_term("asdasdaQ","\r")
        False
        >>> import re
        >>> _StreamHelper.check_term("asdasdaQ",re.compile("[a-z]([A-Z].*)"))
        True
        >>> _StreamHelper.check_term("asdasdaQ",re.compile("[0-9]([A-Z].*)"))
        False
        >>> _StreamHelper.check_term("asdasdaQ",['q','Q'])
        True
        >>> _StreamHelper.check_term("asdasdaQ",['q','Z'])
        False
        >>> try: _StreamHelper.check_term("asdasdaQ",True)
        ... except Exception as e: print e
        ...
        Unknown Terminal Condition:True
        
        :param s: the string so far to check 
        :param check_item: the condition
        :return: True or False depending on if the condition is met
        
        """
        if isinstance(check_item, basestring):
            return s.endswith(check_item)
        elif isinstance(check_item, re._pattern_type):
            return bool(check_item.search(s))
        elif isinstance(check_item, (list, tuple)):
            return any(_StreamHelper.check_term(s, itm) for itm in check_item)
        else:
            raise Exception("Unknown Terminal Condition:%r" % check_item)
    @staticmethod
    def read_until(stream, terminal_condition):
        r"""
        reads a stream until a terminal condition is met 
        
        >>> s = StringIO("Hello World\rBob")
        >>> _StreamHelper.read_until(s,"\r")
        'Hello World\r'
        >>> s.seek(0)
        >>> import re
        >>> _StreamHelper.read_until(s,re.compile("\s[A-C]"))
        'Hello World\rB'
        >>> s.seek(0)
        >>> _StreamHelper.read_until(s,re.compile("\s[C-Z]"))
        'Hello W'
        
        :param stream: 
        :param terminal_condition: 
        :return: 
        """
        s = ""
        _StreamHelper._exit=False
        while not _StreamHelper._exit:

            if s and _StreamHelper.check_term(s, terminal_condition):
                logger.debug("Response Complete(%s): %r (returning value)" % (getattr(stream, 'port', stream), s))
                return s
            elif s:
                logger.debug("Incomplete MSG(%s)(%r not found): %r (keep waiting)" % (getattr(stream, "port", stream), terminal_condition, s))
            if not hasattr(stream,"inWaiting") or stream.inWaiting():
                MockSerial._LOCK.acquire()
                try:
                    s += stream.read(1)
                    print("S:",s)
                finally:
                    MockSerial._LOCK.release()
            else:
                if MockSerial._hard_exit:
                    sys.exit(0)
                time.sleep(0.25)

class MockSerial(object):
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

    #: any key:value pair in simple queries is exposed as a simple query response ... and the query string must be an exact match
    #: value can be a string/unicode/bytes value or it can be a list or array, if a list or array is passed in then the responses will be cycled
    #: any other value type will be coerced to `str`
    simple_queries = {}


    def __init__(self,stream,logfile=None,**kwargs):
        """
            **MockSerial(stream:string)** instanciates a new MockStreamTunnel, stream should point to the comm port to listen on. 
            *in general this class should not be directly invoked but should be subclassed, you can find some examples in the examples folder, or in the cli.py file*

            :param stream: a path to a pipe (ie "/dev/ttyS99","COM11"), a stream like object, or "DEBUG"
            :param data_prefix: the separator between getters/setters and the data_attribute they reference            

            
            >>> from serial_mock.decorators import serial_query
            >>> from serial_mock.mock import MockSerial
            >>> class SimpleSerial(MockSerial):
            ...     simple_queries = {
            ...         "get -name":"hello my name is bob",
            ...         "get -next":["123","456","789"],
            ...         "get -id":12
            ...     }
            ...     data={"x":6}
            ...     @serial_query("trigger command")
            ...     def do_something(self,requiredArg,optionalArg="0"):
            ...         return "RESULT: %r %r"%(requiredArg,optionalArg)
            ...
            >>> mock = SimpleSerial("DEBUG")            
            >>> mock.process_cmd("trigger command 1")
            "RESULT: '1' '0'"
            >>> mock.process_cmd("trigger command 1 2")
            "RESULT: '1' '2'"
            >>> mock.process_cmd("get -name")
            'hello my name is bob'
            >>> mock.process_cmd("get -next")
            '123'
            >>> mock.process_cmd("get -next")
            '456'
            >>> mock.process_cmd("get -next")
            '789'
            >>> mock.process_cmd("get -next")
            '123'
            >>> mock.process_cmd("get -id")
            '12'
            >>> mock.process_cmd("get -x")
            '6'
            >>> mock.process_cmd('set -x 10')
            'OK'
            >>> mock.process_cmd("get -x")
            '10'
            
           
        """
        self.running = False
        self.kb = None
        QueryStore.target = self
        super(MockSerial, self).__init__()
        for key in "data_prefix baudrate prompt delimiter endline".split():
            if key in kwargs:
                setattr(self,key,kwargs.pop(key))
        self.stream = stream
        if logfile:
            if isinstance(logfile,basestring):
                logfile = open(logfile,"wb")
            self.logfile = logfile
        if isinstance(stream,basestring) and not stream == "DEBUG":
            try:
                self.stream = serial.Serial(stream,self.baudrate)
            except:
                raise Exception("Unable To Bind To %r"%stream)

        for k in self.data:
            QueryStore.register(lambda self,k=k:str(self.data.get(k,"None")),"get %s%s"%(self.data_prefix,k))
            QueryStore.register(lambda self,value,k=k:self.data.update({k:value}) or "OK","set %s%s"%(self.data_prefix,k))
        self._simple_queries = {}
        for k,v in self.simple_queries.items():
            if isinstance(v,basestring):
                self._simple_queries[k] = cycle([v,])
            elif isinstance(v,(list,tuple)):
                self._simple_queries[k] = cycle(v)
            else:
                self._simple_queries[k] = cycle([str(v), ])
        if not isinstance(self.endline,bytes):
            self.endline = self.endline.encode("latin1","replace")
        if not isinstance(self.prompt,bytes):
            self.prompt = self.prompt.encode("latin1","replace")

        if self.stream is "DEBUG":
            logger.warn("Running in debug mode you may not run MainLoop!")
        else:
            assert hasattr(self.stream,"read") and hasattr(self.stream,"write"),"STREAM must provide a minimum of read and write"
    @staticmethod
    def _read_from_stream(stream,terminal):
        return _StreamHelper.read_until(stream, terminal)


    def process_cmd(self, cmd):
        """
        looks up a command to see if its registered. and returns the result if it is otherwise returns an error string
        in general this command should not be invoked directly (but it can be...)
        
        >>> from serial_mock.mock import MockSerial
        >>> inst = MockSerial("DEBUG") 
        >>> inst.process_cmd("a")
        "ERROR 'a' Not Found"
                        
        :param cmd: the command to process  
        :return: a string (the result of the command)
        
        """

        cmd = re.sub(".\x08","",cmd.strip())
        if self.logfile:
            self.logfile.write("<%r\n"%(cmd,))
        if not cmd:
            return ""
        if cmd in self.simple_queries:
            result = next(self._simple_queries[cmd])
            logger.debug("Simple Query Response:%r -> %r"%(cmd,result))
            return result
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
        except Exception as e:
            traceback.print_exc()
            return "ERROR %r : %s"%(cmd,e)
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
        except:
            if self.stream == "DEBUG":
                print("%s%s"%(response,self.endline))
            else:
                raise
        finally:
            self._LOCK.release()
    def terminate(self):
        """
        stop the MainLoop if running
        :return: 
        """
        self.running = False
        try:
            self.stream.close()
        except:
            logger.warn("unable to close stream...skipping")
        if self.kb:
            self.kb.halt = True
        _StreamHelper._exit = True
        logger.debug("Terminate Flags set!")

    def MainLoop(self):
        """
        Mainloop will run forever serving the rules provided in the subclass to the bound pipe
        
        """

        assert self.stream != "DEBUG"
        self.running = True
        if QueryStore.__keybinds__:
            self.kb = KBListen(self._process_keydown)
            self.kb.Listen()
        print("LISTENING ON:",self.stream)

        while self.running:
            self.stream.write(self.prompt)
            try:
                cmd = self.process_cmd(self._read_from_stream(self.stream, self.delimiter))
            except:
                logger.info("Leaving MainLoop")
                return self.terminate()
            self._write_to_stream(cmd)
        self.terminate()
        logger.info("Leaving MainLoop")


class DummySerial(serial.Serial):
    r"""
    DummySerial provides a serial.Serial interface into a MockSerial instance. you can use this as a dropin replacement to serial.Serial, for anything that accepts serial.Serial as an argument
    
    >>> from serial_mock.mock import DummySerial,MockSerial
    >>> from serial_mock.decorators import serial_query
    >>> class MyInterface(MockSerial):
    ...     @serial_query("trigger command")
    ...     def do_something(self,requiredArg,optionalArg="0"):
    ...         return "RESULT: %r %r"%(requiredArg,optionalArg)
    ...
    >>> ser = DummySerial(MyInterface)
    >>> ser.write("trigger command 5\r")
    18L
    >>> ser.read(ser.inWaiting())    
    "RESULT: '5' '0'\r>"
    >>> ser.write("trigger command 1 2\r")
    20L
    >>> ser.read(ser.inWaiting())
    "RESULT: '1' '2'\r>"
    
    """

    is_open = True
    _port_handle = None
    _baudrate = "ANY"
    _bytesize = "ANY"
    _parity = "ANY"
    _stopbits = 1
    _timeout = None
    _xonxoff = None
    _rtscts = None
    _dsrdtr = None
    def __init__(self,MockSerialClass):
        self.myMock = MockSerialClass(StringIO())
        self.rx_buffer = ""
        self.tx_buffer = ""
        self.port = "MOC1"
        self.is_open = True

    def open(self):
        return True
    def close(self):
        return True
    @property
    def in_waiting(self):
        return self.inWaiting()

    def inWaiting(self):
        return len(self.tx_buffer)

    def write(self,msg):
        self.rx_buffer += msg
        if _StreamHelper.check_term(self.rx_buffer, self.rx_buffer):
            self.myMock._write_to_stream(self.myMock.process_cmd(self.rx_buffer))
            self.myMock.stream.seek(0)
            self.tx_buffer += self.myMock.stream.read() + self.myMock.prompt
            self.myMock.stream.truncate(0)
            self.rx_buffer = ""
        return long(len(msg))
    def read(self,bytes=1):
        resp,self.tx_buffer =self.tx_buffer[:bytes],self.tx_buffer[bytes:]
        return resp

class EmittingSerial(MockSerial):
    emit = "EMIT MSG"
    delay = 5,35
    interval = 15,35

    def __init__(self, stream, logfile=None, **kwargs):
        """
            **EmmitingSerial(stream:string)** provides a reference class on an interface that periodically emits a "heartbeat" type message 


            :param stream: a path to a pipe (ie "/dev/ttyS99","COM11"), a stream like object, or "DEBUG"
            :param data_prefix: the separator between getters/setters and the data_attribute they reference            

        """

        super(EmittingSerial, self).__init__(stream, logfile, **kwargs)

    def _on_start_emit(self):
        threading.Timer(random.uniform(*self.interval),self._on_emit).start()

    def _on_emit(self):
        self._write_to_stream(self.emit)
        self._on_start_emit()
    def MainLoop(self):
        threading.Timer(random.uniform(*self.delay), self._on_start_emit).start()
        MockSerial.MainLoop(self)


if __name__ == "__main__":
    class TestClass(MockSerial):
        @QueryStore("hello")
        def say_hello(self,name="BOB"):
            return "Hello, %s"%name

    d = DummySerial(TestClass)
    print(isinstance(d,serial.Serial),d)
    print("sent:",repr(d.write("hello joey\r")))
    print("RECV:",repr(d.read(d.inWaiting())))

