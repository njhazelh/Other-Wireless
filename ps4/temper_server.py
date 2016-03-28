#! /usr/bin/env python

import SocketServer
import struct
from datetime import datetime

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


class TCPTempHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(48)
            if not data:
                break
            parts = struct.unpack("dddddd", data)
            print_datapoint(parts)


def main():
    server = SocketServer.TCPServer(("", SERVER_PORT), TCPTempHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
