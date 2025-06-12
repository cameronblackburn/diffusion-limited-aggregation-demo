from PySide6 import QtWidgets, QtCore, QtGui
import random

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        toolbar = QtWidgets.QToolBar("Toolbar")
        self.addToolBar(toolbar)
        self.grid_widget = GridWidget()
        self.setCentralWidget(self.grid_widget)
        self.resize(self.grid_widget.size())

class GridWidget(QtWidgets.QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model
        self.initialise_grid()


    
    def initialise_grid(self):
        
        self.cell_size = 6
        self.setFixedSize(self.model.cols * self.cell_size, self.model.rows * self.cell_size)

    def update_view(self):
        self.update()

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        for y in range(self.model.rows):
            for x in range(self.model.cols):
                value = self.model.grid[y][x]
                if value == 1:
                    painter.fillRect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size, QtCore.Qt.red)
                elif value == 2:
                    painter.fillRect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size, QtCore.Qt.green)
