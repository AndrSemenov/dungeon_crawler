import pygame
from pathlib import Path
from src.game import logger

class Sprite:
    def __init__(self, image_path: Path):
        self.sprite = pygame.image.load(image_path)

    def get_dimmed_sprite(self, factor: float = 0.5):
        # TODO: должно наверное работать как шейдер поверх спрайта
        dimmed = self.sprite.copy()
        v = max(0, min(255, int(255 * factor)))  # Clamp value
        dimmed.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def render_state(self, first_x, first_y, scale, br, map):
        # TODO: это по сути анимация нужно че то подумать, как с ней работать
        if self.approaching:
            self.approach_progress += 0.075  # скорость приближения

            if self.approach_progress >= 1:
                self.approach_progress = 0.0
                self.approaching = False
                self.x, self.y = first_x, first_y  # переместить врага ближе
                self.in_combat = True
            self.scale = 0.4 + (0.75 - 0.4) * self.approach_progress
            self.brightness = 0.15 + (0.5 - 0.15) * self.approach_progress

        # TODO: wtf
        elif scale == 0.4 and random.random() < self.attack_probability and not map.get_enemy_at(first_x, first_y):
            self.approaching = True
            self.trigger = True
            self.scale = scale
            self.brightness = br

        elif scale == 0.4 and self.trigger:
            self.approaching = True
            self.scale = scale
            self.brightness = br


        else:
            self.scale = scale
            self.brightness = br

        if self.x == first_x and self.y == first_y and self.scale == 0.4:
            self.scale = 0.75
            self.brightness = 0.5

    def draw(self, surface: pygame.Surface, x: float, y: float):
        surface.blit(self.sprite, (x, y))

class