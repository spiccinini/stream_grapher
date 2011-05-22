import sys, os
import numpy as np
from PyQt4 import QtCore, QtGui, uic

from connection import PatchBay

DRAW_FPS = 60

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'qtui/main.ui')
        uic.loadUi(uifile, self)

        import config
        self.config = config

        for widget in self.config.widgets:
            self.central_layout.addWidget(widget)

        for backend in self.config.backends:
            backend.start()

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(1000/float(DRAW_FPS))

    def on_actionPlay_toggled(self, checked):
        if checked:
            self.update_timer.start()
        else:
            self.update_timer.stop()

    def update(self):
        for backend in self.config.backends:
            samples = backend.get_remaining_samples()
            for connection in PatchBay.connections:
                if connection.src is backend:
                    samples = np.asarray(samples)
                    if samples.size != 0:
                        out_samples = samples.transpose()[connection.src_port-1]
                    else:
                        out_samples = samples
                    if connection.out_port:
                        connection.out.graph.add_samples(out_samples, connection.out_port-1)
                    else:
                        connection.out.graph.add_samples(out_samples)

        for widget in self.config.widgets:
            widget.updateGL()


def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

