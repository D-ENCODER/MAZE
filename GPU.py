import pygame
import cupy as cp
from random import choice
import datetime

RES = WIDTH, HEIGHT = 1500, 880
TILE = 30
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()

# Grid initialization using CuPy
walls = cp.ones((rows, cols, 4), dtype=bool)  # 4 walls: top, bottom, left, right
visited = cp.zeros((rows, cols), dtype=bool)

# Precomputed neighbor offsets for GPU parallelism
offsets = cp.array([[0, -1], [1, 0], [0, 1], [-1, 0]])  # top, right, bottom, left

def draw_cell(x, y, color):
    px, py = x * TILE, y * TILE
    pygame.draw.rect(sc, color, (px, py, TILE, TILE))

def draw_walls(x, y):
    px, py = x * TILE, y * TILE
    cell_walls = walls[y, x]
    if cell_walls[0]:  # top
        pygame.draw.line(sc, pygame.Color("darkorange"), (px, py), (px + TILE, py), 2)
    if cell_walls[1]:  # bottom
        pygame.draw.line(sc, pygame.Color("darkorange"), (px, py + TILE), (px + TILE, py + TILE), 2)
    if cell_walls[2]:  # left
        pygame.draw.line(sc, pygame.Color("darkorange"), (px, py), (px, py + TILE), 2)
    if cell_walls[3]:  # right
        pygame.draw.line(sc, pygame.Color("darkorange"), (px + TILE, py), (px + TILE, py + TILE), 2)

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

current_cell = (0, 0)
stack = []
running = True
initial = datetime.datetime.now()

visited[current_cell[1], current_cell[0]] = True

while running:
    sc.fill(pygame.Color("darkslategrey"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    # Draw the grid
    for y in range(rows):
        for x in range(cols):
            if visited[y, x]:
                draw_cell(x, y, pygame.Color("black"))
            draw_walls(x, y)

    # Highlight the current cell
    draw_cell(current_cell[0], current_cell[1], pygame.Color("saddlebrown"))

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
        print("completed")
        difference = datetime.datetime.now() - initial
        minutes = divmod(difference.total_seconds(), 60)
        print("Minutes: " + str(minutes[0]) + " Seconds: " + str(minutes[1]))

    pygame.display.flip()
