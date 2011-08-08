# -*- coding: UTF-8 -*-

from stream_grapher.widgets.stream_graph import StreamGraph
from stream_grapher.widgets.multiple_stream_graph import MultipleStreamGraph
from stream_grapher.widgets.browsable_stream_graph import BrowsableStreamGraph
from stream_grapher.widgets.fft_graph import FFTGraph
from stream_grapher.widgets.qt_graph import QGLDrawer, QGLDrawerHScroll, Widget
from stream_grapher.connection import PatchBay

backends = []
widgets = []

from stream_grapher.backends.sthocastic import Brownian
sample_generator  = Brownian(ports=3, sample_rate=100)

backends.append(sample_generator)

simple_widget = Widget(StreamGraph(n_samples=300, size=(2, 2), position=(-1, -1),
                                      color=(255,205,205)))

multiple_widget = QGLDrawer(MultipleStreamGraph(n_graphs=2, n_samples=300, size=(2, 2),
                                                position=(-1, -1),
                                                colors=[(135,25,255*i) for i in range(2)]))

scrollable_widget = QGLDrawerHScroll(BrowsableStreamGraph(n_samples=300, size=(2, 2),
                                                          position=(-1, -1), color=(255,205,205)))

fft_widget = Widget(FFTGraph(fft_size=1024, fft_window_size=128,
                                sample_rate=sample_generator.sample_rate,
                                 size=(2, 2), position=(-1, -1), color=(205,24,57),
                                 window_type="boxcar"))

widgets.append(simple_widget)
widgets.append(multiple_widget)
widgets.append(scrollable_widget)
widgets.append(fft_widget)

PatchBay.connect(src=sample_generator, src_port=1, out=simple_widget)
PatchBay.connect(src=sample_generator, src_port=2, out_port=1, out=multiple_widget)
PatchBay.connect(src=sample_generator, src_port=3, out_port=2, out=multiple_widget)
PatchBay.connect(src=sample_generator, src_port=1, out=scrollable_widget)
PatchBay.connect(src=sample_generator, src_port=1, out=fft_widget)
