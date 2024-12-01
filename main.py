import pygame
from random import choice

RES = WIDTH, HEIGHT = 1402, 802
TILE = 100
cols, rows = WIDTH // TILE, HEIGHT // TILE

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, "bottom": True, "left": True, "right": True}
        self.visited = False

    def draw(self):
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


grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []

while True:
    sc.fill(pygame.Color("darkslategrey"))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    [cell.draw() for cell in grid_cells]

    pygame.display.flip()
    pygame.time.Clock().tick(30)
