# snake_pro_sound_fixed.py
import pygame
import random
import os
import sys
from pathlib import Path

# -------------------------
# Audio-preinit + init
# -------------------------
# Pre-initialize mixer for more reliable audio behavior:
# 44100 Hz, signed 16-bit, stereo, medium buffer
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: mixer.init failed:", e)

# -------------------------
# Settings
# -------------------------
WIDTH, HEIGHT = 720, 480
BLOCK = 16
FPS_BASE = 14

# Colors
BG_LIGHT = (238, 244, 255)
PANEL = (230, 230, 230)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_RED = (255, 0, 102)

RAINBOW = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (75, 0, 130),
    (148, 0, 211),
]

FOOD_TYPES = [
    {"id": "normal",  "color": (255, 50, 50),  "label": "Apple",    "duration": 0,  "score": 1},
    {"id": "gold",    "color": (255, 215, 0),  "label": "Gold",     "duration": 0,  "score": 5},
    {"id": "slow",    "color": (100, 200, 255),"label": "Slow",     "duration": 6,  "score": 2},
    {"id": "fast",    "color": (255, 120, 120),"label": "Fast",     "duration": 6,  "score": 2},
    {"id": "life",    "color": (150, 255, 150),"label": "Life",     "duration": 0,  "score": 0},
]

# candidate filenames (try each in order)
CANDIDATE_BG = ["bg_music.ogg", "bg_music.wav", "bg_music.mp3"]
CANDIDATE_BITE = ["bite.wav", "bite.ogg", "bite.mp3"]
CANDIDATE_OVER = ["over.wav", "over.ogg", "over.mp3"]
CANDIDATE_SPECIAL = ["eat_special.wav", "eat_special.ogg", "eat_special.mp3"]

ASSET_PATH = Path(".")
HIGH_SCORE_FILE = ASSET_PATH / "highscore.txt"

# -------------------------
# Utilities
# -------------------------
def read_highscore():
    try:
        if not HIGH_SCORE_FILE.exists():
            HIGH_SCORE_FILE.write_text("0")
        return int(HIGH_SCORE_FILE.read_text().strip() or "0")
    except Exception:
        return 0

def write_highscore(score):
    try:
        HIGH_SCORE_FILE.write_text(str(score))
    except Exception:
        pass

def find_first_existing(paths):
    for p in paths:
        if (ASSET_PATH / p).exists():
            return ASSET_PATH / p
    return None

# Robust loader: tries list of filenames in order and returns loaded Sound or None
def load_sound_candidates(candidates):
    p = find_first_existing(candidates)
    if p is None:
        print("Audio: file not found among candidates:", candidates)
        return None
    try:
        s = pygame.mixer.Sound(str(p))
        print(f"Audio: loaded sound '{p.name}'")
        return s
    except Exception as e:
        print(f"Audio: failed to load sound {p.name} -> {e}")
        return None

# Background music loader (music module uses different API)
def load_background_music(candidates):
    p = find_first_existing(candidates)
    if p is None:
        print("Audio: background music not found among candidates:", candidates)
        return None
    try:
        pygame.mixer.music.load(str(p))
        print(f"Audio: loaded background music '{p.name}'")
        return p
    except Exception as e:
        print(f"Audio: failed to load bg music {p.name} -> {e}")
        return None

# -------------------------
# Load audio (robust)
# -------------------------
bg_music_file = load_background_music(CANDIDATE_BG)
bite_snd = load_sound_candidates(CANDIDATE_BITE)
over_snd = load_sound_candidates(CANDIDATE_OVER)
special_snd = load_sound_candidates(CANDIDATE_SPECIAL)

# Set volumes (if loaded)
if bite_snd:
    bite_snd.set_volume(0.5)
if over_snd:
    over_snd.set_volume(0.6)
if special_snd:
    special_snd.set_volume(0.6)
if bg_music_file:
    try:
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)  # loop background
    except Exception as e:
        print("Audio: could not play background music ->", e)

# -------------------------
# Pygame display + fonts
# -------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Pro - Sound Fixed")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 20)
BIG = pygame.font.SysFont("consolas", 48)
SMALL = pygame.font.SysFont("consolas", 16)

# -------------------------
# Drawing helpers
# -------------------------
def draw_rect(screen, color, rect, radius=6):
    pygame.draw.rect(screen, color, rect, border_radius=radius)

def draw_snake(surface, snake_segments, wiggle_phase):
    for i, seg in enumerate(snake_segments):
        x, y = seg
        color = RAINBOW[i % len(RAINBOW)]
        if i == len(snake_segments) - 1:
            head_rect = pygame.Rect(x - 2, y - 2 + (wiggle_phase % 2), BLOCK + 4, BLOCK + 4)
            pygame.draw.rect(surface, color, head_rect, border_radius=6)
            eye_r = 3
            left_eye = (x + 4, y + 4)
            right_eye = (x + BLOCK - 4, y + 4)
            pygame.draw.circle(surface, WHITE, left_eye, eye_r)
            pygame.draw.circle(surface, WHITE, right_eye, eye_r)
            pygame.draw.circle(surface, BLACK, left_eye, 1)
            pygame.draw.circle(surface, BLACK, right_eye, 1)
        else:
            draw_rect(surface, color, (x, y + (wiggle_phase % 2), BLOCK, BLOCK), radius=4)

# -------------------------
# Food helpers
# -------------------------
def random_food_position():
    max_x = (WIDTH - BLOCK) // BLOCK
    max_y = (HEIGHT - BLOCK) // BLOCK
    return random.randint(0, max_x) * BLOCK, random.randint(0, max_y) * BLOCK

def spawn_food():
    pos = random_food_position()
    weights = [60, 8, 10, 10, 12]
    choice = random.choices(FOOD_TYPES, weights=weights, k=1)[0]
    return {"type": choice, "pos": pos, "born": pygame.time.get_ticks()}

# -------------------------
# Main Gameplay
# -------------------------
def game_session(player_name):
    x = WIDTH // 2 // BLOCK * BLOCK
    y = HEIGHT // 2 // BLOCK * BLOCK
    dx, dy = 0, 0
    snake = [[x, y]]
    length = 1
    score = 0
    lives = 1
    wiggle = 0
    fps = FPS_BASE
    highscore = read_highscore()
    effects = {"slow": 0, "fast": 0}
    food = spawn_food()
    running = True
    paused = False

    while running:
        now = pygame.time.get_ticks()
        if effects["slow"] > now:
            current_fps = max(6, fps // 2)
        elif effects["fast"] > now:
            current_fps = min(40, fps + 8)
        else:
            current_fps = fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                if event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                if event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            head_x, head_y = snake[-1]
            if abs(mx - head_x) > abs(my - head_y):
                dx = BLOCK if mx > head_x else -BLOCK
                dy = 0
            else:
                dy = BLOCK if my > head_y else -BLOCK
                dx = 0

        if paused:
            screen.fill(BG_LIGHT)
            draw_rect(screen, PANEL, (40, 40, WIDTH - 80, HEIGHT - 80), radius=10)
            txt = BIG.render("PAUSED", True, BLACK)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
            sub = FONT.render("Press P to resume | ESC to quit to menu", True, BLACK)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 30))
            pygame.display.flip()
            clock.tick(10)
            continue

        if dx != 0 or dy != 0:
            x += dx
            y += dy

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            lives -= 1
            if over_snd:
                over_snd.play()
            if lives >= 0:
                x = WIDTH // 2 // BLOCK * BLOCK
                y = HEIGHT // 2 // BLOCK * BLOCK
                dx, dy = 0, 0
                snake = [[x, y]]
                length = 1
                pygame.time.wait(350)
            else:
                if score > highscore:
                    write_highscore(score)
                return {"score": score}

        head = [x, y]
        snake.append(head)
        if len(snake) > length:
            del snake[0]

        for seg in snake[:-1]:
            if seg == head:
                lives -= 1
                if over_snd:
                    over_snd.play()
                if li
