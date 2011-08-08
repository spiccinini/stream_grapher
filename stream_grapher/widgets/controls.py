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


class Control(object):
    def __init__(self, name, display_name=None, verbose_name=None):
        self.name = name
        self.display_name = display_name
        self.verbose_name = verbose_name


class ColorControl(Control):
    pass


class FloatControl(Control):
    pref_types = ("slider", "text_input")

    def __init__(self, name, pref_type="slider", *args, **kwargs):

        super(FloatControl, self).__init__(name, *args, **kwargs)


class IntControl(Control):
    pass


class ChoicesControl(Control):

    def __init__(self, name, choices, *args, **kwargs):

        super(ChoicesControl, self).__init__(name, *args, **kwargs)
        self.choices = choices
