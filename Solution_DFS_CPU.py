import os
from random import choice
import datetime
from PIL import Image, ImageDraw

# Constants
WIDTH, HEIGHT = 2000, 1000
TILE = 60
cols, rows = WIDTH // TILE, HEIGHT // TILE

def check_cells(x, y):
    find_index = x + y * cols
    if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
        return False
    return grid_cells[find_index]

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, "bottom": True, "left": True, "right": True}
        self.visited = False
        self.__neighbors__ = []

    def draw(self, draw, highlight=False):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            draw.rectangle([x, y, x + TILE, y + TILE], fill="black")

        # Draw the top, left, bottom, and right walls if present
        if self.walls["top"]:
            draw.line([x, y, x + TILE, y], fill="darkorange", width=1)
        if self.walls["left"]:
            draw.line([x, y, x, y + TILE], fill="darkorange", width=1)
        if self.walls["bottom"] or self.y == rows - 1:
            draw.line([x, y + TILE, x + TILE, y + TILE], fill="darkorange", width=1)
        if self.walls["right"] or self.x == cols - 1:
            draw.line([x + TILE, y, x + TILE, y + TILE], fill="darkorange", width=1)

        if highlight:
            draw.rectangle([x + 2, y + 2, x + TILE - 2, y + TILE - 2], fill="red")

    def check_neighbors(self):
        self.__neighbors__ = []
        top = check_cells(self.x, self.y - 1)
        right = check_cells(self.x + 1, self.y)
        bottom = check_cells(self.x, self.y + 1)
        left = check_cells(self.x - 1, self.y)
        if top and not top.visited:
            self.__neighbors__.append(top)
        if right and not right.visited:
            self.__neighbors__.append(right)
        if bottom and not bottom.visited:
            self.__neighbors__.append(bottom)
        if left and not left.visited:
            self.__neighbors__.append(left)
        return choice(self.__neighbors__) if self.__neighbors__ else False


def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

# Save a frame for the current maze state
def save_maze_frame(grid_cells, filename):
    img = Image.new("RGB", (WIDTH, HEIGHT), "grey")
    draw = ImageDraw.Draw(img)
    for cell in grid_cells:
        cell.draw(draw)
    img.save(filename)

# Generate the maze with frames
def generate_maze_with_frames():
    global grid_cells, stack, current_cell, running, initial
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    stack = []
    running = True
    initial = datetime.datetime.now()

    frame_counter = 0
    os.makedirs("frames", exist_ok=True)

    while running:
        current_cell.visited = True
        next_cell = current_cell.check_neighbors()
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()
        elif len(stack) == 0:
            running = False

        frame_counter += 1
        if frame_counter % 10 == 0:  # Save every 10th frame
            save_maze_frame(grid_cells, f"frames/frame_{frame_counter:05d}.png")

# Solve the maze with frames
def solve_maze_with_frames():
    visited = set()
    path = []
    os.makedirs("solution_frames", exist_ok=True)

    def dfs(x, y):
        if (x, y) in visited or x < 0 or y < 0 or x >= cols or y >= rows:
            return False
        index = x + y * cols
        current = grid_cells[index]
        visited.add((x, y))
        path.append((x, y))

        # Save a frame with the current path
        save_solution_frame(path, f"solution_frames/sol_frame_{len(path):05d}.png")

        # Check if reached the bottom-right cell
        if x == cols - 1 and y == rows - 1:
            return True

        # Try moving in each possible direction
        neighbors = [
            (x, y - 1, "top", "bottom"),
            (x + 1, y, "right", "left"),
            (x, y + 1, "bottom", "top"),
            (x - 1, y, "left", "right"),
        ]
        for nx, ny, wall_from, wall_to in neighbors:
            if (nx, ny) not in visited:
                neighbor_index = nx + ny * cols
                if 0 <= nx < cols and 0 <= ny < rows and not grid_cells[index].walls[wall_from]:
                    if dfs(nx, ny):
                        return True

        path.pop()  # Backtrack
        return False

    dfs(0, 0)

# Save a frame with the solution path
def save_solution_frame(path, filename):
    img = Image.new("RGB", (WIDTH, HEIGHT), "grey")
    draw = ImageDraw.Draw(img)

    for cell in grid_cells:
        cell.draw(draw)

    for (x, y) in path:
        cx, cy = x * TILE, y * TILE
        draw.rectangle([cx + 2, cy + 2, cx + TILE - 2, cy + TILE - 2], fill="blue")

    img.save(filename)

if __name__ == "__main__":
    generate_maze_with_frames()  # Generate maze
    solve_maze_with_frames()     # Solve maze
