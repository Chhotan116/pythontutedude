import pygame, random, os

pygame.init()
pygame.mixer.init()

# ---------- COLORS ----------
BLACK = (0, 0, 0)
NEON_RED = (255, 0, 102)
WHITE = (255, 255, 255)

# 🌈 7 RAINBOW COLORS
RAINBOW = [
    (255, 0, 0),  # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (75, 0, 130),  # Indigo
    (148, 0, 211)  # Violet
]

# ---------- SCREEN SETTINGS ----------
WIDTH = 600
HEIGHT = 400
BLOCK = 15
FPS = 18
game = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🌈 Rainbow Snake Pro by ChatGPT")

# ---------- FONTS ----------
font = pygame.font.SysFont("consolas", 25)
big_font = pygame.font.SysFont("consolas", 50)

# ---------- SOUNDS ----------
BITE_SOUND = "bite.wav"
GAME_OVER_SOUND = "over.wav"

bite = pygame.mixer.Sound(BITE_SOUND) if os.path.exists(BITE_SOUND) else None
over_sound = pygame.mixer.Sound(GAME_OVER_SOUND) if os.path.exists(GAME_OVER_SOUND) else None

# ---------- HIGH SCORE ----------
if not os.path.exists("highscore.txt"):
    with open("highscore.txt", "w") as f:
        f.write("0")


def read_score():
    with open("highscore.txt", "r") as f:
        return int(f.read())


def write_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


# ---------- DRAW RAINBOW SNAKE ----------
def draw_snake(snake):
    for i, (x, y) in enumerate(snake):
        color = RAINBOW[i % len(RAINBOW)]  # Cycle 7 rainbow colors
        pygame.draw.rect(game, color, [x, y, BLOCK, BLOCK], border_radius=4)


# ---------- TEXT FUNCTION ----------
def message(text, color, x, y):
    msg = font.render(text, True, color)
    game.blit(msg, [x, y])


def draw_snake(snake):
    for i, (x, y) in enumerate(snake):
        color = RAINBOW[i % len(RAINBOW)]

        # HEAD (bigger + animated)
        if i == len(snake) - 1:
            pygame.draw.rect(game, color, [x - 2, y - 2, BLOCK + 4, BLOCK + 4], border_radius=6)

            # 🟡 Eyes animation
            eye_size = 3
            pygame.draw.circle(game, WHITE, (x + 5, y + 4), eye_size)
            pygame.draw.circle(game, WHITE, (x + BLOCK - 5, y + 4), eye_size)

            # 👅 Mouth animation (small line)
            pygame.draw.rect(game, BLACK, [x + 4, y + BLOCK - 4, 6, 2], border_radius=1)

        else:
            # BODY (slight wave animation)
            wiggle = (pygame.time.get_ticks() // 200) % 2
            pygame.draw.rect(game, color, [x, y + wiggle, BLOCK, BLOCK], border_radius=4)


# ---------- GAME LOOP ----------
def game_loop():
    x = WIDTH // 2
    y = HEIGHT // 2
    dx, dy = 0, 0
    snake = []
    length = 1
    head = [x, y]

    food_x = random.randrange(0, WIDTH - BLOCK, BLOCK)
    food_y = random.randrange(0, HEIGHT - BLOCK, BLOCK)

    score = 0
    highscore = read_score()
    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        if game_over:
            game.fill(BLACK)
            msg = big_font.render("GAME OVER!", True, NEON_RED)
            game.blit(msg, [WIDTH / 4, HEIGHT / 3])
            message("Press ENTER to Restart | ESC to Quit", WHITE, 70, 250)
            message(f"Score: {score} | High Score: {highscore}", WHITE, 140, 320)
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        game_loop()
                    elif e.key == pygame.K_ESCAPE:
                        running = False
            continue

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    dx, dy = -BLOCK, 0
                if e.key == pygame.K_RIGHT:
                    dx, dy = BLOCK, 0
                if e.key == pygame.K_UP:
                    dy, dx = -BLOCK, 0
                if e.key == pygame.K_DOWN:
                    dy, dx = BLOCK, 0

        # 📱 TOUCH CONTROLS
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if abs(mx - x) > abs(my - y):
                dx = BLOCK if mx > x else -BLOCK
                dy = 0
            else:
                dy = BLOCK if my > y else -BLOCK
                dx = 0

        x += dx
        y += dy

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            if over_sound: over_sound.play()
            game_over = True

        game.fill(BLACK)
        pygame.draw.rect(game, NEON_RED, [food_x, food_y, BLOCK, BLOCK], border_radius=4)

        head = [x, y]
        snake.append(head)
        if len(snake) > length:
            del snake[0]

        for s in snake[:-1]:
            if s == head:
                if over_sound: over_sound.play()
                game_over = True

        draw_snake(snake)
        message(f"Score: {score} | High Score: {highscore}", WHITE, 10, 10)
        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = random.randrange(0, WIDTH - BLOCK, BLOCK)
            food_y = random.randrange(0, HEIGHT - BLOCK, BLOCK)
            length += 1
            score += 1
            if bite: bite.play()
            if score > highscore:
                write_score(score)

        clock.tick(FPS)

    pygame.quit()
    quit()


game_loop()
