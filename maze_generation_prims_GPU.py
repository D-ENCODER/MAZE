import random
import numpy as np
from numba import cuda, types

# Initialize the grid dimensions
rows, cols = 20, 20  # Adjust as needed


# Numba CUDA kernel to generate the maze using Prim's Algorithm
@cuda.jit
def generate_maze_kernel(visited, walls, directions, rows, cols):
    # Thread indices
    tx, ty = cuda.grid(2)

    # List of unvisited neighbors (we will store the neighbors in a fixed-size array)
    neighbors_x = cuda.local.array(4, dtype=numba.int32)  # Array size 4, 4 possible directions
    neighbors_y = cuda.local.array(4, dtype=numba.int32)

    # Initialize the neighbor count
    num_neighbors = 0

    # Check bounds and if the current cell is unvisited
    if 0 <= tx < rows and 0 <= ty < cols and not visited[tx, ty]:
        # Randomly add neighbors
        if tx - 1 >= 0 and not visited[tx - 1, ty]:
            neighbors_x[num_neighbors] = tx - 1
            neighbors_y[num_neighbors] = ty
            num_neighbors += 1
        if tx + 1 < rows and not visited[tx + 1, ty]:
            neighbors_x[num_neighbors] = tx + 1
            neighbors_y[num_neighbors] = ty
            num_neighbors += 1
        if ty - 1 >= 0 and not visited[tx, ty - 1]:
            neighbors_x[num_neighbors] = tx
            neighbors_y[num_neighbors] = ty - 1
            num_neighbors += 1
        if ty + 1 < cols and not visited[tx, ty + 1]:
            neighbors_x[num_neighbors] = tx
            neighbors_y[num_neighbors] = ty + 1
            num_neighbors += 1

        # Pick a random neighbor and mark it as visited
        if num_neighbors > 0:
            idx = random.randint(0, num_neighbors - 1)
            nx, ny = neighbors_x[idx], neighbors_y[idx]
            visited[nx, ny] = True
            # Encode (nx, ny) as a single integer to store in walls
            walls[tx, ty] = nx * cols + ny  # Encoding pair (nx, ny) into a single integer


# Host function to set up and run the kernel
def generate_maze(rows, cols):
    visited = np.zeros((rows, cols), dtype=np.bool_)

    # Store walls as a single integer representing (nx, ny) encoded as nx * cols + ny
    walls = np.zeros((rows, cols), dtype=np.int32)  # Use a fixed-size type (int32)

    directions = np.array([(-1, 0), (1, 0), (0, -1), (0, 1)])  # Directions: up, down, left, right

    # Copy arrays to device memory
    visited_device = cuda.to_device(visited)
    walls_device = cuda.to_device(walls)
    directions_device = cuda.to_device(directions)

    # Set up grid and block sizes for the kernel
    threads_per_block = (16, 16)
    blocks_per_grid = (int(np.ceil(rows / threads_per_block[0])), int(np.ceil(cols / threads_per_block[1])))

    # Launch kernel
    generate_maze_kernel[blocks_per_grid, threads_per_block](visited_device, walls_device, directions_device, rows,
                                                             cols)

    # Copy results back to host
    visited = visited_device.copy_to_host()
    walls = walls_device.copy_to_host()

    return visited, walls


# Main function to run the maze generation
if __name__ == "__main__":
    visited_final, walls_final = generate_maze(rows, cols)

    print("Maze Generated with GPU (Prims Algorithm):")
    print(visited_final)
    print(walls_final)
