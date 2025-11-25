TRON is a high-performance simulation of the classic arcade game "Tron" (Light Cycles). Unlike standard clones, this project focuses on Artificial Intelligence, featuring a custom-built bot engine that uses Voronoi Space Partitioning to trap opponents in real-time.

<img width="1407" height="955" alt="home" src="https://github.com/user-attachments/assets/7ae5628a-9008-48e8-b12c-3c4b200e3e73" />

The Intelligence
    This isn't Machine Learning—it's pure, aggressive Graph Theory. The bot (smart_tron_bot.py) calculates the optimal move 60 times per second using three layers of logic:

1. Voronoi Territory Control

    Instead of just looking for open space, the bot asks: "If I move Left, do I own more of the board than my opponent?"
    The Concept: We treat the game grid as a graph.
    The Execution: A Simultaneous Breadth-First Search (BFS) is launched from both the Bot's potential future position and the Opponent's current position.
    The Metric: If the Bot can reach a specific cell faster than the Opponent, that cell is counted as "Safe Territory."
    The Decision: The bot chooses the move (Up, Down, Left, Right) that maximizes its exclusive territory (Voronoi Region), effectively squeezing the opponent into a smaller space.

3. Tunnel Vision Prevention
   
    It's not enough to see open space; you have to reach it. The bot filters out "air pockets"—areas that look empty but are actually cut off by walls or trails—so it never steers into a dead end that traps it later.

5. Instant Safety Checks
   
    Before running the heavy math, a lightweight filter ensures the bot never makes an obviously suicidal move, like turning directly into a wall or a trail.

Game Modes : 

1. The Arena (arena.py)
   
    A fully automated tournament system.
    Watch AI vs AI: Two instances of the Smart Bot battle for supremacy.
    Live Stats: Real-time sidebar tracking Win Rates, Match Counts, and Scores.
    Configuration: Set custom bot names and match limits via the UI.

   <img width="1413" height="945" alt="result" src="https://github.com/user-attachments/assets/a8fdaf35-b9a4-48a7-b35a-0bfcebb7db1c" />


3. Human vs Machine (game.py)
   
    Test your skills against the algorithm.

Controls: WASD or Arrow Keys.

Challenge: Can you outsmart a bot that calculates territory control mathematically?
