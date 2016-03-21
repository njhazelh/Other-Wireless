#! /usr/bin/env python

import SocketServer
import struct

SERVER_PORT = 1234


class TCPTempHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            print struct.unpack("fffff", data)


def main():
    server = SocketServer.TCPServer(("", SERVER_PORT), TCPTempHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
