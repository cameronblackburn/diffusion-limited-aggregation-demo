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
            weight = random.randint(0, 15)
            self.grid[x][y] = 1
            self.food.append(Food(x, y, self, weight))

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
        self.size = math.ceil(weight / 2)
        self.model = model
        self.radius = self.size
        self.lifetime = 10
        self.cells = []
        
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
        
        if not self.cells:
            self.lifetime = 0  # Ensure this food dies quickly
    
        
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
        target = self.closest_food(model)
        best_dirs = []
        
        if target:
            min_dist = float('inf')
            for dx, dy in DIRECTIONS:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < model.rows and 0 <= ny < model.cols and model.grid[nx][ny] == 0:
                    dist = abs(nx - target.x) + abs(ny - target.y)
                    if dist < min_dist:
                        best_dirs = [(dx, dy)]
                        min_dist = dist
                    elif dist == min_dist:
                        best_dirs.append((dx, dy))
            else:
                best_dirs = [random.choice(DIRECTIONS)]
        
        
        if best_dirs:
                dx, dy = random.choice(best_dirs)
                nx, ny = self.x + dx, self.y + dy

                self.x, self.y = nx, ny
                self.path.append((nx, ny))

                # Check surroundings to stick
                for dx2, dy2 in DIRECTIONS:
                    adj_x, adj_y = nx + dx2, ny + dy2
                    if 0 <= adj_x < model.rows and 0 <= adj_y < model.cols:
                        if model.grid[adj_x][adj_y] != 0:
                            self.stuck = True
                            return True  # Stuck and becoming new seed

                return False
    
    def closest_food(self, model):
        min_dist = float('inf')
        target = None
        for food in model.food:
            dist = abs(self.x - food.x) + abs(self.y - food.y)
            if dist < min_dist:
                min_dist = dist
                target = food
        return target
        

        
        
