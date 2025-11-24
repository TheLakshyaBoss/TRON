import random

# We added 'opp_pos' to the arguments to match the new Arena standard
def get_move(grid, my_pos, my_id, opp_pos):
    x, y = my_pos
    cols = len(grid)
    rows = len(grid[0])
    
    moves = ["UP", "DOWN", "LEFT", "RIGHT"]
    safe_moves = []
    
    # 1. First, find all moves that don't kill us INSTANTLY
    for move in moves:
        nx, ny = x, y
        if move == "UP": ny -= 1
        elif move == "DOWN": ny += 1
        elif move == "LEFT": nx -= 1
        elif move == "RIGHT": nx += 1
        
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] == 0:
            safe_moves.append((move, nx, ny))
            
    # 2. Lookahead 1 step to avoid dead ends
    not_dumb_moves = []
    
    for move, nx, ny in safe_moves:
        future_exits = 0
        possible_next_steps = [
            (nx, ny-1), (nx, ny+1), (nx-1, ny), (nx+1, ny)
        ]
        
        for fx, fy in possible_next_steps:
            if 0 <= fx < cols and 0 <= fy < rows:
                if grid[fx][fy] == 0:
                    future_exits += 1
        
        if future_exits > 0:
            not_dumb_moves.append(move)
            
    if not_dumb_moves:
        return random.choice(not_dumb_moves)
    elif safe_moves:
        return random.choice([m[0] for m in safe_moves]) 
    else:
        return "UP"