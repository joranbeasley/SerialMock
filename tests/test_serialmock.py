import unittest

import time


def getPortTunnelWindows():
    return "COM199 COM200".split()
def getPortTunnelLinux():
    return "COM99 COM100".split()
def getPortTunnel():
    import os
    if os.name == "nt":
        return getPortTunnelWindows()
    return getPortTunnelLinux()

class SerialMockBoundTestCase(unittest.TestCase):
    def setUp(self):
        import threading
        import serial
        import logging
        logging.getLogger("serial_mock").setLevel(logging.DEBUG)
        from serial_mock.mock import MockSerial
        from serial_mock.decorators import serial_query,bind_key_down
        self.ports = getPortTunnel()

        class MyInterface(MockSerial):
            simple_queries = {"get greeting":"Hello User",
                              "get next":["1","2"]}
            data = {"x":5}
            @bind_key_down("a")
            def increment_x(self):
                self.data["x"] = int(self.data['x'])+ 1
            @serial_query("less x")
            def decrement_x(self):
                self.data["x"] = int(self.data['x']) + 1
        self.dut = MyInterface(self.ports[0])
        self.ser = serial.Serial(self.ports[1],timeout=0.5)
        self.proc = threading.Thread(target=self.dut.MainLoop)
        self.proc.start()
    def tearDown(self):
        self.dut.terminate()
        self.proc.join()
        self.ser.close()


    def test_prompt(self):
        self.assertEquals(self.ser.read(1000),self.dut.prompt)
    def test_simpleQuery_STR(self):
        self.assertEquals(self.ser.read(1000), self.dut.prompt)
        self.ser.write("get greeting\r")
        self.assertEquals(self.ser.read(1000), self.dut.simple_queries["get greeting"]+self.dut.endline+self.dut.prompt)

    def test_simpleQuery_CYCLE(self):
        self.assertEquals(self.ser.read(1000), self.dut.prompt)
        for i in range(3):
            self.ser.write("get next\r")
            result = self.ser.read(1000)
            self.assertEquals(result,self.dut.simple_queries['get next'][i%2]+self.dut.endline+self.dut.prompt)
