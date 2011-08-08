# -*- coding: UTF-8 -*-

# Copyright (C) 2009, 2010  Santiago Piccinini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from backend import Backend
import threading
import Queue
import time
import math

class MathGenerator(object):
    def __init__(self, freq, sample_rate):
        self.freq = freq
        self.sample_rate = sample_rate
        self.t = 0
        self.samples = []

    def get_samples(self, n):
        while len(self.samples) < n:
            self.gen_samples()
        samples = self.samples[:n]
        self.samples = self.samples[n:]
        return samples

    def gen_samples(self):
        raise NotImplementedError

class CubicGenerator(MathGenerator):

    def gen_samples(self):
        self.samples.extend([t**3/4.0 for t in range(-10, 10)])

class SineGenerator(MathGenerator):

    def get_samples(self, n):
        samples = []
        for i in range(n):
            samples.append(math.sin(2*3.14* self.freq * self.t))
            self.t += 1/float(self.sample_rate)
        return samples



class Math(Backend):

    generator = None

    def __init__(self, ports, freq, sample_rate):
        Backend.__init__(self, ports, sample_rate=sample_rate)
        self.generators = [self.generator(freq, sample_rate) for x in range(ports)]
        self.last_time = time.time()

    def start(self):
        self.last_time = time.time()

    def get_remaining_samples(self):
        now = time.time()
        elapsed = now - self.last_time
        samples_needed = int(elapsed * self.sample_rate)
        if samples_needed > 0:
            self.last_time = now

        return [generator.get_samples(samples_needed) for generator in self.generators]

class Sine(Math):

    generator = SineGenerator

class Cubic(Math):

    generator = CubicGenerator


if __name__ == "__main__":
    backend = Cubic(ports=5, freq=1, sample_rate=30)

    while 1:
        time.sleep(0.1)
        print backend.get_remaining_samples()

