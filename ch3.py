import pygame
import time
import random
from mpu6050 import mpu6050

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gyro Controlled Movement")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)   # Player's ship
RED = (255, 0, 0)    # Red enemy (stone)
GREEN = (0, 255, 0)  # Food
BLACK = (0, 0, 0)    # Black enemy (enemy ship)
GOLD = (255, 215, 0)  # Gold color

# Object settings
circle_radius = 25
rect_x = SCREEN_WIDTH // 2
rect_y = SCREEN_HEIGHT // 2
speed = 2  # Movement speed adjustment factor

# Lives and score settings
lives = 3
score = 0
enemies_killed = 0
stones_shot = 0
font = pygame.font.Font(None, 36)

# Obstacle settings
obstacle_size = 50
obstacle_speed = 5

# Food settings
food_radius = 15
food_frequency = 30  # Higher number means fewer food items
food_items = []  # List to store food items

# Gold item settings
gold_items = []  # List to store gold items
last_gold_spawn_time = 0  # Timer for gold item spawn
gold_spawn_interval = 5000  # 5 seconds in milliseconds

# Green triangle settings
green_triangles = []  # List to store green triangles
last_green_spawn_time = 0  # Timer for green triangle spawn
green_spawn_interval = 15000  # 15 seconds in milliseconds
green_triangle_size = 30  # Size of the green triangle

# Enemy settings
obstacles = []  # Red enemies
shooting_enemies = []  # Black enemies
enemy_bullets = []  # Bullets shot by black enemies
player_projectiles = []  # List to store player projectiles

# Initialize MPU6050
sensor = mpu6050(0x68)

# Main loop
running = True
clock = pygame.time.Clock()

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Function to draw the player (circle)
def draw_player(x, y):
    pygame.draw.circle(screen, BLUE, (x, y), circle_radius)

# Function to draw red enemy (triangle)
def draw_enemy(x, y):
    points = [(x, y), (x + obstacle_size, y + obstacle_size // 2), (x + obstacle_size, y - obstacle_size // 2)]
    pygame.draw.polygon(screen, RED, points)

# Function to draw food (green circle)
def draw_food(x, y):
    pygame.draw.circle(screen, GREEN, (x, y), food_radius)

# Function to draw black enemy (square)
def draw_shooting_enemy(x, y):
    pygame.draw.rect(screen, BLACK, (x, y, obstacle_size, obstacle_size))

# Function to draw player projectile (small blue circle)
def draw_player_projectile(x, y):
    pygame.draw.circle(screen, BLUE, (x, y), 5)

# Function to draw enemy bullets (small black circle)
def draw_enemy_bullet(x, y):
    pygame.draw.circle(screen, BLACK, (x, y), 5)

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Shoot projectile when space is pressed
                player_projectiles.append([rect_x, rect_y])

    # Get gyro data
    accel_data = sensor.get_accel_data()

    # Update player position based on gyro X and Y values
    rect_x += int(accel_data['x'] * speed)
    rect_y += int(accel_data['y'] * speed)

    # Boundaries check to keep the player within the screen
    if rect_x < circle_radius:
        rect_x = circle_radius
    elif rect_x > SCREEN_WIDTH - circle_radius:
        rect_x = SCREEN_WIDTH - circle_radius
    if rect_y < circle_radius:
        rect_y = circle_radius
    elif rect_y > SCREEN_HEIGHT - circle_radius:
        rect_y = SCREEN_HEIGHT - circle_radius

    # Spawn red enemies (obstacles)
    if random.randint(1, 50) == 1:
        obstacle_x = SCREEN_WIDTH
        obstacle_y = random.randint(obstacle_size, SCREEN_HEIGHT - obstacle_size)
        obstacles.append([obstacle_x, obstacle_y])

    # Spawn black enemies (shooting enemies)
    if random.randint(1, 100) == 1:
        shooting_enemy_x = SCREEN_WIDTH
        shooting_enemy_y = random.randint(obstacle_size, SCREEN_HEIGHT - obstacle_size)
        shooting_enemies.append([shooting_enemy_x, shooting_enemy_y])

    # Spawn food items
    if random.randint(1, 100) == 1:
        food_x = random.randint(food_radius, SCREEN_WIDTH - food_radius)
        food_y = random.randint(food_radius, SCREEN_HEIGHT - food_radius)
        food_items.append([food_x, food_y])

    # Move and remove obstacles (red enemies)
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_speed  # Move obstacle left
        if obstacle[0] < -obstacle_size:
            obstacles.remove(obstacle)  # Remove off-screen obstacles

    # Move and remove shooting enemies (black enemies)
    for enemy in shooting_enemies[:]:
        enemy[0] -= obstacle_speed  # Move enemy left
        if enemy[0] < -obstacle_size:
            shooting_enemies.remove(enemy)  # Remove off-screen enemies
        # Enemy shooting
        if random.randint(1, 100) == 1:  # Randomly shoot
            enemy_bullets.append([enemy[0], enemy[1] + obstacle_size // 2])  # Shoot from the middle of the enemy

    # Move player projectiles
    for p_projectile in player_projectiles[:]:
        p_projectile[0] += 10  # Move player projectile right
        if p_projectile[0] > SCREEN_WIDTH:
            player_projectiles.remove(p_projectile)  # Remove off-screen player projectiles

    # Move enemy bullets
    for bullet in enemy_bullets[:]:
        bullet[0] -= 10  # Move bullet left
        if bullet[0] < 0:
            enemy_bullets.remove(bullet)  # Remove off-screen bullets

    # Check for player collision with food
    player_rect = pygame.Rect(rect_x - circle_radius, rect_y - circle_radius, circle_radius * 2, circle_radius * 2)
    for food in food_items[:]:
        food_rect = pygame.Rect(food[0] - food_radius, food[1] - food_radius, food_radius * 2, food_radius * 2)
        if player_rect.colliderect(food_rect):
            score += 1
            food_items.remove(food)

    # Check for player collisions with enemies
    for obstacle in obstacles[:]:
        obstacle_rect = pygame.Rect(obstacle[0], obstacle[1] - obstacle_size // 2, obstacle_size, obstacle_size)
        if player_rect.colliderect(obstacle_rect):
            lives -= 1  # Reduce lives
            obstacles.remove(obstacle)  # Remove collided obstacle
            break  # Exit after collision

    for enemy in shooting_enemies[:]:
        enemy_rect = pygame.Rect(enemy[0], enemy[1], obstacle_size, obstacle_size)
        if player_rect.colliderect(enemy_rect):
            lives -= 1  # Reduce lives
            shooting_enemies.remove(enemy)  # Remove collided enemy
            break  # Exit after collision

    # Check if lives reach zero
    if lives <= 0:
        running = False  # End the game loop if lives are 0
    
    # Check for win conditions
    if score >= 10 and enemies_killed >= 5 and stones_shot >= 10:
        running = False  # End the game loop if win conditions are met
        print("You Win!")  # Optional: print win message in console

    # Check for player projectiles hitting enemies
    for p_projectile in player_projectiles[:]:
        p_rect = pygame.Rect(p_projectile[0] - 5, p_projectile[1] - 5, 10, 10)

        # Check collision with red enemies
        for obstacle in obstacles[:]:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1] - obstacle_size // 2, obstacle_size, obstacle_size)
            if p_rect.colliderect(obstacle_rect):
                stones_shot += 1
                obstacles.remove(obstacle)
                player_projectiles.remove(p_projectile)
                break

        # Check collision with black enemies
        for enemy in shooting_enemies[:]:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], obstacle_size, obstacle_size)
            if p_rect.colliderect(enemy_rect):
                enemies_killed += 1
                shooting_enemies.remove(enemy)
                player_projectiles.remove(p_projectile)
                break

    # Check for enemy bullets hitting the player
    for bullet in enemy_bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], 10, 10)
        if bullet_rect.colliderect(player_rect):
            lives -= 1  # Reduce lives if hit by enemy bullet
            enemy_bullets.remove(bullet)  # Remove collided bullet
            break  # Exit after collision

    # Clear the screen
    screen.fill(WHITE)

    # Draw the player
    draw_player(rect_x, rect_y)

    # Draw red enemies
    for obstacle in obstacles:
        draw_enemy(obstacle[0], obstacle[1])

    # Draw black enemies
    for enemy in shooting_enemies:
        draw_shooting_enemy(enemy[0], enemy[1])

    # Draw food items
    for food in food_items:
        draw_food(food[0], food[1])

    # Draw player projectiles
    for p_projectile in player_projectiles:
        draw_player_projectile(p_projectile[0], p_projectile[1])

    # Draw enemy bullets
    for bullet in enemy_bullets:
        draw_enemy_bullet(bullet[0], bullet[1])

    # Draw the lives and scores
    draw_text(f"Lives: {lives}", font, (0, 0, 0), screen, 10, 10)
    draw_text(f"Score: {score}", font, (0, 0, 0), screen, 10, 40)
    draw_text(f"Enemies Killed: {enemies_killed}", font, (0, 0, 0), screen, 10, 70)
    draw_text(f"Stones Shot: {stones_shot}", font, (0, 0, 0), screen, 10, 100)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Game Over screen
screen.fill(WHITE)
if score >= 10 and enemies_killed >= 5 and stones_shot >= 10:
    draw_text("You Win!", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Score: {score}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)
    draw_text(f"Enemies Killed: {enemies_killed}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80)
    draw_text(f"Stones Shot: {stones_shot}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120)

else:
    draw_text("Game Over", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Score: {score}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)
    draw_text(f"Enemies Killed: {enemies_killed}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80)
    draw_text(f"Stones Shot: {stones_shot}", font, (0, 0, 0), screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120)

pygame.display.flip()
time.sleep(3)
pygame.quit()
