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
import pyaudio
import threading
import Queue

BUFFER_SIZE = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
SAMPLE_RATE = 44100

in_queue = Queue.Queue()

def sync_samples():
    global stream
    while True:
        in_queue.put(stream.read(BUFFER_SIZE))

class PyAudio(Backend):
    def __init__(self):

        self._p = pyaudio.PyAudio()

        Backend.__init__(self, ports=1, sample_rate=SAMPLE_RATE)

    def stop(self):
        # Kill the worker thread nicely.
        stream.stop_stream()
        stream.close()
        self._p.terminate()

    def start(self):
        global stream
        stream = self._p.open(format = FORMAT,
                channels = CHANNELS,
                rate = SAMPLE_RATE,
                input = True,
                output = True,
                frames_per_buffer = BUFFER_SIZE)
        thread = threading.Thread(target=sync_samples)
        thread.daemon = True
        thread.start()

    def get_remaining_samples(self):
        raw_samples = ""
        while True:
            try:
                raw_samples += in_queue.get_nowait()
            except Queue.Empty:
                np_samples_array = numpy.fromstring(raw_samples, dtype=numpy.float32)
                np_samples_array.shape = (np_samples_array.size, 1)
                return np_samples_array

if __name__ == "__main__":
    import time
    pyaudio_backend = PyAudio()
    pyaudio_backend.start()
    i = 0
    while 1:
        time.sleep(0.01)
        pyaudio_backend.get_remaining_samples()

