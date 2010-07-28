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


class FileReaderWorker(threading.Thread):
    def __init__(self, file_handler, out_queue, sleep):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.out_queue = out_queue
        self.file_handler = file_handler
        self.sleep = sleep

    def run(self):
        init = time.time()
        for line in self.file_handler:
            sample = self.parser(line)
            self.out_queue.put(sample)
            time.sleep(self.sleep)

    def parser(self, line):
        return [float(x) for x in line.split(",")]

class FileReader(Backend):
    def __init__(self, ports, sample_rate, filename):
        Backend.__init__(self, ports, sample_rate=sample_rate)
        sleep = 1./sample_rate
        f = open(filename, "r")
        self.out_queue = Queue.Queue()

        self.worker = FileReaderWorker(f, self.out_queue, sleep)
        self.worker.start()

    def get_remaining_samples(self):
        samples = []
        while True:
            try:
                samples.extend(self.out_queue.get_nowait())
            except Queue.Empty:
                return samples


if __name__ == "__main__":
    f = open("test.txt", "w")
    f.write("123.123, 1398.9998\n 1954454.0, 4953\n")
    f.close()
    filebackend = FileReader(ports=2, sample_rate=100, filename="test.txt")

    while 1:
        time.sleep(0.1)
        print filebackend.get_remaining_samples()

