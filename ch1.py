import pygame
import time
import random
from mpu6050 import mpu6050
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chapter 1: Into the field")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Object settings
rect_x = SCREEN_WIDTH // 4  # Fixed X position like Flappy Bird
rect_y = SCREEN_HEIGHT // 2  # Start in the middle of the screen
speed = 2  # Movement speed adjustment factor

# Load and scale the player image
player_image = pygame.image.load("./assets/Abeja.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (80, 50))
player_width = player_image.get_width()
player_height = player_image.get_height()

# Load and scale the lava tile image for obstacles
lava_tile = pygame.image.load("./assets/lava.png").convert_alpha()

# Obstacle settings
obstacle_width = 50
obstacle_gap = 250  # Increased gap between top and bottom obstacles
obstacle_speed = 5  # Speed of the obstacles
obstacle_frequency = 50  # Higher number means fewer obstacles

# Lives and score settings
lives = 3
score = 0
font = pygame.font.Font("./assets/happyBeige.ttf", 32)

# Initialize the obstacles list
obstacles = []  # List to store obstacles

# Initialize MPU6050
sensor = mpu6050(0x68)

# GPIO setup
BUTTON_1_PIN = 17  # Button 1 pin
BUZZER_PIN = 24    # Buzzer pin
LED_PIN1 = 22      # LED pin

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_PIN1, GPIO.OUT)

# Ensure the buzzer and LED are off initially
GPIO.output(BUZZER_PIN, GPIO.LOW)
GPIO.output(LED_PIN1, GPIO.LOW)

# Pause state
paused = False

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Function to draw the player (image instead of circle)
def draw_player(x, y):
    screen.blit(player_image, (x - player_width // 2, y - player_height // 2))

# Function to draw obstacles using lava tiles
def draw_obstacle(x, gap_y):
    # Scale the lava tile to fit the obstacle width and height
    top_obstacle_height = gap_y
    bottom_obstacle_height = SCREEN_HEIGHT - (gap_y + obstacle_gap)

    top_lava = pygame.transform.scale(lava_tile, (obstacle_width, top_obstacle_height))
    bottom_lava = pygame.transform.scale(lava_tile, (obstacle_width, bottom_obstacle_height))

    # Draw the top obstacle (lava tile)
    screen.blit(top_lava, (x, 0))

    # Draw the bottom obstacle (lava tile)
    screen.blit(bottom_lava, (x, gap_y + obstacle_gap))

# Pause game
def toggle_pause():
    global paused
    paused = not paused
    if paused:
        draw_text("Paused", font, WHITE, screen, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)
        pygame.display.flip()

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Button 1 pause toggle
    if GPIO.input(BUTTON_1_PIN) == GPIO.HIGH:
        toggle_pause()
        time.sleep(0.3)  # Debounce delay for button press

    if paused:
        continue  # Skip the game loop if paused

    # Get gyro data
    accel_data = sensor.get_accel_data()

    # Update player position based on gyro Y value (up/down movement)
    rect_y += int(accel_data['x'] * speed)

    # Boundaries check to keep the player within the screen
    if rect_y < player_height // 2:
        rect_y = player_height // 2
    elif rect_y > SCREEN_HEIGHT - player_height // 2:
        rect_y = SCREEN_HEIGHT - player_height // 2

    # Spawn obstacles
    if random.randint(1, obstacle_frequency) == 1:
        obstacle_x = SCREEN_WIDTH
        gap_y = random.randint(100, SCREEN_HEIGHT - 100 - obstacle_gap)
        obstacles.append([obstacle_x, gap_y])

    # Move and remove obstacles
    for obstacle in obstacles[:]:
        obstacle[0] -= obstacle_speed  # Move obstacle left
        if obstacle[0] < -obstacle_width:
            obstacles.remove(obstacle)  # Remove off-screen obstacles
            score += 1  # Increment score when obstacle is successfully passed
            if score >= 20:
                running = False

    # Check for collisions
    player_rect = pygame.Rect(rect_x - player_width // 2, rect_y - player_height // 2, player_width, player_height)

    for obstacle in obstacles:
        top_rect = pygame.Rect(obstacle[0], 0, obstacle_width, obstacle[1])
        bottom_rect = pygame.Rect(obstacle[0], obstacle[1] + obstacle_gap, obstacle_width, SCREEN_HEIGHT - (obstacle[1] + obstacle_gap))
        
        if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
            lives -= 1

            # Buzzer and LED feedback for life loss
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on buzzer
            GPIO.output(LED_PIN1, GPIO.HIGH)    # Turn on LED
            time.sleep(0.1)                     # Short delay for feedback
            GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn off buzzer
            GPIO.output(LED_PIN1, GPIO.LOW)     # Turn off LED

            obstacles.remove(obstacle)  # Remove the collided obstacle
            if lives <= 0:
                running = False

    # Clear the screen
    screen.fill(BLACK)

    # Draw the player (image)
    draw_player(rect_x, rect_y)

    # Draw the obstacles (lava tiles)
    for obstacle in obstacles:
        draw_obstacle(obstacle[0], obstacle[1])

    # Draw the lives and score
    draw_text(f"Task: Pass 20 barriers!!!", font, WHITE, screen, 10, 10)
    draw_text(f"Lives: {lives}", font, WHITE, screen, 10, 40)
    draw_text(f"Barriers: {score}", font, WHITE, screen, 10, 70)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Display Game Over screen
screen.fill(BLACK)
if score >= 20:
    draw_text("You win this chapter!!!", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Barriers: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)
else:
    draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
    draw_text(f"Final Barriers: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40)

pygame.display.flip()
time.sleep(3)

pygame.quit()
GPIO.cleanup()
