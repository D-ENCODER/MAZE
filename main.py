from random import choice
import datetime
from PIL import Image, ImageDraw

# Constants
WIDTH, HEIGHT = 2000, 1000
TILE = 5
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

    def draw_head_cell(self, draw):
        x, y = self.x * TILE, self.y * TILE
        draw.rectangle([x + 2, y + 2, x + TILE - 2, y + TILE - 2], fill="saddlebrown")

    def draw(self, draw):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            draw.rectangle([x, y, x + TILE, y + TILE], fill="black")

        if self.walls["top"]:
            draw.line([x, y, x + TILE, y], fill="darkorange", width=1)
        if self.walls["bottom"]:
            draw.line([x + TILE, y + TILE, x, y + TILE], fill="darkorange", width=1)
        if self.walls["left"]:
            draw.line([x, y + TILE, x, y], fill="darkorange", width=1)
        if self.walls["right"]:
            draw.line([x + TILE, y, x + TILE, y + TILE], fill="darkorange", width=1)

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

# Function to generate the maze
def generate_maze():
    global grid_cells, stack, current_cell, running, initial
    # Initialize grid and start maze generation
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    stack = []
    running = True
    initial = datetime.datetime.now()

    while running:
        # Mark the current cell as visited
        current_cell.visited = True

        # Check for neighbors and move to the next cell if possible
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
            print("Maze completed")
            difference = datetime.datetime.now() - initial
            minutes = divmod(difference.total_seconds(), 60)
            print("Minutes: " + str(minutes[0]) + " Seconds: " + str(minutes[1]))

# Function to generate an image from the maze
def maze_to_image():
    # Create a blank image with white background
    img = Image.new("RGB", (WIDTH, HEIGHT), "grey")
    draw = ImageDraw.Draw(img)

    # Draw the cells and walls
    for cell in grid_cells:
        cell.draw_head_cell(draw)
        cell.draw(draw)

    # Save the final maze image
    img.save('generated_maze_CPU.png')
    img.show()

if __name__ == "__main__":
    generate_maze()   # Generate the maze
    maze_to_image()   # Convert the maze to an image
