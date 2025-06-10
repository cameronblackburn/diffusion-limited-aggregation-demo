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
        print("Timer running")
        self.walker()
        self.view.update()

    
    def walker(self):
        grid = self.model.grid
        seeds = self.find_terminal_nodes()
        spawn = []

        for x, y in seeds:
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.model.rows and 0 <= ny < self.model.cols:
                    if grid[nx][ny] == 0:
                        spawn.append((nx, ny))

        spawn_copy = spawn[:]

        for _ in range(min(3, len(spawn_copy))):
            nx, ny = random.choice(spawn_copy)
            spawn_copy.remove((nx, ny))
            self.model.grid[nx][ny] = 2




    def find_terminal_nodes(self):
        grid = self.model.grid
        potential_terminals = []
        terminal_nodes = []

        for x in range(self.model.rows):
            for y in range(self.model.cols):
                if grid[x][y] == 2:
                    potential_terminals.append((x, y))

        for x, y in potential_terminals:
            count = 0
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.model.rows and 0 <= ny < self.model.cols:
                    if grid[nx][ny] == 0:
                        count += 1
            if count == 7 or count == 8:
                terminal_nodes.append((x, y))

        return terminal_nodes