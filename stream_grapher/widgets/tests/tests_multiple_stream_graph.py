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

from stream_grapher.widgets.multiple_stream_graph import MultipleStreamGraph

class TestMultipleStremGraph(unittest.TestCase):
    def setUp(self):
        self.test_data = np.arange(10)
        # n_samples, size, position, color
        n_graphs, n_samples, size, position, color = 3, 10, (1, 1), (0, 0), (255, 255, 255)
        self.graph = MultipleStreamGraph(n_graphs, n_samples, size, position, colors=[color]*3)

    def test_add_samples(self):
        self.graph.add_samples([[50, 50, 50]])
        self.assertTrue(all(self.graph.samples[0] == [50,50,50]))
        self.graph.add_samples([[51, 52, 53]])
        self.assertTrue(all(self.graph.samples[0] == [50,50,50]))
        self.assertTrue(all(self.graph.samples[1] == [51,52,53]))

if __name__ == '__main__':
    unittest.main()
