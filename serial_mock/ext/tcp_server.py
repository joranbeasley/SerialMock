import SocketServer
import socket

from serial_mock.aq1_mock import AQ1Base

def setup():
    print "SETUP tcp_server"

class TCPStreamHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def setup(self):
        print "OK SETTING UP",self
        self.instance=AQ1Base(self)

    def read(self,n_bytes=1):

        result = self.request.recv(n_bytes)
        if result == "":
            raise Exception("Disconnect!")

        return result
    def close(self):
        self.request._sock.close()
    def write(self,msg):
        self.request.sendall(msg)

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.instance.MainLoop()





if __name__ == "__main__":
    HOST, PORT = "localhost", 9999


    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), TCPStreamHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()