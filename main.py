import random
from datetime import datetime

# Main function to solve the grid by connecting all pairs
def solve_grid(grid, pairs): 
    N = len(grid) #Size of the grid
    log = [] # List to store logs of path attempts
    chosen_routes = [None]*len(pairs)  # To store the chosen path for each pair

    # Log the current attempt and the grid state
    def log_attempt(message): 
        log.append(message + "\n")
        for row in grid:
            # Convert grid row to a readable string (numbers or dots for empty cells)
            log.append(" ".join(str(c) if c != 0 else "." for c in row) + "\n")
        log.append("\n")

    # Save the log to a txt file with timestamp
    def save_log(log):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grid_attempts_{timestamp}.txt"
        with open(filename, "w") as file:
            file.write("".join(log)) # Write all logs to the file
        print(f"\nLog saved to {filename}")

    # Guarantee that a cell (x, y) is within grid bounds
    def is_valid(x, y):
        return 0 <= x < N and 0 <= y < N

    # Check if the entire grid is filled (no zeros left)
    def is_full():
        return all(grid[i][j] != 0 for i in range(N) for j in range(N))

    # Find all possible paths between a start and an end point -> Depth First Search (DFS)
    def find_all_paths_for_pair(sx, sy, ex, ey, label):
        all_paths = [] # Store all valid paths

        # Backtracking function to diving deeply into one possible direction -> Recursive Exploration -> Depth First Search (DFS)
        def backtrack(x, y, steps, visited, path):
            # Basically if the endpoint is reached, save the path
            if x == ex and y == ey:
                if steps > 0: # A valid path must contain at least one step
                    all_paths.append(path[:]) # Append a copy of the path
                return
            
            # Explore four possible directions: right, down, left, up
            directions = [(0,1),(1,0),(0,-1),(-1,0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy # Next cell coordinates
                # If the move is valid and the cell has not been visited yet
                if is_valid(nx, ny) and (nx, ny) not in visited:
                    # Only proceed if the cell is either empty or the endpoint
                    if (nx, ny) == (ex, ey) or grid[nx][ny] == 0:
                        visited.add((nx, ny)) # Mark the cell as visited
                        # Avoid marking the endpoint
                        if (nx, ny) != (ex, ey):
                            path.append((nx, ny)) # Add cell to the path
                            grid[nx][ny] = label # Temporarily mark grid
                        backtrack(nx, ny, steps + (0 if (nx, ny) == (ex, ey) else 1), visited, path)
                        # Backtrack: Undo the changes made during exploration
                        if (nx, ny) != (ex, ey):
                            grid[nx][ny] = 0 # Unmark grid cell
                            path.pop() # Remove the cell from the path
                        visited.remove((nx, ny)) # Mark the cell as unvisited

        visited = {(sx, sy)} # Start with the source cell as visited
        backtrack(sx, sy, 0, visited, []) # Start backtracking
        return all_paths

    # To solve all pairs
    def solve_all_pairs(index):
        # Basically if all pairs are solved, check if the grid is full
        if index == len(pairs):
            return is_full()

        # Extract start and end points for the current pair
        (sx, sy), (ex, ey) = pairs[index]
        label = grid[sx][sy] # Label of the current pair
        log_attempt(f"Attempting to connect pair {label} from ({sx},{sy}) to ({ex},{ey})")

        # Backup the current grid state before attempting to solve this pair
        backup = [row[:] for row in grid]
        # Find all possible paths for the current pair
        all_routes = find_all_paths_for_pair(sx, sy, ex, ey, label)

        # Try each route for the current pair
        for route in all_routes:
            # Apply the route 
            for (px, py) in route:
                grid[px][py] = label
            chosen_routes[index] = route[:] # Save the chosen route

            # Call to solve the next pair
            if solve_all_pairs(index + 1):
                return True # Return True If a solution is found
            # Undo if the solution fails
            chosen_routes[index] = None
            for i in range(N):
                for j in range(N):
                    grid[i][j] = backup[i][j] # Restore grid to previous state

        return False  # Return False if no valid path is found for this pair

    # Calculate Manhattan distance between two points, 
    # Manhattan distance is often more suitable for grid-based systems or high-dimensional data
    def manhattan_dist(p):
        (ax, ay), (bx, by) = p
        return abs(ax - bx) + abs(ay - by) # Sum of absolute differences in x and y

    # Sort pairs by Manhattan distance (Heuristic)
    pairs.sort(key=manhattan_dist, reverse=True)

    # Start solving from the first pair
    if solve_all_pairs(0):
        log.append("\nSolution found!\n")
        save_log(log) # Save the log

        # Map labels to letters output
        label_to_letter = {1: "A", 2: "B", 3: "C"}

        # Insert arrows using the storage routes
        for i, ((sx, sy), (ex, ey)) in enumerate(pairs):
            label = grid[sx][sy]
            route = chosen_routes[i]
            full_path = [(sx, sy)] + route + [(ex, ey)] # Full path of the pair
            letter = label_to_letter.get(label, "X") # Map label to letter

            # Add arrows for path directions
            for idx in range(1, len(full_path)-1):
                x1, y1 = full_path[idx-1]
                x2, y2 = full_path[idx]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 1 and dy == 0: # Down
                    arrow = "↓" 
                elif dx == -1 and dy == 0: # Up
                    arrow = "↑" 
                elif dx == 0 and dy == 1: # Right
                    arrow = "→" 
                elif dx == 0 and dy == -1: # Left
                    arrow = "←"
                else:
                    arrow = "?" # unexpected cases
                # Store arrow as tuple (arrow, letter) to know which path is
                grid[x2][y2] = (arrow, letter)

        # Replace endpoints with formatted labels "A1","A2","B1","B2","C1","C2"
        for i, ((sx, sy), (ex, ey)) in enumerate(pairs, start=1):
            label = grid[sx][sy]
            # Label is still integer in endpoint, get letter
            letter = label_to_letter.get(label, "X")
            grid[sx][sy] = f"{letter}1"
            grid[ex][ey] = f"{letter}2"

        return grid # Return the solved grid
    else:
        log.append("\nNo complete solution found.\n")
        save_log(log) # Save failed attempts
        return "No Solution"

# Initialize the grid and pairs based on user input
def initialize_grid_with_pairs():
    N = int(input("Inform the grid lenght N: "))

    if N == 5: # For 5x5 grid, offer default models
        escolha = input("Do you want to use default (D) or generate generic pairs (G)? ").strip().upper()
        if escolha == "D":
            modelo = int(input("Choose the model (1 to 6): "))
            grid = [[0 for _ in range(N)] for _ in range(N)]

            # Predefined models for the 5x5 grid
            if modelo == 1:
                # 1st Model:
                # A1: (0, 0), A2: (1, 4)
                # B1: (2, 0), B2: (2, 4)
                # C1: (3, 0), C2: (4, 4)
                grid[0][0] = 1
                grid[1][4] = 1
                grid[2][0] = 2
                grid[2][4] = 2
                grid[3][0] = 3
                grid[4][4] = 3
                pairs = [((0,0),(1,4)), ((2,0),(2,4)), ((3,0),(4,4))]

            elif modelo == 2:
                # 2nd Model:
                # A1: (1,1), A2: (1,2)
                # B1: (2,2), B2: (0,3)
                # C1: (4,0), C2: (2,4)
                grid[1][1] = 1
                grid[1][2] = 1
                grid[2][2] = 2
                grid[0][3] = 2
                grid[4][0] = 3
                grid[2][4] = 3
                pairs = [((1,1),(1,2)), ((2,2),(0,3)), ((4,0),(2,4))]

            elif modelo == 3:
                # 3rd Model:
                # A1: (0,0), A2: (4,1)
                # B1: (2,0), B2: (2,3)
                # C1: (4,2), C2: (4,4)
                grid[0][0] = 1
                grid[4][1] = 1
                grid[2][0] = 2
                grid[2][3] = 2
                grid[4][2] = 3
                grid[4][4] = 3
                pairs = [((0,0),(4,1)), ((2,0),(2,3)), ((4,2),(4,4))]

            elif modelo == 4:
                # 4th Model:
                # A1: (3,0), A2: (3,3)
                # B1: (1,0), B2: (2,2)
                # C1: (0,0), C2: (4,0)
                grid[3][0] = 1
                grid[3][3] = 1
                grid[1][0] = 2
                grid[2][2] = 2
                grid[0][0] = 3
                grid[4][0] = 3
                pairs = [((3,0),(3,3)), ((1,0),(2,2)), ((0,0),(4,0))]

            elif modelo == 5:
                # 5th Model:
                # A1: (1,1), A2: (1,3)
                # B1: (1,0), B2: (2,3)
                # C1: (0,0), C2: (4,4)
                grid[1][1] = 1
                grid[1][3] = 1
                grid[1][0] = 2
                grid[2][3] = 2
                grid[0][0] = 3
                grid[4][4] = 3
                pairs = [((1,1),(1,3)), ((1,0),(2,3)), ((0,0),(4,4))]

            elif modelo == 6:
                # 6th Model (Solution Requested):
                # A1: (0,0), A2: (4,1)
                # B1: (2,0), B2: (2,1)
                # C1: (4,2), C2: (4,4)
                grid[0][0] = 1
                grid[4][1] = 1
                grid[2][0] = 2
                grid[2][1] = 2
                grid[4][2] = 3
                grid[4][4] = 3
                pairs = [((0,0),(4,1)), ((2,0),(2,1)), ((4,2),(4,4))]

            # Default Model 
            else:
                print("Invalid model! Using model 1 as default.")
                grid[0][0] = 1
                grid[1][4] = 1
                grid[2][0] = 2
                grid[2][4] = 2
                grid[3][0] = 3
                grid[4][4] = 3
                pairs = [((0,0),(1,4)), ((2,0),(2,4)), ((3,0),(4,4))]

            return grid, pairs
        else:
            # Generate random pairs for 5x5 grid
            return generate_random_pairs(N)
    else:
        # Generate random pairs for other grid sizes
        return generate_random_pairs(N)

# Generate random pairs for grids larger than 5x5
def generate_random_pairs(N):
    global pairs
    grid = [[0 for _ in range(N)] for _ in range(N)]
    num_pairs = int(input("How many pairs do you want to use? "))
    used_positions = set()
    label = 1

    pairs = []

    # Loop to generate each pair
    for _ in range(num_pairs): 
        # First endpoint
        while True:
            sx, sy = random.randint(0, N-1), random.randint(0, N-1)
            if (sx, sy) not in used_positions and grid[sx][sy] == 0:
                break
        grid[sx][sy] = label
        used_positions.add((sx, sy))

        # Second endpoint
        while True:
            ex, ey = random.randint(0, N-1), random.randint(0, N-1)
            if (ex, ey) not in used_positions and grid[ex][ey] == 0 and (ex, ey) != (sx, sy):
                break
        grid[ex][ey] = label
        used_positions.add((ex, ey))

        pairs.append(((sx, sy), (ex, ey))) # Add the pair
        label += 1 # Increment label for the next pair

    return grid, pairs

# Print the grid with colors and arrows for paths
def print_grid(grid):
    # Colors:
    # A (red) = \033[31m
    # B (green) = \033[32m
    # C (blue) = \033[34m
    # Endpoints follow the color of the initial letter
    # Arrows also in the corresponding color    
    letter_colors = {
        'A': "\033[31m",
        'B': "\033[32m",
        'C': "\033[34m"
    }

    # Display grid using arrows and labels for endpoints
    for row in grid:
        row_str = []
        for c in row:
            if isinstance(c, tuple):
                # c = (arrow, letter)
                arrow, letter = c
                color = letter_colors.get(letter, "\033[36m")
                row_str.append(f"{color}{arrow}\033[0m")

            elif isinstance(c, str):
                # Can be endpoint (A1,A2,B1,B2,C1,C2)
                # Starts with A,B or C
                letter = c[0]
                color = letter_colors.get(letter, "\033[36m")
                row_str.append(f"{color}{c}\033[0m")

            elif isinstance(c, int) and c != 0:
                # If still has any ints, just cyan
                row_str.append(f"\033[36m{c}\033[0m")
            else:
                row_str.append(".")
        print("   ".join(row_str)) # Print formatted row

# Entry point for the program
if __name__ == "__main__":
    pairs = []
    grid, pairs = initialize_grid_with_pairs() # Initialize the grid and pairs
    print("\nInitial Grid:")
    print_grid(grid) # Display the initial grid

    start_time = datetime.now() # Record start time

    solution = solve_grid(grid, pairs) # Solve the grid

    end_time = datetime.now() # Record end time

    print("\nExecution Time: ", end_time - start_time) # Print time

    if solution == "No Solution":
        print("\nNo valid solution exists")
    else:
        print("\nSolved Grid:")
        print_grid(solution) # Print the solved grid