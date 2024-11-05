import pygame
import random
import threading
from mpu6050 import mpu6050
import RPi.GPIO as GPIO
import time

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chapter 2: Fight with them")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Load images
player_img = pygame.image.load('./assets/Abeja.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (80, 50))
enemy_img = pygame.image.load('./assets/enemy_tropper.png').convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (120, 60))
enemy_boss_img = pygame.image.load('./assets/enemyboss.png').convert_alpha()
enemy_boss_img = pygame.transform.scale(enemy_boss_img, (120, 200))
food_img = pygame.image.load('./assets/honeypoint_noblue.png').convert_alpha()
food_img = pygame.transform.scale(food_img, (30, 30))
health_img = pygame.image.load('./assets/honey_pixel.png').convert_alpha()
health_img = pygame.transform.scale(health_img, (40, 40))

# Initialize variables
lives = 3
score = 0
boss_health = 5
font = pygame.font.Font("./assets/happyBeige.ttf", 32)
rect_x = SCREEN_WIDTH // 2 - player_img.get_width() // 2
rect_y = SCREEN_HEIGHT // 2 - player_img.get_height() // 2
enemies = []
food_items = []
health_items = []
bullets = []
enemy_bullets = []
boss_spawned = False
game_paused = False
boss_y = SCREEN_HEIGHT // 2 - enemy_boss_img.get_height() // 2
task = "Collect 10 points!!!"

# Initialize MPU6050
sensor = mpu6050(0x68)

# GPIO Pin configuration for buttons
BUTTON_1_PIN = 17  # Pause
BUTTON_2_PIN = 27  # Shoot
BUZZER_PIN = 24     # Buzzer
LED_PIN1 = 22      # LED 1 (for lives decrease)
LED_PIN2 = 23      # LED 2 (for shooting feedback)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_PIN1, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)

# Ensure the buzzer is off initially
GPIO.output(BUZZER_PIN, GPIO.LOW)  # Start with the buzzer off (active-low configuration)
GPIO.output(LED_PIN1, GPIO.LOW)
GPIO.output(LED_PIN2, GPIO.LOW)

# Debounce settings
debounce_time = 0.1
button1_last_state = GPIO.LOW
button2_last_state = GPIO.LOW

# Function to shoot bullets in a separate thread
def shoot_bullet():
    global bullets
    bullet_x = rect_x + player_img.get_width()
    bullet_y = rect_y + player_img.get_height() // 2
    bullets.append([bullet_x, bullet_y])
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Activate buzzer (sound on)
    GPIO.output(LED_PIN2, GPIO.HIGH)    # LED 2 on
    time.sleep(0.1)                      # Duration of the beep (100 ms)
    GPIO.output(BUZZER_PIN, GPIO.LOW)   # Deactivate buzzer (silent)
    GPIO.output(LED_PIN2, GPIO.LOW)     # LED 2 off

# Function to handle shooting in a thread
def handle_shooting():
    while True:
        button2_state = GPIO.input(BUTTON_2_PIN)
        if button2_state == GPIO.HIGH:
            shoot_bullet()
            time.sleep(debounce_time)  # Debounce delay
        time.sleep(0.01)  # Short sleep to reduce CPU usage

# Start the shooting thread
shooting_thread = threading.Thread(target=handle_shooting, daemon=True)
shooting_thread.start()

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# Function to pause the game
def pause_game():
    global game_paused
    game_paused = not game_paused

# Function to spawn enemies
def spawn_enemy():
    enemy_x = SCREEN_WIDTH
    enemy_y = random.randint(0, SCREEN_HEIGHT - enemy_img.get_height())
    enemies.append([enemy_x, enemy_y])

# Main loop
running = True
clock = pygame.time.Clock()

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Button handling for pause with debounce logic
    button1_state = GPIO.input(BUTTON_1_PIN)
    if button1_state == GPIO.HIGH and button1_last_state == GPIO.LOW:
        pause_game()
        time.sleep(debounce_time)
    button1_last_state = button1_state

    # Game paused screen
    if game_paused:
        screen.fill(BLACK)
        draw_text("Paused", font, WHITE, screen, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50)
        pygame.display.flip()
        continue

    # Get gyro data
    accel_data = sensor.get_accel_data()
    rect_x += int(accel_data['y'] * 2)
    rect_y += int(accel_data['x'] * 2)

    # Boundary checks
    rect_x = max(0, min(rect_x, SCREEN_WIDTH - player_img.get_width()))
    rect_y = max(0, min(rect_y, SCREEN_HEIGHT - player_img.get_height()))

    # Player rectangle for collision
    player_rect = pygame.Rect(rect_x, rect_y, player_img.get_width(), player_img.get_height())

    # Spawn trooper enemies before boss
    if not boss_spawned and random.randint(1, 50) == 1:
        spawn_enemy()

    # Boss spawn logic
    if score >= 10 and not boss_spawned:
        boss_x = SCREEN_WIDTH - enemy_boss_img.get_width()
        boss_spawned = True
        task = "Kill Boss"  # Set task when boss appears

    # Spawn food items only if the boss has not spawned
    if not boss_spawned and random.randint(1, 50) == 1:
        food_x = random.randint(0, SCREEN_WIDTH - food_img.get_width())
        food_y = random.randint(0, SCREEN_HEIGHT - food_img.get_height())
        food_items.append([food_x, food_y])

    # Spawn health items
    if random.randint(1, 200) == 1:
        health_x = random.randint(0, SCREEN_WIDTH - health_img.get_width())
        health_y = random.randint(0, SCREEN_HEIGHT - health_img.get_height())
        health_items.append([health_x, health_y])

    # Move bullets
    for bullet in bullets[:]:
        bullet[0] += 10
        if bullet[0] > SCREEN_WIDTH:
            bullets.remove(bullet)

    # Enemy movement and collision with bullets
    for enemy in enemies[:]:
        enemy[0] -= 5
        enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_img.get_width(), enemy_img.get_height())
        if enemy_rect.colliderect(player_rect):
            lives -= 1
            GPIO.output(LED_PIN1, GPIO.HIGH)   # LED 1 on when lives decrease
            time.sleep(0.1)
            GPIO.output(LED_PIN1, GPIO.LOW)    # LED 1 off
            enemies.remove(enemy)
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 5)
            if bullet_rect.colliderect(enemy_rect):
                score += 1
                bullets.remove(bullet)
                enemies.remove(enemy)

    # Boss shooting
    if boss_spawned and random.randint(1, 60) == 1:  # Reduced frequency of boss's bullets
        enemy_bullets.append([boss_x, boss_y + enemy_boss_img.get_height() // 2])

    # Move boss vertically
    if boss_spawned:
        boss_y += random.choice([-2, 0, 2])  # Boss moves up and down
        boss_y = max(0, min(boss_y, SCREEN_HEIGHT - enemy_boss_img.get_height()))  # Keep within bounds

    # Move enemy bullets and check for collision with player
    for e_bullet in enemy_bullets[:]:
        e_bullet[0] -= 10
        e_bullet_rect = pygame.Rect(e_bullet[0], e_bullet[1], 5, 5)
        if e_bullet_rect.colliderect(player_rect):
            lives -= 1
            enemy_bullets.remove(e_bullet)

    # Collision with health items
    for health in health_items[:]:
        health_rect = pygame.Rect(health[0], health[1], health_img.get_width(), health_img.get_height())
        if player_rect.colliderect(health_rect):
            if lives < 3:  # Only increase lives if below maximum
                lives += 1
            health_items.remove(health)

    # Collision with food items
    for food in food_items[:]:
        food_rect = pygame.Rect(food[0], food[1], food_img.get_width(), food_img.get_height())
        if player_rect.colliderect(food_rect):
            score += 1
            food_items.remove(food)

    # Check for bullet collision with the boss
    if boss_spawned:
        boss_rect = pygame.Rect(boss_x, boss_y, enemy_boss_img.get_width(), enemy_boss_img.get_height())
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 5)
            if bullet_rect.colliderect(boss_rect):
                boss_health -= 1
                bullets.remove(bullet)
                if boss_health <= 0:
                    running = False

    # Drawing
    screen.fill(BLACK)
    screen.blit(player_img, (rect_x, rect_y))

    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

    if boss_spawned:
        screen.blit(enemy_boss_img, (boss_x, boss_y))

    for bullet in bullets:
        pygame.draw.circle(screen, WHITE, (bullet[0], bullet[1]), 5)

    for e_bullet in enemy_bullets:
        pygame.draw.circle(screen, RED, (e_bullet[0], e_bullet[1]), 5)

    for food in food_items:
        screen.blit(food_img, (food[0], food[1]))

    for health in health_items:
        screen.blit(health_img, (health[0], health[1]))

    # Draw score and lives
    draw_text(f"Lives: {lives}", font, WHITE, screen, 10, 10)
    draw_text(f"Score: {score}", font, WHITE, screen, 10, 50)
    if boss_spawned:
        draw_text(f"Boss Health: {boss_health}", font, WHITE, screen, SCREEN_WIDTH - 300, 10)
    draw_text(f"Task: {task}", font, WHITE, screen, 10, 90)
    pygame.display.flip()
    clock.tick(60)

    # Check for game over
    if lives <= 0:
        running = False

# Win screen
    if boss_health <= 0:
        screen.fill(BLACK)
        draw_text("Congratulations! You Win!", font, WHITE, screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50)
    else:
		# Game over screen
        screen.fill(BLACK)
        draw_text("Game Over", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
        draw_text(f"Final Score: {score}", font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)

pygame.display.flip()
time.sleep(3)

# Cleanup
pygame.quit()
GPIO.cleanup()
