# -*- coding: cp1252 -*-
#USB CDC testing and developing


import serial
import struct

class Spiro(object):
    def __init__(self, port="COM2", timeout=0.5):
        self.ser = serial.Serial(port=port, timeout=timeout)
    #def get_sample(self):
    #    self.ser.write("0")
    #    blk = self.ser.read(3)
    #    sample = struct.unpack("H", blk[1:])[0]
    #    return sample
    #def get_bulk(self, n_samples):
    #    return [self.get_sample() for x in range(n_samples)]
    def get_100_samples(self):
        blk = self.ser.read(100)
        samples = struct.unpack("H"*(len(blk)/2), blk)
        return samples
    def get_sample(self):
        blk = self.ser.read(2)
        samples = struct.unpack("H"*(len(blk)/2), blk)
        return samples
    def get_remaining_samples(self):
        blk = self.ser.read(1)
        blk += self.ser.read(self.ser.inWaiting())
        samples = struct.unpack("H"*(len(blk)/2), blk)
        return samples
    def run(self):
        self.ser.write("1")
    def stop(self):
        self.ser.write("0")    
    def close(self):
        self.stop()
        self.ser.close()
    def __del__(self):
        self.stop()
        self.ser.close()

