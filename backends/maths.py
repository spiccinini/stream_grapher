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

class MathGenerator(object):
    def __init__(self):
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
    def __init__(self):
        MathGenerator.__init__(self)

    def gen_samples(self):
        self.samples.extend([t**3/4.0 for t in range(-10, 10)])

class MathWorker(threading.Thread):
    def __init__(self, generator, out_queue, sleep):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.out_queue = out_queue
        self.sleep = sleep
        self.generator = generator

    def run(self):
        while True:
            self.out_queue.put(self.generator.get_samples(1))
            time.sleep(self.sleep)

class Math(Backend):
    def __init__(self, ports, sample_rate):
        Backend.__init__(self, ports, sample_rate=sample_rate)
        sleep = 1./sample_rate
        self.out_queue = Queue.Queue()
        self.generator = CubicGenerator()
        self.worker = MathWorker(CubicGenerator(), self.out_queue, sleep)
        self.worker.start()

    def get_remaining_samples(self):
        samples = []
        while True:
            try:
                samples.extend(self.out_queue.get_nowait())
            except Queue.Empty:
                return samples


if __name__ == "__main__":
    backend = Math(ports=1, sample_rate=30)
    
    while 1:
        time.sleep(0.1)
        print backend.get_remaining_samples()

