import random
from PySide6 import QtCore
from .model import Food


DIRECTIONS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

class DLAController(QtCore.QObject):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.initialise_timer()

        self.food_timer = QtCore.QTimer()
        self.food_timer.timeout.connect(self.spawn_food)
        self.food_timer.start(15000) # 15 seconds spawn food

    def initialise_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step_model)
        self.timer.start(100)

    
    def step_model(self):
        self.spawn_walker()
        self.view.update()


    
    def spawn_walker(self):
        grid = self.model.grid
        seeds = self.find_terminal_nodes()
        spawn_walker = []

        for x, y in seeds:
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.model.rows and 0 <= ny < self.model.cols:
                    if grid[nx][ny] == 0:
                        spawn_walker.append((nx, ny))

        spawn_walker_copy = spawn_walker[:]

        for _ in range(min(3, len(spawn_walker_copy))):
            nx, ny = random.choice(spawn_walker_copy)
            spawn_walker_copy.remove((nx, ny))
            self.model.grid[nx][ny] = 2

    def spawn_food(self):
        grid = self.model.grid
        empty_cells = [(x, y) for x in range(self.model.rows) for y in range(self.model.cols) if grid[x][y] == 0]

        if not empty_cells:
            return # Nowhere to spawn food

        x, y = random.choice(empty_cells)
        new_food = Food(x, y, model=self.model, weight=random.randint(0, 15))

        self.model.food.append(new_food)

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
            if count >= 5:
                terminal_nodes.append((x, y))

        return terminal_nodes

    def move_walker(self, model):
        target = self.closest_food(model)
        best_dirs = []
        
        if target: # check if there is a food source nearby and head towards it
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
        else: # else just travel randomly
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
    
    def find_closest_food(self, model):
        min_dist = float('inf')
        target = None
        for food in model.food:
            dist = abs(self.x - food.x) + abs(self.y - food.y)
            if dist < min_dist:
                min_dist = dist
                target = food
        return target