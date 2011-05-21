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

class Connection(object):
    def __init__(self, src, src_port, out, out_port):
        self.src = src
        self.src_port = src_port
        self.out = out
        self.out_port = out_port

class PatchBay(object):
    """
    Use out_port != 0 when using MultipleStreamWidget
    """
    connections = []
    @classmethod
    def connect(cls, src, src_port, out, out_port=0):
        cls.connections.append(Connection(src, src_port, out, out_port))
