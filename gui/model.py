import view


class MyDLAmodel:
    def __init__(self, rows=100, cols=100):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

        centre_x = cols // 2
        centre_y = rows // 2
        self.grid[centre_y][centre_x] = 1