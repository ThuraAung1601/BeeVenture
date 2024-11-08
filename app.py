import pygame
import RPi.GPIO as GPIO
import time
import os

# GPIO Pin configuration
BUTTON_1_PIN = 17  # Choose option
BUTTON_2_PIN = 27  # Select option
BUZZER_PIN = 24    # Buzzer

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BeeVenture")
font = pygame.font.Font("./assets/happyBeige.ttf", 32)
clock = pygame.time.Clock()

# Options list
options = ["Chapter 1", "Chapter 2", "Help", "Quit"]
current_option = 0

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0)
ORANGE = (255, 165, 0)

# Load Help Images
help_image1 = pygame.image.load("./assets/help1.png")
help_image2 = pygame.image.load("./assets/help2.png")
help_image1 = pygame.transform.scale(help_image1, (350, 300))
help_image2 = pygame.transform.scale(help_image2, (350, 300))

# Helper function to play tune on buzzer
def play_buzzer_tune():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(0.1)

# Function to display options
def display_options():
    screen.fill(BLACK)

    # Title: "BeeVenture"
    title_text = font.render("BeeVenture", True, ORANGE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Options
    for i, option in enumerate(options):
        color = HIGHLIGHT if i == current_option else WHITE
        text = font.render(option, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 60))
        screen.blit(text, text_rect)
    
    pygame.display.flip()

# Help page function
def show_help_page():
    screen.fill(BLACK)
    screen.blit(help_image1, (50, 150))  # Position of help1.png
    screen.blit(help_image2, (400, 150))  # Position of help2.png
    home_text = font.render("Press Button 1 or 2 to return", True, WHITE)
    screen.blit(home_text, (200, 500))
    pygame.display.flip()

    # Wait for button press to return to main menu
    while True:
        if GPIO.input(BUTTON_1_PIN) == GPIO.HIGH or GPIO.input(BUTTON_2_PIN) == GPIO.HIGH:
            time.sleep(0.5)  # Debounce delay
            break

# Main loop
try:
    while True:
        display_options()

        # Check GPIO buttons for navigation and selection
        if GPIO.input(BUTTON_1_PIN) == GPIO.HIGH:
            current_option = (current_option + 1) % len(options)
            time.sleep(0.2)  # Debounce delay

        if GPIO.input(BUTTON_2_PIN) == GPIO.HIGH:
            play_buzzer_tune()  # Play buzzer only when button 2 is pressed
            # Demonstrating Blocking Execution style
            selected_option = options[current_option]
            if selected_option == "Chapter 1":
                os.system("python3 ch1.py")  # Run Chapter 1 script
            elif selected_option == "Chapter 2":
                os.system("python3 ch2.py")  # Run Chapter 2 script
            elif selected_option == "Help":
                show_help_page()  # Display help page
            elif selected_option == "Quit":
                print("Exiting the program.")
                break  # Exit the main loop
            time.sleep(0.2)  # Debounce delay

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                GPIO.cleanup()
                exit()

        clock.tick(30)  # Limit frame rate

finally:
    GPIO.cleanup()
    pygame.quit()
    print("GPIO cleaned up and program ended.")
