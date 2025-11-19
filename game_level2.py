import pygame
import sys
import os
import time
class Heart:
    """A single heart icon with its own position and visibility."""
    def __init__(self, image, x, y):
        
        self.image = image
        self.x = x
        self.y = y
        self.visible = True  # You can toggle this later if needed

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))


class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Drag Line Catcher")

        # Background
        self.background_image = pygame.image.load(os.path.join("background", "night.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Music
        pygame.mixer.music.load(os.path.join("music", "music.mp3"))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        # Sound
        self.fall_sound = pygame.mixer.Sound(os.path.join("sound effect", "falldown.mp3"))
        self.fall_sound.set_volume(1.0)
        self.fall_sound_played = False

        # Victory sound
        self.victory_sound = pygame.mixer.Sound(os.path.join("music", "Victorysound.mp3"))
        self.victory_sound.set_volume(1.0)
        self.victory_played = False

        # Fade and next level button
        self.fade_alpha = 0
        self.fading = False
        self.fade_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.fade_surface.fill((0, 0, 0))
        self.next_level_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 80, self.SCREEN_HEIGHT // 2 - 25, 160, 50)
        self.button_font = pygame.font.SysFont(None, 36)
        self.level_complete = False

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)

        # Clock
        self.clock = pygame.time.Clock()

        # Object settings
        self.object_size = 100
        self.object_speed = 3
        self.objects = []

        # CJ walking speed (adjustable) - slower default
        self.cj_walk_speed = 2

        # Pixel Heart
        heart_scale = 0.07
        heart_img = pygame.image.load(os.path.join("object", "pixelheart.png")).convert_alpha()
        heart_w = int(heart_img.get_width() * heart_scale)
        heart_h = int(heart_img.get_height() * heart_scale)
        heart_img = pygame.transform.scale(heart_img, (heart_w, heart_h))
        # Create three separate Heart objects
        self.heart1 = Heart(heart_img, 10, 50)
        self.heart2 = Heart(heart_img, 10 + heart_w, 50)
        self.heart3 = Heart(heart_img, 10 + 2 * heart_w, 50)

        # Shield stat: starts at 0, increments when CJ hits shield
        self.shield_stat = 0

        # Spike
        spike_scale = 0.15
        spike_img = pygame.image.load(os.path.join("object", "spike.png")).convert_alpha()
        spike_w = int(spike_img.get_width() * spike_scale)
        spike_h = int(spike_img.get_height() * spike_scale)
        self.spike_image = pygame.transform.scale(spike_img, (spike_w, spike_h))
        # Spike fixed at 509, 350
        self.spike_x = 509
        self.spike_y = 350
        self.spike_stuck = True  # Always fixed

        # Key
        self.key_width, self.key_height = 250, 200
        self.key_image = pygame.image.load(os.path.join("object", "keyu.png")).convert_alpha()
        self.key_image = pygame.transform.scale(self.key_image, (self.key_width, self.key_height))
        self.key_x = self.SCREEN_WIDTH // 2 - self.key_width // 2
        self.key_y = self.SCREEN_HEIGHT - 510
        self.dragging_key = False

        # Shield
        self.shield_size = 75
        self.shield_image = pygame.image.load(os.path.join("object", "sheild-2.png")).convert_alpha()
        self.shield_image = pygame.transform.scale(self.shield_image, (self.shield_size, self.shield_size))
        self.shield_x = 60
        self.shield_y = self.key_y
        self.shield_falling = False
        self.shield_fall_speed = 3
        self.shield_hit_ground_flag = False

        # Second key
        self.second_key_width, self.second_key_height = 250, 200
        self.second_key_image = pygame.image.load(os.path.join("object", "keyu.png")).convert_alpha()
        self.second_key_image = pygame.transform.scale(self.second_key_image, (self.second_key_width, self.second_key_height))
        self.second_key_x = self.shield_x + self.shield_size // 2 - self.second_key_width // 2
        self.second_key_y = self.key_y
        self.dragging_second_key = False

        # Floor
        self.floor_y = self.SCREEN_HEIGHT - 110

        # Ground
        self.ground_image = pygame.image.load(os.path.join("object", "ground1.png")).convert_alpha()
        self.ground_rect = self.ground_image.get_rect()
        self.ground_rect.bottomleft = (0, self.floor_y)

        # Object
        self.object_image = pygame.image.load(os.path.join("object", "cj-2.png")).convert_alpha()
        self.object_image = pygame.transform.scale(self.object_image, (self.object_size, self.object_size))

        # Volume button
        self.volume_button_rect = pygame.Rect(self.SCREEN_WIDTH - 100, 20, 80, 40)
        self.volume_on = True
        self.volume_font = pygame.font.SysFont(None, 24)

        # Initial object
        self.objects.append([self.key_x + self.key_width // 2 - self.object_size // 2, self.key_y - 30])

        # State flags
        self.key_disappear = False
        self.second_key_disappear = False
        self.shield_disappear = False
        # CJ walking toward diamond
        self.cj_walking = False
        self.cj_walking_to_shield = False
        self.cj_walking_to_diamond = False

        # Heart cooldown system
        self.heart_cooldown = False
        self.heart_cooldown_start = 0
        self.heart_cooldown_duration = 5  # 5 seconds

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i and pygame.key.get_mods() & pygame.KMOD_META:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.volume_button_rect.collidepoint(event.pos):
                    self.toggle_volume()
                else:
                    self.check_drag_start(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_key = False
                self.dragging_second_key = False
        return True

    def hide_next_heart(self):
        # Hide hearts one by one in order: heart3, heart2, heart1
        if self.heart_cooldown:
            return  # Do not hide if cooldown is active
        # If shield stat > 0, consume shield instead of hiding heart
        if self.shield_stat > 0:
            self.shield_stat -= 1
            return
        # If shield_stat is 0, decrease heart
        if self.heart3.visible:
            self.heart3.visible = False
            self.start_heart_cooldown()
        elif self.heart2.visible:
            self.heart2.visible = False
            self.start_heart_cooldown()
        elif self.heart1.visible:
            self.heart1.visible = False
            self.start_heart_cooldown()

    def start_heart_cooldown(self):
        self.heart_cooldown = True
        self.heart_cooldown_start = time.time()

    def update_heart_cooldown(self):
        if self.heart_cooldown:
            if time.time() - self.heart_cooldown_start >= self.heart_cooldown_duration:
                self.heart_cooldown = False

    def toggle_volume(self):
        self.volume_on = not self.volume_on
        vol = 0.1 if self.volume_on else 0.0
        pygame.mixer.music.set_volume(vol)
        self.fall_sound.set_volume(vol)
        self.victory_sound.set_volume(vol)

    def check_drag_start(self, pos):
        mouse_x, mouse_y = pos
        key_rect = pygame.Rect(self.key_x, self.key_y, self.key_width, self.key_height)
        second_key_rect = pygame.Rect(self.second_key_x, self.second_key_y, self.second_key_width, self.second_key_height)
        if key_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_key = True
        elif second_key_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_second_key = True
            # Shield falls if it is NOT resting on the key
            if not (self.shield_x + self.shield_size >= self.second_key_x and
                    self.shield_x <= self.second_key_x + self.second_key_width):
                self.shield_falling = True
                # Remove the key when shield starts falling
                self.second_key_disappear = True

    def update_key(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.dragging_key:
            self.key_x = max(0, min(mouse_x - self.key_width // 2, self.SCREEN_WIDTH - self.key_width))
        if self.dragging_second_key:
            self.second_key_x = max(0, min(mouse_x - self.second_key_width // 2, self.SCREEN_WIDTH - self.second_key_width))
        # Spike is fixed; no mouse following

    def update_objects(self):
        # Update heart cooldown
        self.update_heart_cooldown()
        # --- Adjustable CJ walking speed via keyboard ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_MINUS] or keys[pygame.K_UNDERSCORE]:
            self.cj_walk_speed = max(1, self.cj_walk_speed - 1)
        if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
            self.cj_walk_speed = min(30, self.cj_walk_speed + 1)

        for obj in self.objects[:]:
            # Handle shield falling inside the same loop
            if self.shield_falling:
                self.shield_y += self.shield_fall_speed
                if self.shield_y + self.shield_size >= self.floor_y:
                    self.shield_y = self.floor_y - self.shield_size
                    self.shield_falling = False
                    self.shield_hit_ground_flag = True
                    self.cj_hit_ground = False
                    print("key hits the ground")

            obj_bottom = obj[1] + self.object_size
            on_key1 = (obj_bottom >= self.key_y and obj_bottom <= self.key_y + self.key_height and
                       obj[0] + self.object_size >= self.key_x and obj[0] <= self.key_x + self.key_width - 80)
            on_key2 = (obj_bottom >= self.second_key_y and obj_bottom <= self.second_key_y + self.second_key_height and
                       obj[0] + self.object_size >= self.second_key_x and obj[0] <= self.second_key_x + self.second_key_width - 80)
            on_shield = (obj_bottom >= self.shield_y and obj_bottom <= self.shield_y + self.shield_size and
                         obj[0] + self.object_size >= self.shield_x and obj[0] <= self.shield_x + self.shield_size)

            if on_key1 or on_key2 or on_shield:
                if on_key1:
                    obj[1] = self.key_y - 20
                elif on_key2:
                    obj[1] = self.second_key_y - 20
                else:
                    obj[1] = self.shield_y - 20
            else:
                obj[1] += self.object_speed
                # When object starts to fall, make the key disappear
                self.key_disappear = True
        
            if obj[1] + self.object_size > self.floor_y:
                obj[1] = self.floor_y - self.object_size

            if obj[1] == self.floor_y - self.object_size and not (on_key1 or on_key2 or on_shield) and not self.fall_sound_played:
                self.fall_sound.play(0)
                self.fall_sound_played = True
                self.cj_hit_ground = True
                # Determine walking path based on shield and CJ ground order
                if self.shield_hit_ground_flag and self.cj_hit_ground:
                    # Shield already on ground: flip and walk to shield first
                    # flipped_cj = pygame.transform.flip(self.object_image, True, False)
                    # self.object_image = flipped_cj
                    self.cj_walking_to_shield = True
                elif self.cj_hit_ground and not self.shield_hit_ground_flag:
                    # CJ first on ground: flip and walk to diamond directly
                    flipped_cj = pygame.transform.flip(self.object_image, True, False)
                    self.object_image = flipped_cj
                    self.cj_walking_to_diamond = True
            elif obj[1] != self.floor_y - self.object_size:
                self.fall_sound_played = False

            # Handle walking to shield first
            if self.cj_walking_to_shield:
                # flipped_cj = pygame.transform.flip(self.object_image, True, False)
                # self.object_image = flipped_cj
                shield_center_x = self.shield_x + self.shield_size // 2
                if abs(obj[0] + self.object_size // 2 - shield_center_x) > 5:
                    direction = 1 if obj[0] + self.object_size // 2 < shield_center_x else -1
                    obj[0] += direction * self.cj_walk_speed
                else:
                    # Reached shield: increment shield_stat and flip to face diamond then walk to diamond
                    self.shield_stat += 1
                    flipped_cj = pygame.transform.flip(self.object_image, True, False)
                    self.object_image = flipped_cj
                    self.cj_walking_to_shield = False
                    self.shield_disappear = True
                    self.cj_walking_to_diamond = True

            # Then handle walking to diamond
            if self.cj_walking_to_diamond:
                diamond_x = self.SCREEN_WIDTH - 100
                if obj[0] < diamond_x:
                    obj[0] += self.cj_walk_speed
                    # Hide next heart when CJ walks past position_x = 610
                    if obj[0] + self.object_size // 2 >= 610:
                        self.hide_next_heart()
                else:
                    # Reached diamond: stop and trigger fade
                    self.cj_walking_to_diamond = False
                    self.fading = True
    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        # Draw each heart separately
        self.heart1.draw(self.screen)
        self.heart2.draw(self.screen)
        self.heart3.draw(self.screen)
        # Draw spike at fixed position
        self.screen.blit(self.spike_image, (self.spike_x, self.spike_y))
        # Draw shield stat below hearts
        shield_text = self.button_font.render(f"Shield: {self.shield_stat}", True, self.WHITE)
        self.screen.blit(shield_text, (10, self.heart1.y + 60))
        if not self.key_disappear:
            self.screen.blit(self.key_image, (self.key_x, self.key_y))
        if not self.second_key_disappear:
            self.screen.blit(self.second_key_image, (self.second_key_x, self.second_key_y))
        if not self.shield_disappear:
            self.screen.blit(self.shield_image, (self.shield_x, self.shield_y))
        for obj in self.objects:
            self.screen.blit(self.object_image, (obj[0], obj[1]))
        for x in range(0, 500, 100):
            self.screen.blit(self.ground_image, (x, 350))

        # Draw diamond on the right side over the invisible ground
        self.diamond_image = pygame.image.load(os.path.join("object", "diamond.png")).convert_alpha()
        self.diamond_scale = 0.07
        self.diamond_width = int(self.diamond_image.get_width() * self.diamond_scale)
        self.diamond_height = int(self.diamond_image.get_height() * self.diamond_scale)
        self.diamond_image = pygame.transform.scale(self.diamond_image, (self.diamond_width, self.diamond_height))
        diamond_x = self.SCREEN_WIDTH - 100
        self.screen.blit(self.diamond_image, (diamond_x, 400))
        
        button_color = self.BLUE if self.volume_on else self.RED
        pygame.draw.rect(self.screen, button_color, self.volume_button_rect)
        label = "ON" if self.volume_on else "OFF"
        text_surface = self.volume_font.render(label, True, self.WHITE)
        text_rect = text_surface.get_rect(center=self.volume_button_rect.center)
        self.screen.blit(text_surface, text_rect)

        if self.fading:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0, 0))
            if self.fade_alpha < 255:
                self.fade_alpha += 5
            else:
                self.level_complete = True

        if self.level_complete:
            pygame.draw.rect(self.screen, self.BLUE, self.next_level_button_rect)
            button_text = self.button_font.render("Next Level", True, self.WHITE)
            button_text_rect = button_text.get_rect(center=self.next_level_button_rect.center)
            self.screen.blit(button_text, button_text_rect)

        pygame.display.flip()
        self.clock.tick(60)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if not self.level_complete:
                self.update_key()
                self.update_objects()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
