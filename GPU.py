import cupy as cp
import numpy as np
from random import choice
import datetime
from PIL import Image

# Constants
RES = WIDTH, HEIGHT = 2000, 1000
TILE = 5
cols, rows = WIDTH // TILE, HEIGHT // TILE

# Colors
BLACK = (0, 0, 0)  # black
DARK_ORANGE = (255, 140, 0)  # darkorange

# Grid initialization using CuPy
walls = cp.ones((rows, cols, 4), dtype=bool)  # 4 walls: top, bottom, left, right
visited = cp.zeros((rows, cols), dtype=bool)

# Precomputed neighbor offsets for GPU parallelism
offsets = cp.array([[0, -1], [1, 0], [0, 1], [-1, 0]])  # top, right, bottom, left

def remove_walls(current, next):
    cx, cy = current
    nx, ny = next
    dx, dy = nx - cx, ny - cy
    if dx == 1:  # right
        walls[cy, cx, 3] = False
        walls[ny, nx, 2] = False
    elif dx == -1:  # left
        walls[cy, cx, 2] = False
        walls[ny, nx, 3] = False
    if dy == 1:  # bottom
        walls[cy, cx, 1] = False
        walls[ny, nx, 0] = False
    elif dy == -1:  # top
        walls[cy, cx, 0] = False
        walls[ny, nx, 1] = False

def check_neighbors_gpu(x, y):
    global offsets
    x_offsets = offsets[:, 0] + x
    y_offsets = offsets[:, 1] + y
    valid = (x_offsets >= 0) & (x_offsets < cols) & (y_offsets >= 0) & (y_offsets < rows)
    x_neighbors, y_neighbors = x_offsets[valid], y_offsets[valid]

    visited_neighbors = visited[y_neighbors, x_neighbors]
    unvisited_indices = cp.where(~visited_neighbors)[0]

    if len(unvisited_indices) > 0:
        chosen_index = choice(unvisited_indices.get())
        return int(x_neighbors[chosen_index]), int(y_neighbors[chosen_index])
    return None

def generate_maze():
    current_cell = (0, 0)
    stack = []
    visited[current_cell[1], current_cell[0]] = True
    initial = datetime.datetime.now()

    while len(stack) > 0 or current_cell is not None:
        # Maze generation logic
        next_cell = check_neighbors_gpu(*current_cell)
        if next_cell:
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
            visited[current_cell[1], current_cell[0]] = True
        elif stack:
            current_cell = stack.pop()
        elif len(stack) == 0:
            print("Maze completed")
            difference = datetime.datetime.now() - initial
            minutes = divmod(difference.total_seconds(), 60)
            print("Minutes: " + str(minutes[0]) + " Seconds: " + str(minutes[1]))
            break

def maze_to_image():
    # Convert walls to a binary image representation
    maze_image = np.ones((rows * TILE, cols * TILE, 3), dtype=np.uint8) * BLACK[0]  # Default black background
    for y in range(rows):
        for x in range(cols):
            # Draw walls (4 walls)
            if walls[y, x, 0]:  # top wall
                maze_image[y * TILE, x * TILE:(x + 1) * TILE] = DARK_ORANGE  # darkorange for top wall
            if walls[y, x, 1]:  # bottom wall
                maze_image[(y + 1) * TILE - 1, x * TILE:(x + 1) * TILE] = DARK_ORANGE  # darkorange for bottom wall
            if walls[y, x, 2]:  # left wall
                maze_image[y * TILE:(y + 1) * TILE, x * TILE] = DARK_ORANGE  # darkorange for left wall
            if walls[y, x, 3]:  # right wall
                maze_image[y * TILE:(y + 1) * TILE, (x + 1) * TILE - 1] = DARK_ORANGE  # darkorange for right wall

            # Mark visited cells with black inside the cell
            if visited[y, x]:
                maze_image[y * TILE + 1:(y + 1) * TILE - 1, x * TILE + 1:(x + 1) * TILE - 1] = BLACK  # black for visited cells

    # Save the maze image
    img = Image.fromarray(maze_image)
    img.save('generated_maze_GPU.png')
    img.show()  # Optionally show the image

if __name__ == "__main__":
    generate_maze()
    maze_to_image()
