import pygame
import numpy as np
import sys
import time

# --- IMPORTS ---
import smart_tron_bot

# --- CONSTANTS ---
GAME_WIDTH = 600
SIDEBAR_WIDTH = 340  # Slightly wider for the form
WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
HEIGHT = 600
GRID_SIZE = 20
COLS = GAME_WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

# COLORS
BLACK = (10, 10, 15)
NEON_BLUE = (0, 255, 255)
NEON_RED = (255, 50, 50)
DARK_GRAY = (40, 40, 50)
GRID_COLOR = (30, 30, 40)
SIDEBAR_BG = (20, 20, 25)
WHITE = (240, 240, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (180, 50, 255)
INPUT_BG = (50, 50, 60)
INPUT_ACTIVE = (80, 80, 100)

class TronGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 
        
        self.fullscreen = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TRON: AI Tournament Arena")
        self.clock = pygame.time.Clock()

        # --- AUDIO ---
        self.sounds_loaded = False
        try:
            pygame.mixer.music.load("./sounds/bg_music.mp3")
            pygame.mixer.music.set_volume(0.4) 
            pygame.mixer.music.play(-1)
            self.snd_crash = pygame.mixer.Sound("./sounds/game_over.wav")
            self.snd_crash.set_volume(0.8)
            self.sounds_loaded = True
        except Exception:
            print("Audio not found. Running silent.")

        # --- FONTS ---
        try:
            self.title_font = pygame.font.SysFont("impact", 40)
            self.header_font = pygame.font.SysFont("monospace", 28, bold=True)
            self.text_font = pygame.font.SysFont("monospace", 18)
            self.score_font = pygame.font.SysFont("monospace", 50, bold=True)
            self.status_font = pygame.font.SysFont("monospace", 22, bold=True) # Added missing font
            self.input_font = pygame.font.SysFont("monospace", 22)
        except:
             self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
             self.header_font = pygame.font.SysFont("Courier", 28, bold=True)
             self.text_font = pygame.font.SysFont("Courier", 18)
             self.score_font = pygame.font.SysFont("Courier", 50, bold=True)
             self.status_font = pygame.font.SysFont("Courier", 22, bold=True) # Added missing font
             self.input_font = pygame.font.SysFont("Courier", 22)

        # --- APP STATE ---
        self.state = "SETUP" # Can be "SETUP" or "PLAYING"
        
        # Setup Variables (Input Fields)
        self.input_p1 = ""
        self.input_p2 = ""
        self.input_matches = ""
        
        # 0 = P1 Name, 1 = P2 Name, 2 = Matches, 3 = None
        self.active_field = 0 
        
        # Final Game Settings (Defaults)
        self.p1_name = "BLUE BOT"
        self.p2_name = "RED BOT"
        self.max_matches = 20
        
        # Tournament Logic
        self.match_count = 1
        self.p1_score = 0
        self.p2_score = 0
        self.tournament_over = False
        
        self.reset_round()

    def reset_round(self):
        self.grid = np.zeros((COLS, ROWS))
        self.p1_pos = [5, ROWS // 2]
        self.p2_pos = [COLS - 6, ROWS // 2]
        self.grid[self.p1_pos[0]][self.p1_pos[1]] = 1
        self.grid[self.p2_pos[0]][self.p2_pos[1]] = 2
        self.round_over = False
        self.winner = None

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def start_tournament(self):
        # Apply Defaults if empty
        if self.input_p1.strip() != "":
            self.p1_name = self.input_p1
        if self.input_p2.strip() != "":
            self.p2_name = self.input_p2
        
        # Parse Matches
        if self.input_matches.strip() != "":
            try:
                val = int(self.input_matches)
                self.max_matches = max(1, min(val, 100)) # Clamp between 1 and 100
            except ValueError:
                self.max_matches = 20 # Fallback if they typed gibberish
        else:
            self.max_matches = 20

        self.state = "PLAYING"
        self.match_count = 1
        self.p1_score = 0
        self.p2_score = 0
        self.reset_round()

    def draw_input_box(self, label, text, y_pos, field_index):
        # Label
        lbl = self.text_font.render(label, True, (180, 180, 180))
        self.screen.blit(lbl, (GAME_WIDTH + 30, y_pos))
        
        # Box Background
        color = INPUT_ACTIVE if self.active_field == field_index else INPUT_BG
        box_rect = pygame.Rect(GAME_WIDTH + 30, y_pos + 25, 280, 40)
        pygame.draw.rect(self.screen, color, box_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE if self.active_field == field_index else DARK_GRAY, box_rect, 2, border_radius=5)
        
        # Text
        txt_surf = self.input_font.render(text, True, WHITE)
        # Clip text if too long
        self.screen.blit(txt_surf, (GAME_WIDTH + 40, y_pos + 35))

    def draw_sidebar_setup(self):
        # Background
        pygame.draw.rect(self.screen, SIDEBAR_BG, (GAME_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, DARK_GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 3)

        # Title
        title_surf = self.title_font.render("TOURNAMENT SETUP", True, YELLOW)
        self.screen.blit(title_surf, (GAME_WIDTH + 20, 40))

        # Inputs
        self.draw_input_box("Blue Bot Name:", self.input_p1, 120, 0)
        self.draw_input_box("Red Bot Name:", self.input_p2, 200, 1)
        self.draw_input_box("Number of Matches (Default: 20):", self.input_matches, 280, 2)

        # Start Button
        btn_rect = pygame.Rect(GAME_WIDTH + 30, 400, 280, 60)
        
        # Hover effect logic handled in loop, here just simple draw
        mouse_pos = pygame.mouse.get_pos()
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (0, 200, 0), btn_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (0, 150, 0), btn_rect, border_radius=10)
            
        pygame.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=10)
        
        btn_text = self.header_font.render("START MATCH", True, WHITE)
        text_rect = btn_text.get_rect(center=btn_rect.center)
        self.screen.blit(btn_text, text_rect)
        
        # Defaults Note
        note = self.text_font.render("* Leave blank for defaults", True, (100, 100, 100))
        self.screen.blit(note, (GAME_WIDTH + 40, 470))

    def draw_sidebar_game(self):
        # Sidebar Background
        pygame.draw.rect(self.screen, SIDEBAR_BG, (GAME_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, DARK_GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 3)

        # Header
        title_text = "TRON ARENA"
        title_surf = self.title_font.render(title_text, True, PURPLE)
        center_x = GAME_WIDTH + SIDEBAR_WIDTH // 2
        title_rect = title_surf.get_rect(center=(center_x, 50))
        self.screen.blit(title_surf, title_rect)

        # Match Progress
        pygame.draw.rect(self.screen, (50, 50, 60), (GAME_WIDTH + 30, 100, 280, 30), border_radius=15)
        progress = (self.match_count - 1) / self.max_matches
        if self.tournament_over: progress = 1.0
        bar_width = int(280 * progress)
        pygame.draw.rect(self.screen, YELLOW, (GAME_WIDTH + 30, 100, bar_width, 30), border_radius=15)
        
        match_str = f"MATCH {self.match_count}/{self.max_matches}"
        if self.tournament_over: match_str = "FINISHED"
        match_text = self.status_font.render(match_str, True, BLACK if progress > 0.5 else WHITE)
        self.screen.blit(match_text, match_text.get_rect(center=(center_x, 115)))

        # Player Cards (Using Custom Names)
        # Blue
        pygame.draw.rect(self.screen, (10, 30, 40), (GAME_WIDTH + 20, 170, 300, 70), border_radius=10)
        pygame.draw.rect(self.screen, NEON_BLUE, (GAME_WIDTH + 20, 170, 300, 70), 2, border_radius=10)
        p1_label = self.header_font.render(self.p1_name[:12], True, NEON_BLUE) # Limit len
        self.screen.blit(p1_label, (GAME_WIDTH + 35, 180))
        self.screen.blit(self.text_font.render("Voronoi AI", True, (100, 200, 255)), (GAME_WIDTH + 35, 210))

        # Red
        pygame.draw.rect(self.screen, (40, 10, 10), (GAME_WIDTH + 20, 260, 300, 70), border_radius=10)
        pygame.draw.rect(self.screen, NEON_RED, (GAME_WIDTH + 20, 260, 300, 70), 2, border_radius=10)
        p2_label = self.header_font.render(self.p2_name[:12], True, NEON_RED)
        self.screen.blit(p2_label, (GAME_WIDTH + 35, 270))
        self.screen.blit(self.text_font.render("Voronoi AI", True, (255, 100, 100)), (GAME_WIDTH + 35, 300))

        # Scoreboard
        score_bg_rect = pygame.Rect(GAME_WIDTH + 20, 380, 300, 100)
        pygame.draw.rect(self.screen, (0, 0, 0), score_bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, DARK_GRAY, score_bg_rect, 2, border_radius=15)

        p1_score_surf = self.score_font.render(str(self.p1_score), True, NEON_BLUE)
        p2_score_surf = self.score_font.render(str(self.p2_score), True, NEON_RED)
        dash_surf = self.score_font.render("-", True, WHITE)

        total_w = p1_score_surf.get_width() + dash_surf.get_width() + p2_score_surf.get_width() + 40
        start_x = center_x - total_w // 2
        
        self.screen.blit(p1_score_surf, (start_x, 405))
        self.screen.blit(dash_surf, (start_x + p1_score_surf.get_width() + 20, 405))
        self.screen.blit(p2_score_surf, (start_x + p1_score_surf.get_width() + 20 + dash_surf.get_width() + 20, 405))

        # Winner/Status
        if self.round_over:
            msg = f"{self.winner} WINS!" if self.winner != "DRAW" else "DRAW!"
            color = NEON_BLUE if self.winner == "BLUE" else NEON_RED
            if self.winner == "DRAW": color = YELLOW
            
            res_bg = pygame.Rect(GAME_WIDTH + 20, 510, 300, 50)
            pygame.draw.rect(self.screen, (20, 20, 20), res_bg, border_radius=8)
            pygame.draw.rect(self.screen, color, res_bg, 2, border_radius=8)
            res_text = self.header_font.render(msg, True, color)
            self.screen.blit(res_text, res_text.get_rect(center=res_bg.center))
        elif self.tournament_over:
            if self.p1_score > self.p2_score:
                msg, color = f"{self.p1_name} WINS!", NEON_BLUE
            elif self.p2_score > self.p1_score:
                msg, color = f"{self.p2_name} WINS!", NEON_RED
            else:
                msg, color = "GRAND DRAW!", YELLOW
            
            res_bg = pygame.Rect(GAME_WIDTH + 20, 510, 300, 50)
            pygame.draw.rect(self.screen, (20, 20, 20), res_bg, border_radius=8)
            pygame.draw.rect(self.screen, color, res_bg, 2, border_radius=8)
            res_text = self.header_font.render(msg, True, color)
            self.screen.blit(res_text, res_text.get_rect(center=res_bg.center))

    def draw(self):
        self.screen.fill(BLACK)
        
        # Grid
        for x in range(0, GAME_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GAME_WIDTH, y), 1)

        # Trails
        for x in range(COLS):
            for y in range(ROWS):
                if self.grid[x][y] == 1:
                    pygame.draw.rect(self.screen, NEON_BLUE, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, (150, 255, 255), (x*GRID_SIZE+5, y*GRID_SIZE+5, GRID_SIZE-10, GRID_SIZE-10))
                elif self.grid[x][y] == 2:
                    pygame.draw.rect(self.screen, NEON_RED, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, (255, 150, 150), (x*GRID_SIZE+5, y*GRID_SIZE+5, GRID_SIZE-10, GRID_SIZE-10))

        # Heads
        pygame.draw.rect(self.screen, WHITE, (self.p1_pos[0]*GRID_SIZE, self.p1_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, NEON_BLUE, (self.p1_pos[0]*GRID_SIZE, self.p1_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)
        pygame.draw.rect(self.screen, WHITE, (self.p2_pos[0]*GRID_SIZE, self.p2_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, NEON_RED, (self.p2_pos[0]*GRID_SIZE, self.p2_pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)

        # Sidebar based on state
        if self.state == "SETUP":
            self.draw_sidebar_setup()
        else:
            self.draw_sidebar_game()
            
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
            # --- EVENT HANDLING ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Fullscreen / Quit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        
                # --- SETUP INPUT HANDLING ---
                if self.state == "SETUP":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        # Check clicks on input boxes
                        if GAME_WIDTH + 30 <= mx <= GAME_WIDTH + 310:
                            if 145 <= my <= 185: self.active_field = 0 # Name 1
                            elif 225 <= my <= 265: self.active_field = 1 # Name 2
                            elif 305 <= my <= 345: self.active_field = 2 # Matches
                            elif 400 <= my <= 460: self.start_tournament() # Start Button
                            else: self.active_field = 3 # Clicked void
                            
                    if event.type == pygame.KEYDOWN:
                        if self.active_field <= 2:
                            if event.key == pygame.K_RETURN:
                                if self.active_field < 2:
                                    self.active_field += 1
                                else:
                                    self.start_tournament()
                            elif event.key == pygame.K_BACKSPACE:
                                if self.active_field == 0: self.input_p1 = self.input_p1[:-1]
                                elif self.active_field == 1: self.input_p2 = self.input_p2[:-1]
                                elif self.active_field == 2: self.input_matches = self.input_matches[:-1]
                            elif event.key == pygame.K_TAB:
                                self.active_field = (self.active_field + 1) % 3
                            else:
                                # Limit max chars
                                if len(event.unicode) > 0 and event.unicode.isprintable():
                                    if self.active_field == 0 and len(self.input_p1) < 12:
                                        self.input_p1 += event.unicode
                                    elif self.active_field == 1 and len(self.input_p2) < 12:
                                        self.input_p2 += event.unicode
                                    elif self.active_field == 2 and len(self.input_matches) < 3:
                                        if event.unicode.isdigit(): # Only digits for matches
                                            self.input_matches += event.unicode

            # --- LOGIC & RENDERING ---
            if self.state == "PLAYING":
                if not self.tournament_over and not self.round_over:
                    # Update more frequently for smoother look, but logic throttled if needed
                    self.clock.tick(60) 
                    
                    # Logic happens every frame here (60fps) - fast bots!
                    # If too fast, add time.delay or modulo check
                    move1 = smart_tron_bot.get_move(self.grid.copy(), self.p1_pos, 1, self.p2_pos)
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
                        if self.sounds_loaded: self.snd_crash.play()
                        if p1_dead and p2_dead:
                            self.winner = "DRAW"
                        elif p1_dead:
                            self.winner = "RED" # Red wins if Blue dies
                            self.p2_score += 1
                        elif p2_dead:
                            self.winner = "BLUE" # Blue wins if Red dies
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
                    
                    if self.match_count < self.max_matches:
                        self.match_count += 1
                        self.reset_round()
                    else:
                        self.tournament_over = True
            
            # Draw everything (Setup or Game)
            self.draw()
            if self.state == "SETUP":
                self.clock.tick(30) # Slower tick for menu is fine

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TronGame()
    game.run()
