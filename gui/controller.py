import random
from PySide6 import QtCore
DIRECTIONS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


class DLAController(QtCore.QObject):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.initialise_timer()

    def initialise_timer(self):
    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step_model)
        self.timer.start(100)
    
    def step_model(self):
        self.model.update_model()
        self.view.update()


    def check_adjacent_seeds(self, seeds):
        import model
        self.model = model.MyDLAmodel()

        
        