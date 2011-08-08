# -*- coding: UTF-8 -*-

# Copyright (C) 2011  Santiago Piccinini
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

import random
import unittest
import numpy as np

from stream_grapher.widgets.stream_graph import StreamGraph

class TestStremGraph(unittest.TestCase):
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
