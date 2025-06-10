import random

DIRECTIONS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


class MyDLAmodel:
    def __init__(self, rows=100, cols=100):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.seeds = []
        self.food = []
        self.walkers = []

    def set_start_state(self):
        """Set a random starting node"""
        x = random.randrange(self.rows)
        y = random.randrange(self.cols)
        self.grid[x][y] = 2
        self.seeds.append(Seed(x, y))
        
        x = random.randrange(self.rows)
        y = random.randrange(self.cols)
        if self.grid[x][y] != 2:
            self.grid[x][y] = 1
            self.food.append(Food(x, y))

    def update_model(self):
        for seed in self.seeds:
            if len(seed.walkers) < 3:
                self.walkers.append(seed.spawn_walker())

        # Move all walkers
        for walker in self.walkers[:]:  # copy since we may modify list
            if walker.move(self):
                self.grid[walker.x][walker.y] = 2
                self.seeds.append(Seed(walker.x, walker.y))
                self.walkers.remove(walker)
                
class Food:
    def __init__(self, x, y, weight=10):
        self.x = x
        self.y = y
        self.weight = weight
    
        
class Seed:
    def __init__(self, x, y, radius=3):
        self.x = x
        self.y = y
        self.radius = radius
        self.walkers = []
        
    def spawn_walker(self):
        walker = Walker(self.x, self.y, parent=self)
        self.walkers.append(walker)
        return walker
    
class Walker:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.path = [(x, y)]
        self.stuck = False
        
    def move(self, model):
        dx, dy = random.choice(DIRECTIONS)
        nx, ny = self.x + dx, self.y + dy
        
        if 0 <= nx < model.rows and 0 <= ny < model.cols:
            self.x, self.y = nx, ny
            self.path.append((nx, ny))
        
        for dx, dy in DIRECTIONS:
            adj_x, adj_y = nx + dx, ny + dy
            if 0 <= adj_x < model.rows and 0 <= adj_y < model.cols:
                if model.grid[adj_x][adj_y] == 2:
                    self.stuck = True
                    return True  # signal to stick
        return False
        

        
        
