import random

DIRECTIONS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


class MyDLAmodel:
    def __init__(self, rows=100, cols=100):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

    def set_start_state(self):
        """Set a random starting node"""
        x = random.randrange(self.rows)
        y = random.randrange(self.cols)
        self.grid[x][y] = 2

    def update_model(self):
        empty_cells = [(x, y) for x in range(self.rows) for y in range(self.cols) if self.grid[x][y] == 0]
        if not empty_cells:
            return  # grid full, do nothing
        # Pick a random empty cell and set to 2
        x, y = random.choice(empty_cells)
        self.grid[x][y] = 2

        
        
