import pygame
import sys
import os
import subprocess
class Background:
    def __init__(self, path, size):
        self.image = pygame.image.load(path).convert()
        self.image = pygame.transform.scale(self.image, size)


class MusicPlayer:
    def __init__(self, music_path, volume=0.1, loops=-1):
        self.music_path = music_path
        self.volume = volume
        self.loops = loops
        self.load_and_play()

    def load_and_play(self):
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(self.loops)


class VictorySound:
    def __init__(self):
        self.sound = pygame.mixer.Sound(os.path.join("music", "Victorysound.mp3"))
        self.sound.set_volume(1.0)
        self.played = False


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)


class Heart:
    def __init__(self, x, y, scale=0.07):
        self.image = pygame.image.load(os.path.join("object", "pixelheart.png")).convert_alpha()
        self.width = int(self.image.get_width() * scale)
        self.height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = x
        self.y = y


class Key:
    def __init__(self, image_path, width, height, x, y, rotate=0):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (width, height))
        # Initialize width/height before any rotation
        self.width, self.height = width, height
        if rotate != 0:
            self.image = pygame.transform.rotate(self.image, rotate)
            # After 90/270-degree rotation, width and height swap
            self.width, self.height = self.height, self.width
        self.x = x
        self.y = y
        self.visible = True
        self.disappeared = False
        self.dragging = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Diamond:
    def __init__(self, image_path, x, y, scale=0.07):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.width = int(self.original_image.get_width() * scale)
        self.height = int(self.original_image.get_height() * scale)
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        self.x = x
        self.y = y


class FallingObject:
    def __init__(self, image_path, size, x, y):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.size = size
        self.x = x
        self.y = y


class VolumeButton:
    def __init__(self, x, y, width, height, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.on = True
        self.font = pygame.font.SysFont(None, font_size)

    def toggle(self):
        self.on = not self.on
        vol = 0.1 if self.on else 0.0
        pygame.mixer.music.set_volume(vol)
        return self.on


class FadeTransition:
    def __init__(self, width, height):
        self.alpha = 0
        self.fading = False
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))
        self.complete = False

    def update(self):
        if self.fading and self.alpha < 255:
            self.alpha += 5
            if self.alpha >= 255:
                self.complete = True
        self.surface.set_alpha(self.alpha)

    def start(self):
        self.fading = True


class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("เกมลากกุญแจด่านที่ 1")

        self.background = Background(os.path.join("object", "SKY3.png"), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.music_player = MusicPlayer(os.path.join("music", "music.mp3"))
        self.fall_sound = pygame.mixer.Sound(os.path.join("sound effect", "falldown.mp3"))
        self.fall_sound.set_volume(1.0)
        self.fall_sound_played = False
        self.victory_sound_obj = VictorySound()
        self.fade = FadeTransition(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.colors = Colors()
        self.clock = pygame.time.Clock()

        self.object_size = 100
        self.object_speed = 3
        self.objects = []

        self.heart1 = Heart(10, 50)
        self.heart2 = Heart(self.heart1.x + self.heart1.width, 50)
        self.heart3 = Heart(self.heart2.x + self.heart2.width, 50)

        self.key1 = Key(os.path.join("object", "keyu.png"), 250, 200, self.SCREEN_WIDTH - 290, self.SCREEN_HEIGHT - 500)
        self.key2 = Key(os.path.join("object", "keyu.png"), 250, 200,
                        self.SCREEN_WIDTH // 2 - 125, self.SCREEN_HEIGHT // 2 - 50, rotate=270)
        self.diamond = Diamond(os.path.join("object", "Diamond.png"), 80, 499)

        self.floor_y = self.SCREEN_HEIGHT - 110
        self.ground_image = pygame.image.load(os.path.join("object", "ground1.png")).convert_alpha()
        self.object_image_path = os.path.join("object", "cj-2.png")

        self.volume_button = VolumeButton(self.SCREEN_WIDTH - 100, 20, 80, 40)
        self.next_level_button_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 80, self.SCREEN_HEIGHT // 2 - 25, 160, 50)
        self.button_font = pygame.font.SysFont(None, 36)

        self.victory_played = False
        self.level_complete = False

        self.objects.append(FallingObject(self.object_image_path, self.object_size,
                                          self.key1.x + self.key1.width // 2 - self.object_size // 2,
                                          self.key1.y - 20))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i and pygame.key.get_mods() & pygame.KMOD_META:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.volume_button.rect.collidepoint(event.pos):
                    self.volume_button.toggle()
                    self.fall_sound.set_volume(1.0 if self.volume_button.on else 0.0)
                    self.victory_sound_obj.sound.set_volume(1.0 if self.volume_button.on else 0.0)
                elif not self.key1.disappeared and self.key1.visible and self.key1.rect().collidepoint(event.pos):
                    self.key1.dragging = True
                elif not self.key2.disappeared and self.key2.visible and self.key2.rect().collidepoint(event.pos):
                    self.key2.dragging = True
                elif self.level_complete and self.next_level_button_rect.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, "game_level2.py"])
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.key1.dragging = False
                self.key2.dragging = False
        return True

    def update_key(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.key1.dragging and not self.key1.disappeared:
            self.key1.x = mouse_x - self.key1.width // 2
            self.key1.x = max(0, min(self.key1.x, self.SCREEN_WIDTH - self.key1.width))
        if self.key1.x < 400:
            self.key1.visible = False
            self.key1.disappeared = True

        if self.key2.dragging and not self.key2.disappeared:
            if mouse_y < self.key2.y + self.key2.height // 2:
                self.key2.y = mouse_y - self.key2.height // 2
                self.key2.y = max(0, self.key2.y)
        if self.key2.y < 100:
            self.key2.visible = False
            self.key2.disappeared = True

    def update_objects(self):
        for obj in self.objects:
            obj_bottom = obj.y + obj.size
            on_key1 = (self.key1.visible and
                       obj_bottom >= self.key1.y and obj_bottom <= self.key1.y + self.key1.height and
                       obj.x + obj.size >= self.key1.x and obj.x <= self.key1.x + self.key1.width - 80)
            on_key2 = (self.key2.visible and
                       obj_bottom >= self.key2.y and obj_bottom <= self.key2.y + self.key2.height and
                       obj.x + obj.size >= self.key2.x and obj.x <= self.key2.x + self.key2.width - 80)
            if on_key1:
                obj.y = self.key1.y - 20
            elif on_key2:
                obj.y = self.key2.y - 8
            else:
                obj.y += self.object_speed

            if obj.y + obj.size > self.floor_y:
                obj.y = self.floor_y - obj.size

            if obj.y == self.floor_y - obj.size and not (on_key1 or on_key2) and not self.fall_sound_played:
                self.fall_sound.play(0)
                self.fall_sound_played = True
            elif obj.y != self.floor_y - obj.size:
                self.fall_sound_played = False

            if obj.y == self.floor_y - obj.size:
                if not self.key2.disappeared:
                    if obj.x > 510:
                        obj.x -= 2
                    if obj.x <= 510:
                        obj.x = 510
                else:
                    if obj.x > self.diamond.x:
                        obj.x -= 2
                    if obj.x <= self.diamond.x:
                        obj.x = self.diamond.x
                        if not self.victory_played:
                            self.victory_sound_obj.sound.play(0)
                            self.victory_played = True
                            pygame.mixer.music.stop()
                            self.fade.start()

    def draw(self):
        self.screen.blit(self.background.image, (0, 0))
        self.screen.blit(self.diamond.image, (30, 400))
        self.screen.blit(self.heart1.image, (self.heart1.x, self.heart1.y))
        self.screen.blit(self.heart2.image, (self.heart2.x, self.heart2.y))
        self.screen.blit(self.heart3.image, (self.heart3.x, self.heart3.y))
        if self.key1.visible:
            self.screen.blit(self.key1.image, (self.key1.x, self.key1.y))
        if self.key2.visible:
            self.screen.blit(self.key2.image, (self.key2.x, self.key2.y))
        for obj in self.objects:
            self.screen.blit(obj.image, (obj.x, obj.y))
        for gx in [0, 100, 200, 300, 400]:
            self.screen.blit(self.ground_image, (gx, 350))

        button_color = self.colors.BLUE if self.volume_button.on else self.colors.RED
        pygame.draw.rect(self.screen, button_color, self.volume_button.rect)
        label = "ON" if self.volume_button.on else "OFF"
        text_surface = self.volume_button.font.render(label, True, self.colors.WHITE)
        text_rect = text_surface.get_rect(center=self.volume_button.rect.center)
        self.screen.blit(text_surface, text_rect)

        if self.fade.fading:
            self.fade.update()
            self.screen.blit(self.fade.surface, (0, 0))
            if self.fade.complete:
                self.level_complete = True

        if self.level_complete:
            pygame.draw.rect(self.screen, self.colors.BLUE, self.next_level_button_rect)
            button_text = self.button_font.render("Next Level", True, self.colors.WHITE)
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
    game = Game()
    game.run()