# snake_pro.py
import pygame
import random
import os
import sys
from pathlib import Path
from math import copysign

# ----------------------------
# Initialization
# ----------------------------
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# ----------------------------
# Settings and Constants
# ----------------------------
WIDTH, HEIGHT = 720, 480
BLOCK = 16
FPS_BASE = 14

# Colors
BG_LIGHT = (238, 244, 255)    # soft light-blue background (you asked "light")
PANEL = (230, 230, 230)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_RED = (255, 0, 102)

# Rainbow (7 colors)
RAINBOW = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 0, 255),
    (75, 0, 130),
    (148, 0, 211),
]

# Special fruit types (id, color, label, effect_duration, score_value)
# effect_duration in seconds (0 = instant, nonzero = lasts)
FOOD_TYPES = [
    {"id": "normal",  "color": (255, 50, 50),  "label": "Apple",    "duration": 0,  "score": 1},
    {"id": "gold",    "color": (255, 215, 0),  "label": "Gold",     "duration": 0,  "score": 5},
    {"id": "slow",    "color": (100, 200, 255),"label": "Slow",     "duration": 6,  "score": 2},
    {"id": "fast",    "color": (255, 120, 120),"label": "Fast",     "duration": 6,  "score": 2},
    {"id": "life",    "color": (150, 255, 150),"label": "Life",     "duration": 0,  "score": 0},  # gives +1 life
]

# Files (optional) - place them in same folder to enable
BG_MUSIC = "bg_music.mp3"
BITE_SOUND = "bite.wav"
OVER_SOUND = "over.wav"
SPECIAL_SOUND = "eat_special.wav"

ASSET_PATH = Path(".")
HIGH_SCORE_FILE = ASSET_PATH / "highscore.txt"

# ----------------------------
# Utilities: highscore, load sounds
# ----------------------------
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

# load sounds if present
def safe_sound(filename):
    path = ASSET_PATH / filename
    if path.exists():
        try:
            return pygame.mixer.Sound(str(path))
        except Exception:
            return None
    return None

bite_snd = safe_sound(BITE_SOUND)
over_snd = safe_sound(OVER_SOUND)
special_snd = safe_sound(SPECIAL_SOUND)
BG_MUSIC_EXISTS = (ASSET_PATH / BG_MUSIC).exists()

# ----------------------------
# Pygame screen setup
# ----------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Pro - Rainbow Edition")
clock = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont("consolas", 20)
BIG = pygame.font.SysFont("consolas", 48)
SMALL = pygame.font.SysFont("consolas", 16)

# ----------------------------
# Helper: draw rounded rect (simple)
# ----------------------------
def draw_rect(screen, color, rect, radius=6):
    pygame.draw.rect(screen, color, rect, border_radius=radius)

# ----------------------------
# Snake drawing (rainbow + head animation)
# ----------------------------
def draw_snake(surface, snake_segments, wiggle_phase):
    # wiggle_phase is a small int for visual offset
    for i, seg in enumerate(snake_segments):
        x, y = seg
        color = RAINBOW[i % len(RAINBOW)]
        # head
        if i == len(snake_segments) - 1:
            # slightly bigger head with eyes
            head_rect = pygame.Rect(x - 2, y - 2 + (wiggle_phase % 2), BLOCK + 4, BLOCK + 4)
            pygame.draw.rect(surface, color, head_rect, border_radius=6)
            # eyes
            eye_r = 3
            left_eye = (x + 4, y + 4)
            right_eye = (x + BLOCK - 4, y + 4)
            pygame.draw.circle(surface, WHITE, left_eye, eye_r)
            pygame.draw.circle(surface, WHITE, right_eye, eye_r)
            pygame.draw.circle(surface, BLACK, left_eye, 1)
            pygame.draw.circle(surface, BLACK, right_eye, 1)
        else:
            # body piece with small vertical wiggle
            draw_rect(surface, color, (x, y + (wiggle_phase % 2), BLOCK, BLOCK), radius=4)

# ----------------------------
# Food utils
# ----------------------------
def random_food_position():
    max_x = (WIDTH - BLOCK) // BLOCK
    max_y = (HEIGHT - BLOCK) // BLOCK
    return random.randint(0, max_x) * BLOCK, random.randint(0, max_y) * BLOCK

def spawn_food():
    pos = random_food_position()
    # ensure food not on the very top UI band (optional)
    # choose type with weighted randomness (normal more common)
    weights = [60, 8, 10, 10, 12]  # tuned probabilities
    choice = random.choices(FOOD_TYPES, weights=weights, k=1)[0]
    return {"type": choice, "pos": pos, "born": pygame.time.get_ticks()}

# ----------------------------
# Menu UI Components
# ----------------------------
def button(surface, rect, text, inactive_col, active_col, action=None):
    mx, my = pygame.mouse.get_pos()
    r = pygame.Rect(rect)
    hovered = r.collidepoint(mx, my)
    draw_rect(surface, active_col if hovered else inactive_col, rect, radius=8)
    txt = FONT.render(text, True, BLACK)
    surface.blit(txt, (rect[0] + (rect[2] - txt.get_width()) // 2, rect[1] + (rect[3] - txt.get_height()) // 2))
    clicked = pygame.mouse.get_pressed()[0] and hovered
    return clicked

# ----------------------------
# Main Game Implementation
# ----------------------------
def game_session(player_name):
    # Game variables
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

    # effect timers
    effects = {
        "slow": 0,   # ends timestamp
        "fast": 0,
    }

    food = spawn_food()
    running = True
    paused = False

    while running:
        # apply active effects (timers)
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
                    return None  # go back to menu
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    return "restart"
                # arrow controls (grid aligned)
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK, 0
                if event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK, 0
                if event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK
                if event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK

        # touch/mouse quick control (click to direct movement)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            head_x, head_y = snake[-1]
            # decide horizontal/vertical based on larger delta
            if abs(mx - head_x) > abs(my - head_y):
                dx = BLOCK if mx > head_x else -BLOCK
                dy = 0
            else:
                dy = BLOCK if my > head_y else -BLOCK
                dx = 0

        if paused:
            # draw paused screen
            screen.fill(BG_LIGHT)
            draw_rect(screen, PANEL, (40, 40, WIDTH - 80, HEIGHT - 80), radius=10)
            txt = BIG.render("PAUSED", True, BLACK)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
            sub = FONT.render("Press P to resume | ESC to quit to menu", True, BLACK)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 30))
            pygame.display.flip()
            clock.tick(10)
            continue

        # movement
        if dx != 0 or dy != 0:
            x += dx
            y += dy

        # collision with walls
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            # lose a life or end
            lives -= 1
            if over_snd:
                over_snd.play()
            if lives >= 0:
                # respawn at center & reset direction
                x = WIDTH // 2 // BLOCK * BLOCK
                y = HEIGHT // 2 // BLOCK * BLOCK
                dx, dy = 0, 0
                snake = [[x, y]]
                length = 1
                pygame.time.wait(350)
            else:
                # game over
                if score > highscore:
                    write_highscore(score)
                return {"score": score}

        # update snake segments
        head = [x, y]
        snake.append(head)
        if len(snake) > length:
            del snake[0]

        # self collision
        for seg in snake[:-1]:
            if seg == head:
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

        # draw
        screen.fill(BG_LIGHT)
        # top panels
        draw_rect(screen, PANEL, (0, 0, WIDTH, 36), radius=0)
        header = FONT.render(f"Player: {player_name}   Score: {score}   High: {read_highscore()}   Lives: {lives}", True, BLACK)
        screen.blit(header, (10, 8))

        # draw food
        fx, fy = food["pos"]
        fcol = food["type"]["color"]
        pygame.draw.rect(screen, fcol, (fx, fy, BLOCK, BLOCK), border_radius=6)
        # label small
        label = SMALL.render(food["type"]["label"], True, BLACK)
        screen.blit(label, (fx, fy - 16))

        # draw snake (animated wiggle)
        wiggle = (pygame.time.get_ticks() // 160) % 2
        draw_snake(screen, snake, wiggle)

        pygame.display.flip()

        # check eating (exact grid match)
        if head[0] == fx and head[1] == fy:
            ftype = food["type"]["id"]
            # immediate score/life effects
            score += food["type"]["score"]
            if ftype == "life":
                lives += 1
            # play appropriate sound
            if food["type"]["score"] >= 5 and special_snd:
                special_snd.play()
            elif bite_snd:
                bite_snd.play()

            # apply temporary effects
            if ftype == "slow":
                effects["slow"] = pygame.time.get_ticks() + int(food["type"]["duration"] * 1000)
            if ftype == "fast":
                effects["fast"] = pygame.time.get_ticks() + int(food["type"]["duration"] * 1000)
            # grow snake & maybe increase speed slightly
            length += 1
            # make new food (ensure not on snake)
            tries = 0
            while True:
                new_food = spawn_food()
                if new_food["pos"] not in snake:
                    food = new_food
                    break
                tries += 1
                if tries > 100:
                    food = new_food
                    break

        # gradually increase difficulty slightly
        if score and score % 5 == 0:
            fps = FPS_BASE + min(6, score // 5)

        # tick
        clock.tick(current_fps)

# ----------------------------
# Main Menu + Name Input
# ----------------------------
def main_menu():
    player_name = "Player"
    input_active = False
    input_box = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 45, 240, 36)
    name_text = ""
    show_instructions = False

    # start background music if exists
    if BG_MUSIC_EXISTS:
        try:
            pygame.mixer.music.load(str(ASSET_PATH / BG_MUSIC))
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    while True:
        screen.fill(BG_LIGHT)

        # title
        title = BIG.render("Rainbow Snake Pro", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # name input
        draw_rect(screen, PANEL, (WIDTH // 2 - 140, HEIGHT // 2 - 55, 280, 80), radius=10)
        label = FONT.render("Enter your name:", True, BLACK)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 50 + 6))

        # input field
        color_box = (200, 200, 255) if input_active else WHITE
        draw_rect(screen, color_box, input_box, radius=6)
        txt_surface = FONT.render(name_text or "Player", True, BLACK)
        screen.blit(txt_surface, (input_box.x + 8, input_box.y + 6))

        # buttons
        mx, my = pygame.mouse.get_pos()
        start_clicked = button(screen, (WIDTH // 2 - 90, HEIGHT // 2 + 50, 80, 40), "Start", (150, 240, 150), (130, 220, 130))
        quit_clicked = button(screen, (WIDTH // 2 + 10, HEIGHT // 2 + 50, 80, 40), "Quit", (255, 150, 150), (240, 120, 120))
        menu_info = FONT.render("Press ESC in-game to return to menu. Press P to pause. R to restart.", True, BLACK)
        screen.blit(menu_info, (10, HEIGHT - 28))

        if show_instructions:
            inst = SMALL.render("Special Fruits: Gold(+5), Slow(slow time), Fast(temporary speed), Life(+1).", True, BLACK)
            screen.blit(inst, (10, HEIGHT - 56))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        player_name = name_text.strip() or "Player"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    else:
                        if len(name_text) < 14:
                            name_text += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        player_name = name_text.strip() or "Player"
                        # start game
                        res = game_session(player_name)
                        if isinstance(res, dict) and "score" in res:
                            # show game over result then return to menu
                            pass
                    if event.key == pygame.K_i:
                        show_instructions = not show_instructions

        if start_clicked:
            player_name = name_text.strip() or "Player"
            outcome = game_session(player_name)
            # outcome may be None (exit to menu), "restart", or dict with final score
            if isinstance(outcome, dict) and "score" in outcome:
                # show brief game over overlay
                over_msg = BIG.render("Game Over", True, NEON_RED)
                screen.blit(over_msg, (WIDTH // 2 - over_msg.get_width() // 2, HEIGHT // 2 - 30))
                pygame.display.flip()
                pygame.time.wait(800)
            # continue to menu
        if quit_clicked:
            pygame.quit()
            sys.exit(0)

        clock.tick(30)

# ----------------------------
# Program entry
# ----------------------------
if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print("An error occurred:", e)
        pygame.quit()
        sys.exit(1)
