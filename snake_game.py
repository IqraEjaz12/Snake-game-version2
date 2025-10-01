import pygame
import sys
import random

# Game settings
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
CELL_SIZE = 20
FPS = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (40, 40, 40)

LEVEL_COLORS = [
    (30, 30, 30),   # Level 1: dark gray
    (20, 50, 80),   # Level 2: blueish
    (50, 20, 50),   # Level 3: purple
    (20, 80, 40),   # Level 4: greenish
]

LEVEL_OBSTACLES = [
    [],  # Level 1: no obstacles
    [((10, 10), (20, 1)), ((10, 25), (20, 1))],  # Level 2: horizontal walls
    [((5, 5), (1, 20)), ((25, 5), (1, 20))],     # Level 3: vertical walls
    [((15, 0), (1, 30)), ((0, 15), (30, 1))],    # Level 4: cross
]

LEVEL_UP_SCORE = 5  # Score needed to level up
MAX_LEVEL = len(LEVEL_COLORS)


import os

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game with Levels')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# Asset loading helpers
def load_image(name, size):
    path = os.path.join('assets', name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        # Fallback: draw a colored surface
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if 'snake_head' in name:
            pygame.draw.ellipse(surf, (60, 180, 60), surf.get_rect())
            pygame.draw.ellipse(surf, (0, 0, 0), (size[0]//2, size[1]//4, size[0]//4, size[1]//4))
        elif 'snake_body' in name:
            pygame.draw.ellipse(surf, (80, 200, 80), surf.get_rect())
        elif 'food' in name:
            pygame.draw.ellipse(surf, (200, 40, 40), surf.get_rect())
        elif 'obstacle' in name:
            pygame.draw.rect(surf, (100, 100, 100), surf.get_rect(), border_radius=8)
        elif 'background' in name:
            surf.fill((30, 60, 30))
        return surf

snake_head_img = load_image('snake_head.png', (CELL_SIZE, CELL_SIZE))
snake_body_img = load_image('snake_body.png', (CELL_SIZE, CELL_SIZE))
food_img = load_image('food.png', (CELL_SIZE, CELL_SIZE))
obstacle_img = load_image('obstacle.png', (CELL_SIZE, CELL_SIZE))
background_img = load_image('background.png', (SCREEN_WIDTH, SCREEN_HEIGHT))


def draw_text(text, pos, color=WHITE, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(surf, rect)


def draw_obstacles(obstacles):
    for (x, y), (w, h) in obstacles:
        for i in range(w):
            for j in range(h):
                screen.blit(obstacle_img, ((x + i) * CELL_SIZE, (y + j) * CELL_SIZE))


def random_food(snake, obstacles):
    while True:
        x = random.randint(0, (SCREEN_WIDTH // CELL_SIZE) - 1)
        y = random.randint(0, (SCREEN_HEIGHT // CELL_SIZE) - 1)
        food_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        collision = any(food_rect.colliderect(pygame.Rect(ox * CELL_SIZE, oy * CELL_SIZE, ow * CELL_SIZE, oh * CELL_SIZE))
                        for (ox, oy), (ow, oh) in obstacles)
        if (x, y) not in snake and not collision:
            return (x, y)


def main():
    running = True
    direction = (1, 0)
    snake = [(10, 10), (9, 10), (8, 10)]
    score = 0
    level = 1
    speed = FPS
    obstacles = LEVEL_OBSTACLES[level - 1]
    food = random_food(snake, obstacles)
    game_over = False
    move_delay = 0

    while running:
        # Draw background image or color
        screen.blit(background_img, (0, 0))
        # Optionally tint for level
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*LEVEL_COLORS[level - 1], 60))
        screen.blit(overlay, (0, 0))
        draw_obstacles(obstacles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        direction = (1, 0)
                else:
                    if event.key == pygame.K_r:
                        return main()

        if not game_over:
            move_delay += clock.get_time()
            if move_delay > 1000 // speed:
                move_delay = 0
                new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                # Check wall collision
                if (
                    new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH // CELL_SIZE or
                    new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT // CELL_SIZE
                ):
                    game_over = True
                # Check self collision
                elif new_head in snake:
                    game_over = True
                # Check obstacle collision
                else:
                    head_rect = pygame.Rect(new_head[0] * CELL_SIZE, new_head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if any(head_rect.colliderect(pygame.Rect(ox * CELL_SIZE, oy * CELL_SIZE, ow * CELL_SIZE, oh * CELL_SIZE))
                           for (ox, oy), (ow, oh) in obstacles):
                        game_over = True
                    else:
                        snake.insert(0, new_head)
                        if new_head == food:
                            score += 1
                            if score % LEVEL_UP_SCORE == 0 and level < MAX_LEVEL:
                                level += 1
                                obstacles = LEVEL_OBSTACLES[level - 1]
                                speed += 3
                            food = random_food(snake, obstacles)
                        else:
                            snake.pop()

        # Draw snake with images
        for i, (x, y) in enumerate(snake):
            pos = (x * CELL_SIZE, y * CELL_SIZE)
            if i == 0:
                # Head
                screen.blit(snake_head_img, pos)
            else:
                screen.blit(snake_body_img, pos)
        # Draw food
        screen.blit(food_img, (food[0] * CELL_SIZE, food[1] * CELL_SIZE))
        # Draw UI
        draw_text(f'Score: {score}', (10, 10))
        draw_text(f'Level: {level}', (SCREEN_WIDTH - 120, 10))
        if game_over:
            draw_text('GAME OVER', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30), color=RED, center=True)
            draw_text('Press R to Restart', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10), color=WHITE, center=True)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
