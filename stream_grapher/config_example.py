# -*- coding: UTF-8 -*-

from widgets.stream_graph import StreamGraph
from widgets.qt_graph import QGLDrawer
from connection import PatchBay

backends = []
widgets = []

from backends.sthocastic import Brownian
sample_generator  = Brownian(ports=2, sample_rate=100)

backends.append(sample_generator)

stream_widget = QGLDrawer(StreamGraph(n_samples=300, size=(2, 2), position=(-1, -1), color=(255,255,255)))
widgets.append(stream_widget)

PatchBay.connect(src=sample_generator, src_port=1, out=stream_widget)
