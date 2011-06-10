# -*- coding: UTF-8 -*-

from widgets.stream_graph import StreamGraph
from widgets.multiple_stream_graph import MultipleStreamGraph
from widgets.browsable_stream_graph import BrowsableStreamGraph
from widgets.qt_graph import QGLDrawer, QGLDrawerHScroll
from connection import PatchBay

backends = []
widgets = []

from backends.sthocastic import Brownian
sample_generator  = Brownian(ports=4, sample_rate=100)

backends.append(sample_generator)

widget1 = QGLDrawer(StreamGraph(n_samples=300, size=(2, 2), position=(-1, -1), color=(255,205,205)))
widget2 = QGLDrawer(MultipleStreamGraph(n_graphs=2, n_samples=300, size=(2, 2),
                                        position=(-1, -1),
                                        colors=[(135,25,255*i) for i in range(2)]))
widget3 = QGLDrawerHScroll(BrowsableStreamGraph(n_samples=300, size=(2, 2), position=(-1, -1), color=(255,205,205)))

widgets.append(widget1)
widgets.append(widget2)
widgets.append(widget3)

PatchBay.connect(src=sample_generator, src_port=1, out=widget1)
PatchBay.connect(src=sample_generator, src_port=2, out_port=1, out=widget2)
PatchBay.connect(src=sample_generator, src_port=3, out_port=2, out=widget2)
PatchBay.connect(src=sample_generator, src_port=4, out=widget3)
