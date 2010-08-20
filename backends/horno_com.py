# -*- coding: utf-8 -*-
# Comunicación con la placa controladora del horno SMD
# http://redmine.clubderobotica.com.ar

import serial
import struct
from backend import Backend
from scipy import interpolate
from numpy import array
from k_adj_arrays import mv, T

BAUDRATE = 38400
PORT = '/dev/ttyUSB0'

class Horno(Backend):
    def __init__(self, ports, sample_rate, serial_port=PORT,
                 baudrate = BAUDRATE, timeout = 0.5):
        Backend.__init__(self, ports, sample_rate=sample_rate)

        self.ser = serial.Serial(port=serial_port, baudrate=baudrate,
                                 timeout=timeout)

        self._corr_termocupla = interpolate.interp1d(mv, T)

    #FIXME ver get_remaining...
    def get_100_samples(self):
        blk = self.ser.read(600)
        samples = struct.unpack("<H"*(len(blk)/2), blk)
        samples = [samples[0::3], samples[1::3], samples[2::3]]
        return samples[:2]

    #FIXME ver get_remaining...
    def get_sample(self):
        blk = self.ser.read(6)
        samples = [samples[0::3], samples[1::3], samples[2::3]]
        samples = struct.unpack("<H"*(len(blk)/2), blk)
        samples = [samples[0::3], samples[1::3], samples[2::3]]
        return samples[:2]

    def get_remaining_samples(self):

        # Es necesario leer 1 byte antes de usar inWaiting()
        blk = self.ser.read(1)
        # Los datos llegan en bloques de 6 bytes. La división que se hace es
        # entera
        blocks_to_read = self.ser.inWaiting() / 6
        bytes_to_read = blocks_to_read * 6 - 1
        blk += self.ser.read(bytes_to_read)

        if len(blk) == 0:
            return array([])

        samples = array(struct.unpack("<" + "H"*(len(blk)/2), blk)).reshape((3,-1))
        sensor, terms = samples[:,0], samples[:,(1,2)]

        #convirtiendo a temperatura
        sensor = senor * .065

        # 2.5v referencia AD de 10 bits, 151.85 A_v del Amplificador
        # x1000 para tenerlo en mV
        terms = terms * (2.5 / 1<<10) / 151.85 * 1000
        terms = self._corr_termocupla(terms)

        return terms[:,0]

    # FIXME: La nueva version tiene comandos de empezar/terminar
    def run(self):
        pass #self.ser.write("1")

    def stop(self):
        pass #self.ser.write("0")

    def close(self):
        self.stop()
        self.ser.close()

    def __del__(self):
        self.stop()
        self.ser.close()
