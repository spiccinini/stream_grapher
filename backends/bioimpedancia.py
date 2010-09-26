# -*- coding: UTF-8 -*-

#import serial
import random
from itertools import izip
from backend import Backend

def grouper(n, iterable):
    "grouper(3, 'ABCDEFG') --> 'ABC' 'DEF'"
    args = [iter(iterable)] * n
    return ["".join(x) for x in izip(*args)]

class Bioimpedancia(Backend):
    PACKET_LENGTH = 16
    DATA_LENGTH = PACKET_LENGTH * 4

    def __init__(self, port="COM1", timeout=0.1):
        Backend.__init__(self, ports=16, sample_rate=10) # Unknown sample_rate
        #self.ser = serial.Serial(port=port, timeout=timeout)
        #self.ser.flushInput()
        self._buffer = ""
        self.f = open("backends/biompedancia_1.log", "r")

    def get_remaining_samples(self):
        import time
        time.sleep(random.random()/5.)
        leido = self.f.read(random.randint(1,100))
        #leido += self.ser.read(self.ser.inWaiting())
        #self.f.write(leido)
        self._buffer += leido
        
        sobrantes = len(self._buffer) % Bioimpedancia.DATA_LENGTH
        data = grouper(Bioimpedancia.DATA_LENGTH, self._buffer)
        self._buffer = self._buffer[-sobrantes:]
        samples = [[]]*16 # 16 canales, 4 frecuencias por 4 mediciones.
        for meta_packet in data:
            packets = grouper(Bioimpedancia.PACKET_LENGTH, meta_packet)
            print packets
            for i, packet in enumerate(packets):
                decod = [int(x.encode("hex"),16) for x in packet[1:9]]
                samples[4*i+0].append(decod[0]*256+decod[1])
                samples[4*i+1].append(decod[2]*256+decod[3])
                samples[4*i+2].append(decod[4]*256+decod[5])
                samples[4*i+3].append(decod[6]*256+decod[7])
        
        return samples

    def close(self):
        self.stop()
        self.ser.close()

    def __del__(self):
        self.stop()
        self.ser.close()
