import random
import unittest
import numpy as np

from stream_grapher.widgets.stream_graph import StreamGraph

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.test_data = np.arange(10)
        self.graph = StreamGraph(n_samples=10, size=(1,1), position=(0,0), color=(255,255,255))

    def test_add_samples(self):
        self.graph.add_samples([50])
        self.assertEqual(self.graph.samples[0], 50)
        self.graph.add_samples([51, 52])
        self.assertEqual(self.graph.samples[0], 50)
        self.assertEqual(self.graph.samples[1], 51)
        self.assertEqual(self.graph.samples[2], 52)
        self.graph.add_samples(list(range(20)))
        self.assertEqual(self.graph.samples[0], 10)

    def test_n_samples(self):
        self.graph.n_samples = 5
        self.graph.add_samples([50])
        self.assertEqual(self.graph.samples[0], 50)
        self.graph.add_samples(list(range(20)))
        self.assertEqual(self.graph.samples[0], 15)



if __name__ == '__main__':
    unittest.main()
