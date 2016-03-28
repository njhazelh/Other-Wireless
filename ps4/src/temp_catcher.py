#! /usr/bin/env python

import serial
import time
import argparse
import socket
import ssl
import struct
from datetime import datetime

s = serial.Serial("/dev/ttyS0", 57600)

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


def parseLine(line):
    parts = line.strip().split("\t")
    if len(parts) != 5:
        raise RuntimeError("empty line %s" % line)
    parts = [float(p) for p in parts]
    return parts


def pack_parts(parts):
    return struct.pack("dddddd", *parts)


def get_connection(server_address, server_port):
    print "Opening connection to %s on port %d" % (server_address, server_port)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(conn,
                           ca_certs="server.cert",
                           cert_reqs=ssl.CERT_REQUIRED)
    conn.connect((server_address, server_port))
    print "Connection established"
    return conn


def main(server_address, server_port):
    conn = get_connection(server_address, server_port)
    try:
        while True:
            line = s.readline()
            try:
                t = time.mktime(time.localtime())
                parts = [t] + parseLine(line)
                print_datapoint(parts)
                conn.sendall(pack_parts(parts))
            except socket.error as e:
                print e
                conn.close()
                conn = get_connection(server_address, server_port)
            except RuntimeError as e:
                print e
    except KeyboardInterrupt:
        pass
    finally:
        print "\rClosing connection to %s:%d" % (server_address, server_port)
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get data from Microcontroller and send to server")
    parser.add_argument("server_address", help="The ip/domain of the server")
    parser.add_argument("server_port", type=int,
                        help="The TCP port of the server")
    args = parser.parse_args()
    main(args.server_address, args.server_port)
