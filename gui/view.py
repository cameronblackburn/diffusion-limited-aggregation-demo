import sys, random, model
from PySide6 import QtWidgets, QtCore, QtGui

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        toolbar = QtWidgets.QToolBar("Toolbar")
        self.addToolBar(toolbar)
        self.grid_widget = GridWidget()
        self.setCentralWidget(self.grid_widget)
        self.resize(self.grid_widget.size())

class GridWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.model = model.MyDLAmodel()
        self.initialise_grid()

    
    def initialise_grid(self):
        
        self.cell_size = 6
        self.setFixedSize(self.model.cols * self.cell_size, self.model.rows * self.cell_size)

    



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyMainWindow()
    widget.resize(600, 600)
    widget.show()

    sys.exit(app.exec())
    