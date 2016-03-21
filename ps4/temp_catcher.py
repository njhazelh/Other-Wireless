#! /usr/bin/env python

import serial
import time
import argparse
import socket
import struct

s = serial.Serial("/dev/ttyS0", 57600)


def parseLine(line):
    parts = line.strip().split("\t")
    if len(parts) != 5:
        raise RuntimeError("empty line %s" % line)
    parts = [float(p) for p in parts]
    return parts


def pack_parts(parts):
    return struct.pack("fffff", *parts)


def main(server_address, server_port):
    print "Opening connection to %s on port %d" % (server_address, server_port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((server_address, server_port))
    print "Connection established"
    try:
        while True:
            line = s.readline()
            try:
                parts = parseLine(line)
            except RuntimeError as e:
                print e
                continue
            print parts
            server.sendall(pack_parts(parts))
    except KeyboardInterrupt:
        pass
    finally:
        print "\rClosing connection to %s:%d" % (server_address, server_port)
        server.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get data from Microcontroller and send to server")
    parser.add_argument("server_address", help="The ip/domain of the server")
    parser.add_argument("server_port", type=int,
                        help="The TCP port of the server")
    args = parser.parse_args()
    main(args.server_address, args.server_port)
