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

from PyQt4 import QtGui

from controls import ColorControl

class ControlWidget(QtGui.QWidget):
    def __init__(self, graph, control, parent=None):
        super(ControlWidget, self).__init__(parent)

        self.control = control
        self.graph = graph

        self.name = control.display_name or control.name
        if control.verbose_name:
            self.setToolTip(control.verbose_name)

    def on_value_changed(self, value):
        raise NotImplemented

    def value_from_graph(self):
        raise NotImplemented


class ColorControlWidget(ControlWidget):
    def __init__(self, graph, control, parent=None):
        ControlWidget.__init__(self, graph, control, parent)

        self.button = QtGui.QPushButton()
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.button)

        self.style = "background-color: rgb(%d, %d, %d);"

        def on_click(val):
            color = QtGui.QColorDialog.getColor()
            color = color.red(), color.green(), color.blue()
            self.on_value_changed(color)

        self.button.clicked.connect(on_click)

        self.value_from_graph()

    def on_value_changed(self, value):
        self.setStyleSheet(self.style % value)
        getattr(self.graph, "set_" + self.control.name)(value)

    def value_from_graph(self):
        value = getattr(self.graph, "get_" + self.control.name)()
        self.setStyleSheet(self.style % value)



control_map = {
    ColorControl: ColorControlWidget,
}
