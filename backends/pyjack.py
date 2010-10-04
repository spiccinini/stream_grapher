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
import sys

from scipy.signal import iirdesign, lfilter
import numpy

class PasaBajos(object):
    def __init__(self):
        FS = 48000.
        BANDPASS = 1000.
        STOPBAND = 1500.
        self.b, self.a = iirdesign(wp = BANDPASS/FS, ws = STOPBAND/FS, gpass=0.1, gstop=40)
        self.init_cond = numpy.zeros(max(len(self.a),len(self.b))-1)

    def do_filter(self, data):
        filtered_data, self.init_cond = lfilter(self.b, self.a, data, zi=self.init_cond)
        return filtered_data

filtro = PasaBajos()

class JackWorker(threading.Thread):
    def __init__(self, output, capture, counter, sleep, nonstop_event):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.output = output
        self.capture = capture
        self.counter = counter
        self.sleep = sleep
        self.nonstop_event = nonstop_event

    def run(self):
        while self.nonstop_event.isSet():
            try:
                jack.process(self.output, self.capture)
                self.capture[0] = filtro.do_filter(self.capture[0])
                self.output = self.capture.copy()

                self.counter[0] += 1
                time.sleep(self.sleep)
            except jack.InputSyncError:
                print >> sys.stderr, "Input Sync Error, samples lost"
            except jack.OutputSyncError:
                print >> sys.stderr, "Output Sync"
        # Workarround to put output buffer to zero. If not for some reason
        # jackd will constantly output the last buffer, making noise
        self.output = self.output*0
        jack.process(self.output, self.capture)
        time.sleep(0.2) # "Waiting" the jack thread to sync.
        jack.deactivate()
        jack.detach()
        self.nonstop_event.set()

class Jack(Backend):
    def __init__(self):
        jack.attach("stream_grapher")
        jack.register_port("in_1", jack.IsInput)
        jack.register_port("in_2", jack.IsInput)
        jack.register_port("out_1", jack.IsOutput)
        jack.register_port("out_2", jack.IsOutput)

        jack.activate()
        try:
            jack.connect("system:capture_1", "stream_grapher:in_1")
            jack.connect("system:capture_2", "stream_grapher:in_2")
            jack.connect("stream_grapher:out_1", "system:playback_1")
            jack.connect("stream_grapher:out_2", "system:playback_2")
        except jack.UsageError:
            pass
        
        buff_size = jack.get_buffer_size()
        if buff_size < 1024:
            print >> sys.stderr, "Jack buffer size is %d. If you have sync problems try a buff size >= 1024." % (buff_size, )

        self.buff_size = jack.get_buffer_size()
        sample_rate = jack.get_sample_rate()

        Backend.__init__(self, ports=2, sample_rate=sample_rate)
        self.capture = numpy.zeros((2, self.buff_size), 'f')
        self.output = numpy.zeros((2, self.buff_size), 'f')

        self.counter = [0]
        self.last_counter = 0

        # Time to sleep between calls to jack.process
        # R should be at least 1.0
        # To never get InputSyncErrors R should be like 2.0 or higher
        R = 1.2
        self.sleep = self.buff_size / float(self.sample_rate) / R

    def stop(self):
        # Kill the worker thread nicely.
        self.worker_corriendo.clear()
        self.worker_corriendo.wait()

    def start(self):
        self.worker_corriendo = threading.Event()
        self.worker_corriendo.set()
        self.worker = JackWorker(self.output, self.capture, self.counter, self.sleep, self.worker_corriendo)
        self.worker.start()

    def get_remaining_samples(self):
        if self.counter[0] > self.last_counter: # TODO: add a Lock
            if self.counter[0] > self.last_counter + 1:
                print >> sys.stderr, "Lost at least %d samples" % ((self.counter[0]-self.last_counter -1)*self.buff_size)
            self.last_counter = self.counter[0]
            return self.capture.T
        else:
            return []


if __name__ == "__main__":
    jack_backend = Jack()
    i = 0
    while 1:
        time.sleep(0.01)
        print jack_backend.get_remaining_samples()

