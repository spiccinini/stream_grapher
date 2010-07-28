from backend import Backend
import random
import threading
import Queue
import time


class RandomWalker(object):
    def __init__(self, min_value=None, max_value=None):
        self.actual = 0
        self.min_value = min_value
        self.max_value = max_value

    def __iter__(self):
        return self

    def next(self):
        self.actual += random.choice((-1, 1))
        if self.min_value is not None and self.min_value > self.actual:
            self.actual = self.min_value
        elif self.max_value is not None and self.max_value < self.actual:
            self.actual = self.max_value
        return self.actual


class BrownianWorker(threading.Thread):
    def __init__(self, walkers, out_queue, sleep):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.out_queue = out_queue
        self.walkers = walkers
        self.sleep = sleep

    def run(self):
        while True:
            sample = [walker.next() for walker in self.walkers]
            self.out_queue.put(sample)
            time.sleep(self.sleep)


class Brownian(Backend):
    def __init__(self, ports, sample_rate):
        Backend.__init__(self, ports, sample_rate=sample_rate)
        sleep = 1./sample_rate
        self.out_queue = Queue.Queue()
        walkers = [RandomWalker(min_value=-255, max_value=255) for x in range(ports)]
        self.worker = BrownianWorker(walkers, self.out_queue, sleep)
        self.worker.start()

    def get_remaining_samples(self):
        samples = []
        while True:
            try:
                samples.extend(self.out_queue.get_nowait())
            except Queue.Empty:
                return samples

if __name__ == "__main__":
    brown_noise = Brownian(ports=4, sample_rate=100)
    
    while 1:
        time.sleep(0.1)
        print brown_noise.get_remaining_samples()
