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
pygame.display.set_caption("Chapter 2")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load and scale images
player_img = pygame.image.load('./assets/Abeja.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (80, 50))

food_img = pygame.image.load('./assets/honeypoint_noblue.png').convert_alpha()
food_img = pygame.transform.scale(food_img, (30, 30))

enemy_img = pygame.image.load('./assets/enemy_tropper.png').convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (120, 60))

health_img = pygame.image.load('./assets/honey_pixel.png').convert_alpha()
health_img = pygame.transform.scale(health_img, (40, 40))

# Lives and score settings
lives = 3
score = 0
font = pygame.font.Font("./assets/happyBeige.ttf", 32)

# Player initial position
rect_x = SCREEN_WIDTH // 2 - player_img.get_width() // 2  # Centered horizontally
rect_y = SCREEN_HEIGHT // 2 - player_img.get_height() // 2  # Centered vertically

# Obstacle settings
obstacle_speed = 5  # Speed of the obstacles
obstacle_frequency = 50  # Higher number means fewer obstacles

# Food settings
food_items = []  # List to store food items
food_frequency = 80  # Higher number means fewer food items

# Health item settings (using health_img)
health_items = []  # List to store health items
last_health_spawn_time = pygame.time.get_ticks()  # Time of last health item spawn
health_spawn_interval = 15000  # 15 seconds in milliseconds

# Initialize the obstacles list
obstacles = []  # List to store obstacles

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

# Function to draw sprites
def draw_sprite(image, x, y):
    screen.blit(image, (x, y))

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get gyro data
    accel_data = sensor.get_accel_data()

    # Update player position based on gyro X and Y values
    rect_x += int(accel_data['y'] * 2)
    rect_y += int(accel_data['x'] * 2)

    # Boundaries check to keep the player within the screen
    rect_x = max(0, min(rect_x, SCREEN_WIDTH - player_img.get_width()))
    rect_y = max(0, min(rect_y, SCREEN_HEIGHT - player_img.get_height()))

    # Spawn obstacles
    if random.randint(1, obstacle_frequency) == 1:
        obstacle_x = SCREEN_WIDTH
        obstacle_y = random.randint(0, SCREEN_HEIGHT - enemy_img.get_height())
        obstacles.append([obstacle_x, obstacle_y])

    # Move and remove obstacles
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_speed  # Move obstacle left
        if obstacle[0] < -enemy_img.get_width():
            obstacles.remove(obstacle)  # Remove off-screen obstacles

    # Spawn food
    if random.randint(1, food_frequency) == 1:
        food_x = random.randint(0, SCREEN_WIDTH - food_img.get_width())
        food_y = random.randint(0, SCREEN_HEIGHT - food_img.get_height())
        food_items.append([food_x, food_y])

    # Spawn health items every 15 seconds
    current_time = pygame.time.get_ticks()
    if current_time - last_health_spawn_time >= health_spawn_interval:
        health_x = SCREEN_WIDTH
        health_y = random.randint(0, SCREEN_HEIGHT - health_img.get_height())
        health_items.append([health_x, health_y])
        last_health_spawn_time = current_time  # Reset the last spawn time

    # Move and remove health items
    for health in health_items[:]:
        health[0] -= obstacle_speed  # Move health item left
        if health[0] < -health_img.get_width():
            health_items.remove(health)  # Remove off-screen health items

    # Check for collisions
    player_rect = pygame.Rect(rect_x, rect_y, player_img.get_width(), player_img.get_height())

    for obstacle in obstacles:
        obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], enemy_img.get_width(), enemy_img.get_height())
        if player_rect.colliderect(obstacle_rect):
            lives -= 1
            obstacles.remove(obstacle)
            if lives <= 0 or score >= 15:
                running = False

    for food in food_items[:]:
        food_rect = pygame.Rect(food[0], food[1], food_img.get_width(), food_img.get_height())
        if player_rect.colliderect(food_rect):
            score += 1  # Reduced score increase rate
            food_items.remove(food)

    for health in health_items[:]:
        health_rect = pygame.Rect(health[0], health[1], health_img.get_width(), health_img.get_height())
        if player_rect.colliderect(health_rect):
            if lives < 3:  # Only increase lives if less than 3
                lives += 1
            health_items.remove(health)  # Remove the health item on collision

    # Clear the screen
    screen.fill(BLACK)  # Set background to black

    # Draw the player
    draw_sprite(player_img, rect_x, rect_y)

    # Draw the obstacles
    for obstacle in obstacles:
        draw_sprite(enemy_img, obstacle[0], obstacle[1])

    # Draw the food
    for food in food_items:
        draw_sprite(food_img, food[0], food[1])

    # Draw the health items
    for health in health_items:
        draw_sprite(health_img, health[0], health[1])

    # Draw the lives and score
    draw_text(f"Task: Collect 15 points!!!", font, WHITE, screen, 10, 10)
    draw_text(f"Lives: {lives}", font, WHITE, screen, 10, 40)
    draw_text(f"Points: {score}", font, WHITE, screen, 10, 70)
    
    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Display Game Over screen
screen.fill(BLACK)  # Set background to black
if score >= 15:
    draw_text("You win this chapter!!!", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Points: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)
else:
    draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Points: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)

pygame.display.flip()
time.sleep(5)

pygame.quit()
