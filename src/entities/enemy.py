import pygame
import random
import src.engine.map as map

class Enemy:
    def __init__(self, x, y, HP, damage, attack_probability = 0.01):
        self.x = x
        self.y = y
        self.HP = HP
        self.damage = damage
        self.__class__.load_sprite()
        self.attack_probability = attack_probability

        self.approaching = False
        self.trigger = False
        self.approach_progress = 0.0  # от 0.0 до 1.0
        self.in_combat = False

        self.advantage = 1

    @classmethod
    def load_sprite(cls):
        cls.sprite = pygame.image.load(f"assets/enemies/{cls.__name__}.png")

    def get_dimmed_sprite(self, factor=0.5):
        """
        Возвращает копию спрайта с пониженной яркостью.
        factor: 1.0 — оригинал, 0.5 — затемнение на 50%
        """
        if self.sprite is None:
            raise ValueError("Sprite not loaded. Call Enemy.load_sprite() first.")

        dimmed = self.sprite.copy()
        v = max(0, min(255, int(255 * factor)))  # Clamp value
        dimmed.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def render_state(self, first_x, first_y, scale, br, map):
        if self.approaching:
            self.approach_progress += 0.075  # скорость приближения

            if self.approach_progress >= 1:
                self.approach_progress = 0.0
                self.approaching = False
                self.x, self.y = first_x, first_y  # переместить врага ближе
                self.in_combat = True
            self.scale = 0.4 + (0.75 - 0.4) * self.approach_progress
            self.brightness = 0.15 + (0.5 - 0.15) * self.approach_progress

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






class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, HP=5, damage=1)




