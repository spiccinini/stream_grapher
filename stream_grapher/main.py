import sys, os
from PyQt4 import QtCore, QtGui, uic

from widgets.qt_graph import QGLDrawer
from widgets.stream_graph import StreamGraph

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'qtui/main.ui')
        uic.loadUi(uifile, self)

        self.glwidget = QGLDrawer(self, StreamGraph(n_samples=300, size=(2, 2), position=(-1, -1), color=(255,255,255)))
        self.central_layout.addWidget(self.glwidget)
        self.fps_timer = QtCore.QTimer()
        self.fps_timer.timeout.connect(self.glwidget.updateGL)
        self.fps_timer.start(1/60.*1000)

def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

