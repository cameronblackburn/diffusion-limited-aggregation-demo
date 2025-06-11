import random, math, noise

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
            self.food.append(Food(x, y, self, weight=random.randint(0, 15)))

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
    def __init__(self, x, y, model, weight=None):
        self.x = x
        self.y = y
        self.weight = weight
        self.radius = math.ceil(weight / 2)
        self.model = model
        self.lifetime = 10
        self.cells = []
        
        """Randomising the shape of the food"""
        scale = 0.1       # Controls noise frequency
        threshold = 0.1   # Controls how "solid" the blob is

        for dx in range(-self.radius * 2, self.radius * 2):
            for dy in range(-self.radius * 2, self.radius * 2):
                nx = self.x + dx
                ny = self.y + dy

                # Circular mask condition
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist > self.radius:
                    continue  # skip anything outside the radius

                if 0 <= nx < model.rows and 0 <= ny < model.cols:
                    n = noise.pnoise2((nx + x) * scale, (ny + y) * scale)
                    if n > threshold:
                        if model.grid[nx][ny] == 0:
                            model.grid[nx][ny] = 1
                            self.cells.append((nx, ny))
    
        
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
        self.controller.move(model)
        
        
