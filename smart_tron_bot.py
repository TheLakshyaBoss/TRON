import random
import queue

def get_move(grid, my_pos, my_id, opp_pos):
    """
    Advanced Voronoi-based Bot with Safety Heuristics.
    1. Maximize Territory (Voronoi).
    2. Maximize Openness (Don't hug walls if not needed).
    """
    cols = len(grid)
    rows = len(grid[0])
    
    possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
    random.shuffle(possible_moves)
    
    best_move = possible_moves[0]
    best_score = -float('inf')
    
    # 1. Evaluate each valid move
    valid_moves = []
    
    for move in possible_moves:
        nx, ny = my_pos
        if move == "UP": ny -= 1
        elif move == "DOWN": ny += 1
        elif move == "LEFT": nx -= 1
        elif move == "RIGHT": nx += 1
        
        # Check immediate collision
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] == 0:
            valid_moves.append((move, nx, ny))
            
    if not valid_moves:
        return "UP" # No moves, accept defeat
        
    # 2. Run Simulations
    for move, nx, ny in valid_moves:
        
        # A. Voronoi Score: How much territory can I secure?
        territory_score = calculate_voronoi_territory(grid, (nx, ny), opp_pos)
        
        # B. Openness Bonus: How many open neighbors does this new spot have?
        # This prevents the bot from entering tunnels/corners unnecessarily.
        open_neighbors = count_open_neighbors(grid, nx, ny)
        
        # Final Score = Territory + small bonus for open space
        # We weigh territory much higher (1.0) than openness (0.1)
        total_score = territory_score + (open_neighbors * 0.5)
        
        if total_score > best_score:
            best_score = total_score
            best_move = move
            
    return best_move

def count_open_neighbors(grid, cx, cy):
    """Counts how many empty cells are adjacent to (cx, cy)."""
    cols = len(grid)
    rows = len(grid[0])
    count = 0
    moves = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]
    for nx, ny in moves:
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] == 0:
            count += 1
    return count

def calculate_voronoi_territory(grid, my_start, opp_start):
    """
    Runs a simultaneous BFS from both players.
    Returns the count of cells that 'my_start' reaches BEFORE 'opp_start'.
    """
    # --- FIX: Convert inputs to tuples to ensure they are hashable for the set ---
    my_start = tuple(my_start)
    opp_start = tuple(opp_start)

    cols = len(grid)
    rows = len(grid[0])
    
    # Q stores: (x, y, owner_id)
    # owner_id: 1 = Me, 2 = Opponent
    q = queue.Queue()
    q.put((my_start[0], my_start[1], 1))
    q.put((opp_start[0], opp_start[1], 2))
    
    visited = set()
    visited.add(my_start)
    visited.add(opp_start)
    
    my_territory = 0
    
    # Run BFS
    # Increased max_iterations to scan the WHOLE board (900 cells + margin)
    iterations = 0
    max_iterations = 2000 
    
    while not q.empty() and iterations < max_iterations:
        cx, cy, owner = q.get()
        iterations += 1
        
        if owner == 1:
            my_territory += 1
            
        neighbors = [
            (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)
        ]
        
        for nx, ny in neighbors:
            if 0 <= nx < cols and 0 <= ny < rows:
                if grid[nx][ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.put((nx, ny, owner))
                    
    return my_territory