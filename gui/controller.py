import random
from PySide6 import QtCore
from .model import Food, Seed, Walker

DIRECTIONS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

class DLAController(QtCore.QObject):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.initialise_timer()

        self.food_timer = QtCore.QTimer()
        self.food_timer.timeout.connect(self.spawn_food)
        self.food_timer.start(20000) # 20 seconds spawn food

    def initialise_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step_model)
        self.timer.start(100)

    
    def step_model(self):
        self.model.update_model(self)
        food_cells = [(x, y) for x in range(self.model.rows) for y in range(self.model.cols) if self.model.grid[x][y] == 1]
        walker_cells = [(w.x, w.y) for w in self.model.walkers]
        print(f"Food: {len(food_cells)} cells, Walkers: {len(walker_cells)}")
        # Move all walkers
        for walker in self.model.walkers[:]:  # Iterate over a copy
            if walker.move(self.model, self):  # If walker gets stuck
                self.model.grid[walker.x][walker.y] = 2
                self.model.seeds.append(Seed(walker.x, walker.y))
                self.model.walkers.remove(walker)

        self.view.update()


    
    def spawn_walker(self):
        grid = self.model.grid
        seeds = self.model.find_terminal_nodes()
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

            seed = Seed(nx, ny)  # optional: or use existing seed at (x, y)
            walker = Walker(nx, ny, parent=seed, controller=self)
            self.model.walkers.append(walker)
            self.model.grid[nx][ny] = 2

    def spawn_food(self):
        grid = self.model.grid
        empty_cells = [(x, y) for x in range(self.model.rows) for y in range(self.model.cols) if grid[x][y] == 0]

        if not empty_cells:
            return # Nowhere to spawn food

        x, y = random.choice(empty_cells)
        new_food = Food(x, y, model=self.model, weight=random.randint(1, 15))
        print(f"Spawning food at ({x}, {y}) with {len(new_food.cells)} cells")

        self.model.food.append(new_food)

    
    def consume_food(self, start_x, start_y):
        print(f"Consuming food at {start_x}, {start_y}")
        grid = self.model.grid
        visited = set()
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            visited.add((x, y))

            if grid[x][y] == 1:
                grid[x][y] = 2  # Convert food to slime

                # Explore adjacent food
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.model.rows and 0 <= ny < self.model.cols:
                        if grid[nx][ny] == 1:
                            queue.append((nx, ny))

        # Remove fully consumed food blobs
        for food in self.model.food[:]:
            for cell in food.cells:
                if grid[cell[0]][cell[1]] == 2:
                    if all(grid[x][y] == 2 for x, y in food.cells):
                        self.model.food.remove(food)
                    break
        
        print(f"food at {start_x}, {start_y} is being consumed")
