import pygame
import sys
import os
import RPi.GPIO as GPIO
import time

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
screen_width = 800
screen_height = 600
black = (0, 0, 0)
white = (255, 255, 255)

# Set up the display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Front Page")

# Font settings
font = pygame.font.Font("./assets/happyBeige.ttf", 74)
button_font = pygame.font.Font("./assets/happyBeige.ttf", 50)

# Define button labels
buttons = ["Level 1", "Level 2", "Level 3", "Help (?)", "Quit"]
selected_index = 0

# Set up GPIO
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
button_pin1 = 11  # Button 1 for navigating up
button_pin2 = 13  # Button 2 for selecting
led_pins = [36, 38, 40]  # LED pins

# Set up the LED pins
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initialize LEDs to OFF

GPIO.setup(button_pin1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_pin2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def draw_buttons():
    for i, button in enumerate(buttons):
        if i == selected_index:
            label = button_font.render(button, True, white)
        else:
            label = button_font.render(button, True, (100, 100, 100))  # dimmed color for unselected
        text_rect = label.get_rect(center=(screen_width // 2, 200 + i * 60))
        screen.blit(label, text_rect)

def blink_leds():
    for _ in range(3):  # Blink 3 times
        for pin in led_pins:
            GPIO.output(pin, GPIO.HIGH)  # Turn on LEDs
        time.sleep(0.1)  # Keep LEDs on for 100ms
        for pin in led_pins:
            GPIO.output(pin, GPIO.LOW)  # Turn off LEDs
        time.sleep(0.1)  # Keep LEDs off for 100ms

# Main loop
try:
    while True:
        screen.fill(black)  # Clear screen with black color

        # Title
        title_label = font.render("BeeVenture", True, white)
        title_rect = title_label.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_label, title_rect)

        # Draw buttons
        draw_buttons()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                GPIO.cleanup()  # Clean up GPIO
                sys.exit()

        # Check GPIO inputs for button presses
        if GPIO.input(button_pin1) == GPIO.HIGH:  # Button 1
            selected_index = (selected_index - 1) % len(buttons)  # Navigate up
            time.sleep(0.2)  # Debounce delay

        if GPIO.input(button_pin2) == GPIO.HIGH:  # Button 2
            selected_button = buttons[selected_index]
            blink_leds()  # Blink LEDs on select button press
            
            if selected_button == "Quit":
                pygame.quit()  # Quit Pygame
                GPIO.cleanup()  # Clean up GPIO
                sys.exit()     # Exit the program
            elif selected_button == "Level 1":
                os.system("python testAni.py")  # Run level 1 script
            elif selected_button == "Level 2":
                os.system("python test.py")  # Run level 2 script
            elif selected_button == "Level 3":
                os.system("python test3.py")  # Run level 3 script
            else:
                print(f"Pressed: {selected_button}")  # Print the selected button
            time.sleep(0.2)  # Debounce delay

        pygame.display.flip()  # Update the display

finally:
    # Clean up GPIO on exit
    GPIO.cleanup()
