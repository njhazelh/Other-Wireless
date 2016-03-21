#! /usr/bin/env python

import serial
import time

s = serial.Serial("/dev/ttyS0", 57600)


def main():
    while True:
        s.write("1")
        time.sleep(1)
        s.write("0")
        time.sleep(1)

if __name__ == "__main__":
    main()
