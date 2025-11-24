import pygame
import numpy as np
import sys
import time

# --- IMPORTS ---
import smart_tron_bot

# --- CONSTANTS ---
GAME_WIDTH = 600
SIDEBAR_WIDTH = 320
WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
HEIGHT = 600
GRID_SIZE = 20
COLS = GAME_WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE
MAX_MATCHES = 5

# COLORS
BLACK = (10, 10, 15)
NEON_GREEN = (0, 255, 0)   # Changed from NEON_BLUE
NEON_RED = (255, 50, 50)
DARK_GRAY = (40, 40, 50)
GRID_COLOR = (30, 30, 40)
SIDEBAR_BG = (20, 20, 25)
WHITE = (240, 240, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (180, 50, 255)

class TronGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 
        
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TRON: Human vs AI")
        self.clock = pygame.time.Clock()
        
        # --- SOUND ENGINE ---
        self.sounds_loaded = False
        try:
            pygame.mixer.music.load("./sounds/bg_music.mp3")
            pygame.mixer.music.set_volume(0.4) 
            pygame.mixer.music.play(-1) 
            
            self.snd_move = pygame.mixer.Sound("./sounds/move.wav")
            self.snd_crash = pygame.mixer.Sound("./sounds/game_over.wav")
            
            self.snd_move.set_volume(0.6)
            self.snd_crash.set_volume(0.8)
            self.sounds_loaded = True
            print("Audio loaded successfully.")
        except Exception as e:
            print(f"WARNING: Audio files not found in ./sounds/ folder. Game will run without sound. Error: {e}")
        
        # --- SMOOTHNESS SETTINGS ---
        self.move_delay = 80 
        self.last_move_time = pygame.time.get_ticks()
        
        # Fonts
        try:
            self.title_font = pygame.font.SysFont("impact", 40)
            self.header_font = pygame.font.SysFont("monospace", 28, bold=True)
            self.text_font = pygame.font.SysFont("monospace", 18)
            self.score_font = pygame.font.SysFont("monospace", 50, bold=True)
            self.status_font = pygame.font.SysFont("monospace", 22, bold=True)
        except:
             self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
             self.header_font = pygame.font.SysFont("Courier", 28, bold=True)
             self.text_font = pygame.font.SysFont("Courier", 18)
             self.score_font = pygame.font.SysFont("Courier", 50, bold=True)
             self.status_font = pygame.font.SysFont("Courier", 22, bold=True)
        
        # Game State
        self.match_count = 1
        self.p1_score = 0
        self.p2_score = 0
        self.tournament_over = False
        
        # Initialize First Round
        self.reset_round()

    def reset_round(self):
        self.grid = np.zeros((COLS, ROWS))
        
        # Starting positions
        self.p1_pos = [5, ROWS // 2]
        self.p2_pos = [COLS - 6, ROWS // 2]
        
        # Initial Directions
        self.p1_dir = "RIGHT" 
        self.p1_next_dir = "RIGHT" 
        
        # Mark start positions
        self.grid[self.p1_pos[0]][self.p1_pos[1]] = 1
        self.grid[self.p2_pos[0]][self.p2_pos[1]] = 2
        
        self.round_over = False
        self.winner = None
        self.last_move_time = pygame.time.get_ticks()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def play_sound(self, sound_type):
        if self.sounds_loaded:
            if sound_type == "move":
                self.snd_move.play()
            elif sound_type == "crash":
                self.snd_crash.play()

    def draw_sidebar(self):
        pygame.draw.rect(self.screen, SIDEBAR_BG, (GAME_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, DARK_GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 3)

        title_text = "HUMAN VS AI"
        title_surf = self.title_font.render(title_text, True, PURPLE)
        center_x = GAME_WIDTH + SIDEBAR_WIDTH // 2
        title_rect = title_surf.get_rect(center=(center_x, 50))
        self.screen.blit(title_surf, title_rect)

        controls = ["CONTROLS:", "WASD or Arrow Keys", "ESC to Quit"]
        for i, line in enumerate(controls):
            text = self.text_font.render(line, True, (150, 150, 150))
            rect = text.get_rect(center=(center_x, 100 + i*25))
            self.screen.blit(text, rect)

        # Player 1 (Human) - Updated to Green
        pygame.draw.rect(self.screen, (10, 40, 10), (GAME_WIDTH + 20, 190, 280, 80), border_radius=10)
        pygame.draw.rect(self.screen, NEON_GREEN, (GAME_WIDTH + 20, 190, 280, 80), 2, border_radius=10)
        p1_label = self.header_font.render("YOU (GREEN)", True, NEON_GREEN)
        self.screen.blit(p1_label, (GAME_WIDTH + 40, 200))
        p1_sub = self.text_font.render("Manual Control", True, (150, 255, 150))
        self.screen.blit(p1_sub, (GAME_WIDTH + 40, 235))

        # Player 2 (AI)
        pygame.draw.rect(self.screen, (40, 10, 10), (GAME_WIDTH + 20, 290, 280, 80), border_radius=10)
        pygame.draw.rect(self.screen, NEON_RED, (GAME_WIDTH + 20, 290, 280, 80), 2, border_radius=10)
        p2_label = self.header_font.render("AI (RED)", True, NEON_RED)
        self.screen.blit(p2_label, (GAME_WIDTH + 40, 300))
        p2_sub = self.text_font.render("Voronoi Bot", True, (255, 150, 150))
        self.screen.blit(p2_sub, (GAME_WIDTH + 40, 335))

        # Scoreboard
        score_bg_rect = pygame.Rect(GAME_WIDTH + 20, 400, 280, 100)
        pygame.draw.rect(self.screen, (0, 0, 0), score_bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, DARK_GRAY, score_bg_rect, 2, border_radius=15)

        p1_score_surf = self.score_font.render(str(self.p1_score), True, NEON_GREEN)
        p2_score_surf = self.score_font.render(str(self.p2_score), True, NEON_RED)
        dash_surf = self.score_font.render("-", True, WHITE)

        total_w = p1_score_surf.get_width() + dash_surf.get_width() + p2_score_surf.get_width() + 40
        start_x = center_x - total_w // 2
        
        self.screen.blit(p1_score_surf, (start_x, 425))
        self.screen.blit(dash_surf, (start_x + p1_score_surf.get_width() + 20, 425))
        self.screen.blit(p2_score_surf, (start_x + p1_score_surf.get_width() + 20 + dash_surf.get_width() + 20, 425))

        if self.round_over:
            if self.winner == "DRAW":
                msg = "DRAW!"
                color = YELLOW
            elif self.winner == "GREEN":
                msg = "YOU WIN!"
                color = NEON_GREEN
            else:
                msg = "AI WINS!"
                color = NEON_RED
            
            res_bg = pygame.Rect(GAME_WIDTH + 20, 520, 280, 50)
            pygame.draw.rect(self.screen, (20, 20, 20), res_bg, border_radius=8)
            pygame.draw.rect(self.screen, color, res_bg, 2, border_radius=8)
            
            res_text = self.header_font.render(msg, True, color)
            res_rect = res_text.get_rect(center=res_bg.center)
            self.screen.blit(res_text, res_rect)

    def draw(self):
        self.screen.fill(BLACK)
        
        for x in range(0, GAME_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GAME_WIDTH, y), 1)

        for x in range(COLS):
            for y in range(ROWS):
                if self.grid[x][y] == 1:
                    pygame.draw.rect(self.screen, NEON_GREEN, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, (150, 255, 150), (x*GRID_SIZE+5, y*GRID_SIZE+5, GRID_SIZE-10, GRID_SIZE-10))
                elif self.grid[x][y] == 2:
                    pygame.draw.rect(self.screen, NEON_RED, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, (255, 150, 150), (x*GRID_SIZE+5, y*GRID_SIZE+5, GRID_SIZE-10, GRID_SIZE-10))

        pygame.draw.rect(self.screen, WHITE, (self.p1_pos[0]*GRID_SIZE, self.p1_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, NEON_GREEN, (self.p1_pos[0]*GRID_SIZE, self.p1_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)
        
        pygame.draw.rect(self.screen, WHITE, (self.p2_pos[0]*GRID_SIZE, self.p2_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, NEON_RED, (self.p2_pos[0]*GRID_SIZE, self.p2_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)

        self.draw_sidebar()
        pygame.display.update()

    def is_safe(self, x, y):
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return False
        if self.grid[x][y] != 0:
            return False
        return True

    def run(self):
        running = True
        while running:
            # 1. INPUT
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # Buffer Input & Play Sound
                    valid_key = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.p1_dir != "DOWN": 
                            self.p1_next_dir = "UP"
                            valid_key = True
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.p1_dir != "UP": 
                            self.p1_next_dir = "DOWN"
                            valid_key = True
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.p1_dir != "RIGHT": 
                            self.p1_next_dir = "LEFT"
                            valid_key = True
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.p1_dir != "LEFT": 
                            self.p1_next_dir = "RIGHT"
                            valid_key = True
                            
                    if valid_key:
                        self.play_sound("move")

            # 2. GAME LOGIC
            current_time = pygame.time.get_ticks()
            
            if current_time - self.last_move_time > self.move_delay:
                self.last_move_time = current_time
                
                if not self.tournament_over and not self.round_over:
                    self.p1_dir = self.p1_next_dir
                    move1 = self.p1_dir
                    move2 = smart_tron_bot.get_move(self.grid.copy(), self.p2_pos, 2, self.p1_pos)

                    new_p1 = list(self.p1_pos)
                    if move1 == "UP": new_p1[1] -= 1
                    elif move1 == "DOWN": new_p1[1] += 1
                    elif move1 == "LEFT": new_p1[0] -= 1
                    elif move1 == "RIGHT": new_p1[0] += 1

                    new_p2 = list(self.p2_pos)
                    if move2 == "UP": new_p2[1] -= 1
                    elif move2 == "DOWN": new_p2[1] += 1
                    elif move2 == "LEFT": new_p2[0] -= 1
                    elif move2 == "RIGHT": new_p2[0] += 1

                    p1_dead = not self.is_safe(new_p1[0], new_p1[1])
                    p2_dead = not self.is_safe(new_p2[0], new_p2[1])
                    
                    if new_p1 == new_p2:
                        p1_dead = True
                        p2_dead = True

                    if p1_dead or p2_dead:
                        self.play_sound("crash") 
                        if p1_dead and p2_dead:
                            self.winner = "DRAW"
                        elif p1_dead:
                            self.winner = "RED"
                            self.p2_score += 1
                        elif p2_dead:
                            self.winner = "GREEN"
                            self.p1_score += 1
                        self.round_over = True
                    else:
                        self.p1_pos = new_p1
                        self.grid[new_p1[0]][new_p1[1]] = 1
                        self.p2_pos = new_p2
                        self.grid[new_p2[0]][new_p2[1]] = 2
                
                elif self.round_over and not self.tournament_over:
                    self.draw() 
                    pygame.time.wait(2000)
                    
                    if self.match_count < MAX_MATCHES:
                        self.match_count += 1
                        self.reset_round()
                    else:
                        self.tournament_over = True
            
            # 3. RENDER
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TronGame()
    game.run()