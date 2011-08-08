# -*- coding: UTF-8 -*-

# Copyright (C) 2009, 2010, 2011  Santiago Piccinini
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

class Backend(object):
    def __init__(self, ports=1, sample_rate=1.0, y_axis_magnitude="mV"):
        """
        Backend base class. Every backend should inherite from this class.

        ports are the number of different streams returned simultaneously.
        Eg: 8 Channell ADC backend.
        The sample rate is the sample rate of the device and not the how quickly
        get_remaining_samples is called. It's only descriptive, eg. used in the
        FFTWidget to build the frecuency axis.
        y_axis_magnitude is descriptive. A sample of value 1 must equival to that
        magnitude.
        """

        self.ports = ports
        self.sample_rate = sample_rate
        self.y_axis_magnitude = y_axis_magnitude # a sample of value 1 must
                                                 # equival to the magnitude

    def start(self):
        """
        Get's called to start the backend. After that, get_remaining_samples
        will be called periodicaly. Implement only if needed.
        """
        pass

    def stop(self):
        """
        Get's called to stop the backend. After that no more calls to
        get_remaining_samples will be done. A subsequent start() could be made.
        Implement only if needed.
        """
        pass

    def get_remaining_samples(self):
        """
        This method is called by stream_grapher to get new samples from the backend.
        It should retrieve a list or numpy's array. If the backend has N ports and
        is returning M samples the shape should be
        [[port1_sample1, port1_sample2, ..., port1_sampleM],
         [port2_sample1, port2_sample2, ..., port2_sampleM],
         ...,
         [portN_sample1, portN_sample2, ..., portN_sampleM]]

        If there are no samples to retrieve just return an empty list.
        """
        raise NotImplementedError
