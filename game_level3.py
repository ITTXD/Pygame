import pygame
import sys
import os
from pygame.cursors import diamond

class GameLevel3:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Level 3: Background + Platform Only")

        # Background
        self.background_image = pygame.image.load(os.path.join("background", "hell.png")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Sword
        self.sword_image = pygame.image.load(os.path.join("object", "sword1.png")).convert_alpha()
        self.sword_image = pygame.transform.scale(self.sword_image, (50, 50))
        self.sword_visible = True
        self.sword_on_head = False
        self.sword_x = 700
        self.sword_y = 450

        # Platform image (ground1)
        self.ground_image = pygame.image.load(os.path.join("object", "ground1.png")).convert_alpha()

        # Invisible collision lines
        self.diamond_line_x_start = 447
        self.diamond_line_x_end = 552
        self.diamond_line_y = 124
        self.ground_line_y = 512
        self.ground_left = 0
        self.ground_right = 500

        # First key (vertical, draggable only vertically)
        self.first_key = pygame.image.load(os.path.join("object", "keyu.png")).convert_alpha()
        self.first_key = pygame.transform.scale(self.first_key, (200, 150))
        self.first_key = pygame.transform.rotate(self.first_key, -90)
        self.first_key = pygame.transform.flip(self.first_key, True, False)
        self.key_rect = self.first_key.get_rect()
        self.key_rect.topleft = (120, 350)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.key_visible = True

        # Second key (horizontal, draggable only horizontally)
        self.second_key = pygame.image.load(os.path.join("object", "keyu.png")).convert_alpha()
        self.second_key = pygame.transform.scale(self.second_key, (200, 150))
        self.second_key = pygame.transform.rotate(self.second_key, 0)
        self.second_key_rect = self.second_key.get_rect()
        self.second_key_rect.topleft = (300, 215)
        self.second_dragging = False
        self.second_drag_offset = (0, 0)
        self.second_key_visible = True

        # Portal (starts above the second key, then can fall)
        self.portal_image = pygame.image.load(os.path.join("object", "portal.png")).convert_alpha()
        self.portal_image = pygame.transform.scale(self.portal_image, (60, 80))
        self.portal_rect = self.portal_image.get_rect()
        self.portal_rect.midbottom = (self.second_key_rect.centerx, self.second_key_rect.top)
        self.portal_falling = False
        self.portal_fall_speed = 3

        # Character (CJ)
        self.character_image = pygame.image.load(os.path.join("object", "cj-2.png")).convert_alpha()
        self.character_image = pygame.transform.scale(self.character_image, (100, 100))
        self.character_image = pygame.transform.flip(self.character_image, True, False)  # ตอนนี้หันซ้าย
        self.character_rect = self.character_image.get_rect()
        self.character_rect.midbottom = (58, self.ground_line_y)
        self.character_speed = 3
        self.character_facing_right = False  # ให้ตรงกับ sprite ที่ตอนนี้หันซ้าย

        # Diamond ground/platform and diamond
        scale = 2
        self.diamond_ground = pygame.image.load(os.path.join("object", "ground1.png")).convert_alpha()
        self.diamond_ground = pygame.transform.scale(self.diamond_ground, (100 * scale, 100 * scale))
        self.diamond_line_x_start = 551
        self.diamond_line_x_end = 749
        self.diamond_line_y = 192

        self.diamond_ground_pos = (600, 150)
        self.diamond_image = pygame.image.load(os.path.join("object", "Diamond.png")).convert_alpha()
        self.diamond_image = pygame.transform.scale(self.diamond_image, (50, 50))
        self.diamond_pos = (730, 165)
        self.diamond_captured = False

        # Continuous run state (after CJ picks up the sword)
        self.run_to_portal = False
        self.get_portal = False  # stop running once portal is reached
        self.portal_on_ground = False  # track if portal is on ground

        # Clock
        self.clock = pygame.time.Clock()

    def draw(self):
        # Background
        self.screen.blit(self.background_image, (0, 0))

        # Sword
        if self.sword_visible and not self.sword_on_head:
            self.screen.blit(self.sword_image, (self.sword_x, self.sword_y))

        # Ground tiles
        for x in range(0, 500, 100):
            self.screen.blit(self.ground_image, (x, 380))

        # Diamond ground (twice, matching your previous layout)
        self.screen.blit(self.diamond_ground, self.diamond_ground_pos)
        self.screen.blit(self.diamond_ground, self.diamond_ground_pos)

        # Diamond
        self.screen.blit(self.diamond_image, self.diamond_pos)

        # Character
        self.screen.blit(self.character_image, self.character_rect)

        # Sword on CJ's head if captured
        if self.sword_on_head:
            sword_head_x = self.character_rect.centerx - self.sword_image.get_width() // 2
            sword_head_y = self.character_rect.top - self.sword_image.get_height() // 2
            self.screen.blit(self.sword_image, (sword_head_x, sword_head_y))

        # First key
        if self.key_visible and self.key_rect.y >= 192:
            self.screen.blit(self.first_key, self.key_rect)

        # Second key
        if self.second_key_visible:
            self.screen.blit(self.second_key, self.second_key_rect)

        # Portal
        self.screen.blit(self.portal_image, self.portal_rect)

        # Hide the debug diamond line by covering it
        cover_rect = pygame.Rect(
            self.diamond_line_x_start,
            self.diamond_line_y - 1,
            self.diamond_line_x_end - self.diamond_line_x_start,
            2,
        )
        self.screen.blit(self.background_image, cover_rect, cover_rect)

        pygame.display.flip()
        self.clock.tick(60)

    def update(self):
        # 1) Move CJ toward the sword until he picks it up (per-frame)
        sword_x = self.sword_x

    
        if not self.key_visible and not self.sword_on_head:
            if self.character_rect.centerx < sword_x:
                self.character_rect.x += self.character_speed
            elif self.character_rect.centerx > sword_x:
                self.character_rect.x -= self.character_speed
        

            if abs(self.character_rect.centerx - sword_x) < self.character_speed:
                self.sword_visible = False
                self.sword_on_head = True

        # 2) Portal falls if not perfectly above the second key top
        if (
            self.portal_rect.centerx != self.second_key_rect.centerx
            or self.portal_rect.bottom != self.second_key_rect.top
        ):
            self.portal_falling = True

        if self.portal_falling:
            self.portal_rect.y += self.portal_fall_speed
            # Land on the second key
            if (
                self.portal_rect.centerx == self.second_key_rect.centerx
                and self.portal_rect.bottom >= self.second_key_rect.top
            ):
                self.portal_rect.bottom = self.second_key_rect.top
                self.portal_falling = False
            # Or stop at ground line
            if self.portal_rect.bottom >= self.ground_line_y:
                self.portal_rect.bottom = self.ground_line_y
                self.portal_falling = False
                self.portal_on_ground = True

        # 3) After picking the sword, continuously run toward the portal
        if self.sword_on_head and not self.get_portal:  # only run while get_portal is False
            # Start the run once
            if not self.run_to_portal:
                # Face toward portal horizontally once at start
                if self.character_rect.centerx > self.portal_rect.centerx and self.character_facing_right:
                    self.character_image = pygame.transform.flip(self.character_image, True, False)
                    self.character_facing_right = False
                elif self.character_rect.centerx < self.portal_rect.centerx and not self.character_facing_right:
                    self.character_image = pygame.transform.flip(self.character_image, True, False)
                    self.character_facing_right = True
                self.run_to_portal = True

            # Continue moving every frame until reaching portal's center x
            target_x = self.portal_rect.centerx
            if abs(self.character_rect.centerx - target_x) > self.character_speed:
                if self.character_rect.centerx < target_x:
                    print("run")
                    self.character_rect.x += self.character_speed
                    # เดินขวา → หันขวา
                    if not self.character_facing_right:
                        self.character_image = pygame.transform.flip(self.character_image, True, False)
                        self.character_facing_right = True
                else:
                    print("run")
                    self.character_rect.x -= self.character_speed
                    print(self.character_rect.x)
                    # เดินซ้าย → หันซ้าย
                    if self.character_facing_right:
                        self.character_image = pygame.transform.flip(self.character_image, True, False)
                        self.character_facing_right = False
            else:
                # Snap when close enough and mark portal as reached
                self.character_rect.centerx = target_x
                self.get_portal = True  # stop further running

                # If portal is on ground, move it and make it disappear
                if self.portal_on_ground:
                    self.portal_rect.y = -100  # Move off-screen
                    self.portal_on_ground = False  # Reset flag

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.key_visible and self.key_rect.collidepoint(event.pos):
                            self.dragging = True
                            self.drag_offset = (event.pos[0] - self.key_rect.x, event.pos[1] - self.key_rect.y)
                        if self.second_key_visible and self.second_key_rect.collidepoint(event.pos):
                            self.second_dragging = True
                            self.second_drag_offset = (event.pos[0] - self.second_key_rect.x, event.pos[1] - self.second_key_rect.y)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                        if self.key_rect.y < self.diamond_line_y:
                            self.key_visible = False
                        self.second_dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    # First key: vertical drag only
                    if self.dragging and self.key_visible:
                        new_y = event.pos[1] - self.drag_offset[1]
                        if new_y + self.key_rect.height > self.ground_line_y:
                            new_y = self.ground_line_y - self.key_rect.height
                        self.key_rect.y = new_y

                    # Second key: horizontal drag only
                    if self.second_dragging and self.second_key_visible:
                        new_x = event.pos[0] - self.second_drag_offset[0]
                        if new_x < 0:
                            new_x = 0
                        self.second_key_rect.x = new_x

            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    GameLevel3().run()
