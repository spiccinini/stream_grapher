# -*- coding: UTF-8 -*-

import serial
from itertools import izip

def grouper(n, iterable):
    "grouper(3, 'ABCDEFG') --> 'ABC' 'DEF'"
    args = [iter(iterable)] * n
    return ["".join(x) for x in izip(*args)]

class Bioimpedancia(object):
    PACKET_LENGTH = 16
    DATA_LENGTH = PACKET_LENGTH * 4

    def __init__(self, port="COM2", timeout=0.5):
        self.ser = serial.Serial(port=port, timeout=timeout)
        self._buffer = ""

    def get_remaining_samples(self):
        self._buffer += self.ser.read(1)
        self._buffer += self.ser.read(self.ser.inWaiting())

        sobrantes = len(self._buffer) % DATA_LENGTH
        data = grouper(DATA_LENGTH, self._buffer)
        self._buffer = self._buffer[-sobrantes:]
        samples = [[]]*16 # 16 canales, 4 frecuencias por 4 mediciones.
        for meta_packet in data:
            packets = grouper(PACKET_LENGTH, meta_packet)
            for i, packet in enumerate(packets):
                decod = [int(x.encode("hex"),16) for x in packet[:9]]
                samples[4*i+0].append(decod[1]*256+decod[2])
                samples[4*i+1].append(decod[3]*256+decod[4])
                samples[4*i+2].append(decod[5]*256+decod[6])
                samples[4*i+3].append(decod[7]*256+decod[8])
        return samples

    def close(self):
        self.stop()
        self.ser.close()

    def __del__(self):
        self.stop()
        self.ser.close()
