# -*- coding: UTF-8 -*-
from stream_widgets import StreamWidget, FFTWidget
from connection import PatchBay

DISPLAY = {
    "width": 1024,
    "height": 768,
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

from backends.pyjack import Jack
sample_generator = Jack()

backends.append(sample_generator)

stream_widget_left = StreamWidget(N_SAMPLES, size=(400,400), position=(70, 300), color=(255,0,0))
stream_widget_left.graph.set_samples_per_h_division(1000)
stream_widget_left.graph.set_values_per_v_division(0.25)

stream_widget_right = StreamWidget(N_SAMPLES, size=(400,400), position=(570, 300), color=(255,0,0))
stream_widget_right.graph.set_samples_per_h_division(1000)
stream_widget_right.graph.set_values_per_v_division(0.25)

fft_widget_left = FFTWidget(1024, 1024, sample_rate=sample_generator.sample_rate, size=(900,200), position=(70, 40))
fft_widget_left.graph.amplification = 10

widgets.extend([stream_widget_left, stream_widget_right, fft_widget_left])

PatchBay.connect(src=sample_generator, src_port=1, out=stream_widget_left)
PatchBay.connect(src=sample_generator, src_port=2, out=stream_widget_right)
PatchBay.connect(src=sample_generator, src_port=1, out=fft_widget_left)


