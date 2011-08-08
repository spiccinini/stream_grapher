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

import sys
import unittest
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

from stream_grapher.widgets.qt_graph import Widget
from stream_grapher.widgets.stream_graph import StreamGraph


# For more details on pyqt testing look https://voom.kilnhg.com/Project/2/Make-Stuff-Happen

class WidgetTest(unittest.TestCase):

    def setUp(self):
        '''Create the GUI'''
        self.app = QApplication(sys.argv)

    def test_stream_widget(self):
        graph = StreamGraph(n_samples=300, size=(1,1), position=(-1,-1), color=(255, 0, 255))
        widget = Widget(graph)


if __name__ == "__main__":
    unittest.main()
