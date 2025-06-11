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

    def set_start_state(self, controller):
        """Set a random starting node"""
        x = random.randrange(self.rows)
        y = random.randrange(self.cols)
        self.grid[x][y] = 2
        self.seeds.append(Seed(x, y))
        
        controller.spawn_food()

    def update_model(self, controller):
        terminal_positions = self.find_terminal_nodes()
        active_seeds = [seed for seed in self.seeds if (seed.x, seed.y) in terminal_positions]

        for seed in active_seeds:
             if random.random() < 0.2: # 20% chance of spawn per tick to slow down spawn rate
                walker = seed.spawn_walker(self, controller)
                self.walkers.append(walker)


        for walker in self.walkers[:]:
            if walker.move(self, controller):
                self.grid[walker.x][walker.y] = 2
                self.seeds.append(Seed(walker.x, walker.y))
                self.walkers.remove(walker)
        
        
        for food in list(self.food):
            if not food.being_consumed: # check its being eaten
                food.lifetime -= food.decay_rate
            if food.lifetime <= 0: #if the lifetime of the object is <= 0 
                                    # then remove it and set the grid to empty
                for fx, fy in food.cells:
                    self.grid[fx][fy] = 0
                self.food.remove(food)
                    

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
            if food.being_consumed:
                food.consumption_progress += len(food.consumers)

                if food.consumption_progress >= food.consumption_time:
                    for x, y in food.cells:
                        if self.grid[x][y] == 1:
                            self.grid[x][y] = 2
                            self.seeds.append(Seed(x, y))
                    self.food.remove(food)


                
class Food:
    def __init__(self, x, y, model, weight=None):
        """Food Object
        (x, y) coordinates
        The weight of the food, this is used for pathfinding
        the radius is dependent on the weight. This is to simulate
        that a higher weight likely means a larger food source
        (Although the cells of the food source are randomised)

        Lifetime determines object lifetime which is decayed by
        decay_rate
        
        Food object keeps track of how long it takes to consume
        consumption progress
        whether the food is being eaten
        and a list of the total consumers (to use as coef)
        
        Detectable range is used to help prevent walkers from
        heading straight to food source
        """
        self.x = x
        self.y = y
        self.weight = weight
        self.radius = math.ceil(weight / 2)
        self.model = model
        self.lifetime = None
        self.decay_rate = None
        self.cells = []

        self.consumption_time = weight * 50
        self.consumption_progress = 0
        self.being_consumed = False
        self.consumers = set()
        
        self.detectable_range = int(self.radius + self.weight * 1.5)
        
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
        
            # See if spawned near slime or seed to auto-trigger consumption
            for dx in range(-self.radius, self.radius + 1):
                for dy in range(-self.radius, self.radius + 1):
                    nx = self.x + dx
                    ny = self.y + dy
                    if 0 <= nx < model.rows and 0 <= ny < model.cols:
                        if model.grid[nx][ny] == 2:
                            self.being_consumed = True
                            
                            # Add a dummy "ghost" consumer to simulate consumption
                            class GhostWalker:
                                def __init__(self, x, y):
                                    self.x = x
                                    self.y = y
                            self.consumers.add(GhostWalker(nx, ny))

                            break  # one consumer is enough to start
                if self.being_consumed:
                    break
        
class Seed:
    def __init__(self, x, y, radius=3):
        """Seed spawn location
        (x, y) location to spawn
        the radius dictates how many walkers can spawn on a given
        seed, each seed tracks its walkers to ensure it does
        not spawn too many
        """
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
        """Walker calss keeos track of it's (x, y) coords
        and the coords of it's path (for rendering)
        the walker will check when it is stuck
        """
        self.x = x
        self.y = y
        self.parent = parent
        self.path = [(x, y)]
        self.stuck = False
        self.consumption_time = 0
        
    def move(self, model, controller):
        """Movement logic
        walker will move randomly as per DLA
        and will stick to self or food source
        if the walker finds a food source nearby it will head
        in the direction of it and stick, to begin consuming
        """

        target = self.closest_food(model)
        best_dirs = []

        if target: # Found food
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
        else: # Just move
            best_dirs = [random.choice(DIRECTIONS)]

        if best_dirs: # If the walker is moving then append the movements to the path
            dx, dy = random.choice(best_dirs)
            nx, ny = self.x + dx, self.y + dy

            self.x, self.y = nx, ny
            self.path.append((nx, ny))

            for food in model.food:
                # Calculate distance from walker to food center
                dist = math.sqrt((self.x - food.x)**2 + (self.y - food.y)**2)
                if dist <= food.radius:
                    # If inside radius, mark as being consumed
                    food.being_consumed = True
                    food.consumers.add(self)
                    return True

            # Check surroundings to stick
            for dx2, dy2 in DIRECTIONS:
                adj_x, adj_y = nx + dx2, ny + dy2
                if 0 <= adj_x < model.rows and 0 <= adj_y < model.cols:
                    val = model.grid[adj_x][adj_y]
                    if val != 0:
                        if val == 1:
                            food_obj = self.find_food_at(adj_x, adj_y, model)
                            if food_obj:
                                food_obj.being_consumed = True
                                food_obj.consumers.add(self)
                                food_obj.weight = 0
                            self.stuck = True
                        return True
        return False

    def find_food_at(self, x, y, model):
        for food in model.food:
            if(x, y) in food.cells:
                return food
        return None

    def find_food_consumed(self, model):
        """Helper to find the food the walker is stuck to
        """
        for food in model.food:
            if self in food.consumers:
                return food
        return None

    def closest_food(self, model):
        """Finding the clsoest food to return as
        the target
        """
        best_score = float('inf')
        target = None
        for food in model.food:
            dist = math.sqrt((self.x - food.x)**2 + (self.y - food.y)**2) # Euclidean distance
            if dist <= food.detectable_range:
                # Avoid division by zero:
                weight = food.weight if food.weight > 0 else 1
                score = dist / weight # Pathfinding weight is determined by distance and food weight
                if score < best_score:
                    best_score = score
                    target = food
        return target