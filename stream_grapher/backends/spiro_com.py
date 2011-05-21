# -*- coding: cp1252 -*-
#USB CDC testing and developing

import serial
import struct
from backend import Backend

class Spiro(Backend):
    def __init__(self, port="COM2", timeout=0.5):
        self.ser = serial.Serial(port=port, timeout=timeout)

    def get_remaining_samples(self):
        blk = self.ser.read(1)
        blk += self.ser.read(self.ser.inWaiting())
        samples = struct.unpack("H"*(len(blk)/2), blk)
        return samples

    def run(self):
        self.ser.write("1")

    def stop(self):
        self.ser.write("0")
        self.ser.close()


