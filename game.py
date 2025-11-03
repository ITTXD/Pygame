import pygame
import sys
import os

# --- Initialize Pygame ---
pygame.init()

# --- Screen Setup ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Drag Line Catcher")

# --- Background Image ---
# Load and scale the background image to fit the entire window
background_image = pygame.image.load(os.path.join("object", "SKY3.png")).convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Music ---
pygame.mixer.music.load(os.path.join("music", "music.mp3"))
pygame.mixer.music.set_volume(0.1)  # Set initial volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Loop indefinitely

# --- Load fall sound effect ---
fall_sound = pygame.mixer.Sound(os.path.join("sound effect", "falldown.mp3"))
fall_sound.set_volume(1.0)
fall_sound_played = False

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- Clock for controlling frame rate ---
clock = pygame.time.Clock()


# --- Object Settings ---
object_size = 100
object_speed = 3
objects = []
# --- Key Image (replaces blue line) ---
key_image = pygame.image.load(os.path.join("object", "keyu.png")).convert_alpha()
# Scale key to match object (cj) size
"""
BIG MARK: ADJUST key_width HERE TO MAKE THE KEY WIDER
Increase this value to widen the key platform.
"""
key_width = 250  # <--- CHANGE THIS NUMBER TO MAKE KEY WIDER
key_height = 200
key_image = pygame.transform.scale(key_image, (key_width, key_height))
# Position key in the right corner (adjust these values as needed)
key_x = SCREEN_WIDTH - key_width - 40  # 20 pixels from right edge
key_y = SCREEN_HEIGHT - 500
key_speed = 6
# Invisible floor: objects stop when they reach 50 pixels above the bottom
floor_y = SCREEN_HEIGHT - 110  # y-coordinate where objects rest

# --- Load Object Images ---
ground_image = pygame.image.load(os.path.join("object", "ground1.png")).convert_alpha()
# Do not stretch; keep original size
ground_rect = ground_image.get_rect()
ground_rect.bottomleft = (0, floor_y)
object_image = pygame.image.load(os.path.join("object", "cj-2.png")).convert_alpha()
object_image = pygame.transform.scale(object_image, (object_size, object_size))

# --- Initial Object Placement ---
# Start with one object already on screen resting on the key (positioned to the right corner)
objects.append([key_x + key_width // 2 - object_size // 2, key_y - 20])

# --- Game Loop ---
running = True
while running:
    # --- Draw Background ---
    # Blit the background image to cover the entire screen each frame
    screen.blit(background_image, (0, 0))

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Key Movement with Mouse Drag ---
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:  # Left mouse button held
        # Center the key on the mouse x
        key_x = mouse_x - key_width // 2
        # Keep key within screen bounds (right corner adjustment)
        key_x = max(0, min(key_x, SCREEN_WIDTH - key_width))

    # --- Update Falling Objects ---
    for obj in objects[:]:
        # Check if object is on the key
        obj_bottom = obj[1] + object_size
        if (obj_bottom >= key_y and obj_bottom <= key_y + key_height and
            obj[0] + object_size >= key_x and obj[0] <= key_x + key_width -80  ):
            # Object is on the key, keep it resting
            obj[1] = key_y - 20
        else:
            # Object is not on the key, make it fall
            obj[1] += object_speed

        # Keep object on invisible floor if it reaches it
        if obj[1] + object_size > floor_y:
            obj[1] = floor_y - object_size

        # Play sound once when object hits the ground
        # Fixed: now plays only once per landing by checking both floor contact and previous state
        if obj[1] == floor_y - object_size and obj_bottom != key_y and not fall_sound_played:
            fall_sound.play(0)  # Changed to 0 so it plays once
            fall_sound_played = True
        # Reset the flag when the object is no longer resting on the floor
        # floor_y - object_size is the y-coordinate where the object's bottom touches the invisible floor
        elif obj[1] != floor_y - object_size:
            fall_sound_played = False

    # --- Draw Key ---
    screen.blit(key_image, (key_x, key_y))

    # --- Draw Falling Objects ---
    for obj in objects:
        screen.blit(object_image, (obj[0], obj[1]))

    # --- Draw Ground Images ---
    # Draw ground image at the same level as invisible floor, without stretching
    screen.blit(ground_image, (400, 350))
    screen.blit(ground_image, (300, 350))
    screen.blit(ground_image, (200, 350))
    screen.blit(ground_image, (100, 350))
    screen.blit(ground_image, (0, 350))  # second ground

    # --- Update Display ---
    pygame.display.flip()
    clock.tick(60)

    # --- Additional Event Handling (for CMD+I quit) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i and pygame.key.get_mods() & pygame.KMOD_META:
                running = False

# --- Quit Game ---
pygame.quit()
sys.exit()
