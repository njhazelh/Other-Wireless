#! /usr/bin/env python

from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler
import struct
from datetime import datetime
import ssl

SERVER_HOST = ""
SERVER_PORT = 1234

output_tmpl = "Time: %s" +\
    "\tHumidity: %.2f%%" +\
    "\tTemperature: %.2f*C %.2f*F" +\
    "\tHeat index: %.2f*C %.2f*F"


def print_datapoint(parts):
    t = datetime.fromtimestamp(parts[0])
    humid = parts[1]
    temp_c = parts[2]
    temp_f = parts[3]
    heat_c = parts[4]
    heat_f = parts[5]
    print output_tmpl % (t, humid, temp_c, temp_f, heat_c, heat_f)


class SSL_TCPServer(TCPServer):
    """
    Adds SSL to the SocketServer.  Based on response by WarriorPaw in
    http://stackoverflow.com/questions/8582766/adding-ssl-support-to-socketserver
    """
    def __init__(self,
                 server_address,
                 RequestHandlerClass,
                 certfile,
                 keyfile,
                 bind_and_activate=True):
        TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.certfile = certfile
        self.keyfile = keyfile

    def get_request(self):
        newsocket, fromaddr = self.socket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile=self.certfile,
                                     keyfile=self.keyfile)
        return connstream, fromaddr

class SSL_ThreadingTCPServer(ThreadingMixIn, SSL_TCPServer): pass

class TempHandler(StreamRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(48)
            if not data:
                break
            parts = struct.unpack("dddddd", data)
            print_datapoint(parts)


def main():
    server = SSL_ThreadingTCPServer((SERVER_HOST, SERVER_PORT),
                                    TempHandler,
                                    "server.cert",
                                    "server.key")
    server.serve_forever()


if __name__ == "__main__":
    main()
