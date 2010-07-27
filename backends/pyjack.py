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
import numpy
import jack
import threading
import time

class JackWorker(threading.Thread):
    def __init__(self, output, capture, counter, sleep):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.output = output
        self.capture = capture
        self.counter = counter
        self.sleep = sleep

    def run(self):
        while True:
            try:
                # TODO: add a Lock
                jack.process(self.output, self.capture)
                self.counter[0] += 1
                time.sleep(self.sleep)
            except jack.InputSyncError:
                print "Input Sync Error, samples lost"
            except jack.OutputSyncError:
                print "Output Sync"

class Jack(Backend):
    def __init__(self):
        jack.attach("stream_grapher")
        jack.register_port("in", jack.IsInput)
        jack.activate()
        jack.connect("system:capture_1", "stream_grapher:in")
        jack.connect("system:capture_2", "stream_grapher:in")
        self.buff_size = jack.get_buffer_size()
        sample_rate = float(jack.get_sample_rate())

        Backend.__init__(self, ports=1, sample_rate=sample_rate)
        self.capture = numpy.zeros((1, self.buff_size), 'f')
        output = numpy.zeros((1, self.buff_size), 'f')

        self.counter = [0]
        self.last_counter = 0

        # Time to sleep between calls to jack.process
        # R should be at least 1.0
        # To never get InputSyncErrors R should be like 2.0 or higher
        R = 1.2
        sleep = self.buff_size / float(self.sample_rate) / R

        self.worker = JackWorker(output, self.capture, self.counter, sleep)
        self.worker.start()

    def get_remaining_samples(self):
        if self.counter[0] > self.last_counter: # TODO: add a Lock
            if self.counter[0] > self.last_counter + 1:
                print "Lost at least %d samples" % ((self.counter[0]-self.last_counter -1)*self.buff_size)
            self.last_counter = self.counter[0]
            return self.capture[0]
        else:
            return []


if __name__ == "__main__":
    jack_backend = Jack()
    i = 0
    while 1:
        time.sleep(0.01)
        print jack_backend.get_remaining_samples()

