# -*- coding: UTF-8 -*-
from stream_grapher.widgets.browsable_stream_graph import  BrowsableStreamWidget
from stream_grapher.connection import PatchBay

DISPLAY = {
    "width": 1000,
    "height": 600,
    "fullscreen": False,
    "vsync": False,
    "gl_config": {              # pyglet.gl.Config
        "double_buffer": True,
        "buffer_size": 24,
    },

}

N_SAMPLES = 350

backends = []
widgets = []

from backends.horno_com import Horno
sample_generator = Horno(ports=1, sample_rate=100) #FIXME: sample_rate

backends.append(sample_generator)

stream_widget = BrowsableStreamWidget(N_SAMPLES, size=(900,500), position=(80, 20), color=(255,0,0))
stream_widget.graph.set_samples_per_h_division(1000)
stream_widget.graph.set_values_per_v_division(0.25)

widgets.extend([stream_widget])

PatchBay.connect(src=sample_generator, src_port=1, out=stream_widget)


