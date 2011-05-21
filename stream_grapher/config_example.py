# -*- coding: UTF-8 -*-
from stream_widgets import StreamWidget, MultipleStreamWidget, FFTWidget, BrowsableStreamWidget
from connection import PatchBay

DISPLAY = {
    "width": 1024,
    "height": 700,
    "fullscreen":False,
    "vsync": False,
    "gl_config": {              # pyglet.gl.Config
        "double_buffer": True,
        "buffer_size": 24,
    },

}

N_SAMPLES = 350

backends = []
widgets = []

from backends.sthocastic import Brownian
sample_generator  = Brownian(ports=2, sample_rate=100)

backends.append(sample_generator)

stream_widget = StreamWidget(N_SAMPLES, size=(400,400), position=(100, 100), color=(255,0,0))
#fft_widget = FFTWidget(1024, 1024, sample_rate=300, size=(400,400), position=(550, 100))
#b_stream_widget = StreamWidget(N_SAMPLES, size=(400,400), position=(550, 100), color=(255,0,0))
multiple_stream_widget = MultipleStreamWidget(2, N_SAMPLES, size=(400,400), position=(550, 100), colors=((255,0,0),(100,100,100)))
widgets.extend([stream_widget, multiple_stream_widget])

PatchBay.connect(src=sample_generator, src_port=1, out=stream_widget)
#PatchBay.connect(src=sample_generator, src_port=1, out=fft_widget)
PatchBay.connect(src=sample_generator, src_port=1, out=multiple_stream_widget, out_port=1)
PatchBay.connect(src=sample_generator, src_port=2, out=multiple_stream_widget, out_port=2)

