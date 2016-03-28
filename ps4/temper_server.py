#! /usr/bin/env python

import SocketServer
import struct
from datetime import datetime

SERVER_PORT = 1234


class TCPTempHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(48)
            if not data:
                break
            parts = struct.unpack("dddddd", data)
            time, parts = parts[0], parts[1:]
            print datetime.fromtimestamp(time), parts


def main():
    server = SocketServer.TCPServer(("", SERVER_PORT), TCPTempHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
