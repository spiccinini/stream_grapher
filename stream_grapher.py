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

import os
import sys

from PyQt4 import QtGui

from stream_grapher import main

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Usage: ./stream_grapher.py config_file.py\n"
        print "Take a look to stream_grapher/config_*.py files for inspiration."
        sys.exit(1)
    else:
        config_filename = sys.argv[1]

    app = QtGui.QApplication(sys.argv)
    window = main.Main(config_filename=config_filename)
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())
