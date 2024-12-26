# Author: Het Chiragkumar Joshi
# Contains Maze generation algorithm using DFS (Depth First Search)

import pygame
from random import choice
import datetime

RES = WIDTH, HEIGHT = 1500, 880
TILE = 5
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock


def check_cells(x, y):
    find_index = x + y * cols
    if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
        return False
    return grid_cells[find_index]


class Cell:
    """
    This class defines the basic features of a cell on a grid. Features include creating GUI for cells and draw
    """

    def __init__(self, x, y):
        """
        Constructor that initializes the cell parameters such as x, y, walls and visited.
        :param int x: Index on X-Axis
        :param int y: Index on Y-Axis
        :var self.walls: Depicts the walls of maze.
        :var self.visited: Bool to mark if the cell is visited or not
        :returns: None
        """
        self.x = x
        self.y = y
        self.walls = {'top': True, "bottom": True, "left": True, "right": True}
        self.visited = False
        self.__neighbors__ = []

    def draw_head_cell(self):
        """
        This function creates GUI for a cell on the canvas of the pygame.
        :return: None
        """
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('saddlebrown'), (x + 2, y + 2, TILE - 2, TILE - 2))

    def draw(self):
        """
        This function creates GUI for the walls using the **walls** dictionary.
        :return: None
        """
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color("black"), (x, y, TILE, TILE))

        if self.walls["top"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x, y), (x + TILE, y), 2)

        if self.walls["bottom"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x + TILE, y + TILE), (x, y + TILE), 2)

        if self.walls["left"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x, y + TILE), (x, y), 2)

        if self.walls["right"]:
            pygame.draw.line(sc, pygame.Color("darkorange"), (x + TILE, y), (x + TILE, y + TILE), 2)

    def check_neighbors(self):
        """

        :return: None
        """
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


grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []
running = True
initial = datetime.datetime.now()

while running:
    sc.fill(pygame.Color("darkslategrey"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    [cell.draw() for cell in grid_cells]
    current_cell.visited = True
    current_cell.draw_head_cell()
    next_cell = current_cell.check_neighbors()
    if next_cell:
        next_cell.visited = True
        stack.append(current_cell)
        remove_walls(current_cell, next_cell)
        current_cell = next_cell
    elif stack:
        current_cell = stack.pop()
    elif len(stack) == 0:
        # running = False
        print("completed")
        difference = datetime.datetime.now() - initial
        minutes = divmod(difference.total_seconds(), 60)
        print("Minutes: " + str(minutes[0]) + " Seconds: " + str(minutes[1]))
    pygame.display.flip()
