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
            self.food.append(Food(x, y, self, weight=random.randint(1, 15)))

    def update_model(self, controller):
        terminal_positions = self.find_terminal_nodes()
        active_seeds = [seed for seed in self.seeds if (seed.x, seed.y) in terminal_positions]

        for seed in active_seeds:
            # if random.random() < 0.1:
            #     print("Spawning walker with tiny chance!")
                walker = seed.spawn_walker(self, controller)
                self.walkers.append(walker)


        for walker in self.walkers[:]:
            if walker.move(self, controller):
                self.grid[walker.x][walker.y] = 2
                self.seeds.append(Seed(walker.x, walker.y))  # Remember to import Seed
                self.walkers.remove(walker)

        self.update_food_consumption()



    def find_terminal_nodes(self):
        terminal_nodes = []
        for x in range(self.rows):
            for y in range(self.cols):
                if self.grid[x][y] == 2:
                    empty_neighbors = 0
                    for dx, dy in DIRECTIONS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            if self.grid[nx][ny] == 0:
                                empty_neighbors += 1
                    if empty_neighbors >= 5:
                        terminal_nodes.append((x, y))
        return terminal_nodes


    def update_food_consumption(self):
        for food in self.food[:]:
            print(f"Checking food at {food.x}, {food.y} — being_consumed={food.being_consumed}")
            if food.being_consumed:
                print(f"food at {food.x}, {food.y} is being consumed by new method")
                food.consumption_progress += len(food.consumers)

                if food.consumption_progress >= food.consumption_time:
                    print(f"Food at ({food.x},{food.y}) fully consumed.")
                    for x, y in food.cells:
                        if self.grid[x][y] == 1:
                            self.grid[x][y] = 2
                            self.seeds.append(Seed(x, y))
                    self.food.remove(food)


                
class Food:
    def __init__(self, x, y, model, weight=None):
        self.x = x
        self.y = y
        self.weight = weight
        self.radius = math.ceil(weight / 2)
        self.model = model
        self.lifetime = 10
        self.cells = []

        self.consumption_time = self.weight * 100
        self.consumption_progress = 0
        self.being_consumed = False
        self.consumers = set()
        
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
        
    def spawn_walker(self, model, controller):
        walker = Walker(self.x, self.y, parent=self, controller=controller)
        self.walkers.append(walker)
        return walker
    
class Walker:
    def __init__(self, x, y, parent=None, controller=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.path = [(x, y)]
        self.stuck = False
        
    def move(self, model, controller):
        target = self.closest_food(model)
        best_dirs = []

        if target:
            print(f"Walker targeting food at ({target.x}, {target.y})")
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
                    val = model.grid[adj_x][adj_y]
                    if val != 0:
                        self.stuck = True
                        if val == 1:
                            food_obj = self.find_foot_at(adj_x, adj_y, model)
                            if food_obj:
                                food_obj.being_consumed = True
                                food_obj.consumers.add(self)
                            self.stuck = True
                            print(f"Walker consuming food at ({adj_x}, {adj_y}) — calling consume")
                        return True
        return False

    def find_foot_at(self, x, y, model):
        for food in model.food:
            if(x, y) in food.cells:
                return food
        return None

    def closest_food(self, model):
        min_dist = float('inf')
        target = None
        for food in model.food:
            dist = abs(self.x - food.x) + abs(self.y - food.y)
            if dist < min_dist:
                min_dist = dist
                target = food
        return target
        
