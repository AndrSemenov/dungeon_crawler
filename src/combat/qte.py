import pygame
import random
from src.utils.rpg import Weapon
from src.combat.types import QTEConfig
from src.constants import QTE_CONFIG


class TimingBar:
    def __init__(self, screen_width: int, screen_height: int, config: QTEConfig = None):
        self.config = config or QTEConfig(**QTE_CONFIG)

        self.rect = pygame.Rect(
            (screen_width - self.config.bar_width) // 2,
            screen_height // 2 + 100,
            self.config.bar_width,
            self.config.bar_height
        )

        self.active = False
        self.cursor_x = self.rect.left
        self.direction = 1
        self.speed = self.config.base_speed

        self.green_rect = pygame.Rect(0, 0, 0, 0)
        self.yellow_left = pygame.Rect(0, 0, 0, 0)
        self.yellow_right = pygame.Rect(0, 0, 0, 0)

    def start(self, enemy_defense: int, weapon: Weapon):
        self.active = True
        self.cursor_x = self.rect.left
        self.direction = 1
        self.speed = self.config.base_speed + weapon.qte_speed_bonus
        self.weapon_crit_multiplier = weapon.crit_multiplier

        base_hit = weapon.accuracy / (weapon.accuracy + enemy_defense + 1.0)
        hit_chance = min(0.95, base_hit)
        crit_chance = weapon.crit_chance

        green_width = self.rect.width * hit_chance * crit_chance
        yellow_width = self.rect.width * (hit_chance - crit_chance)

        offset = random.uniform(-self.config.random_range, self.config.random_range) \
            if self.config.randomize_offset else self.config.green_offset_pct

        center_x = self.rect.centerx + offset * (self.rect.width * 0.4)

        self.green_rect = pygame.Rect(center_x - green_width/2, self.rect.top, green_width, self.rect.height)
        self.yellow_left = pygame.Rect(self.green_rect.left - yellow_width/2, self.rect.top, yellow_width/2, self.rect.height)
        self.yellow_right = pygame.Rect(self.green_rect.right, self.rect.top, yellow_width/2, self.rect.height)

    def update(self, dt: float):
        if not self.active:
            return

        self.cursor_x += self.direction * self.speed * dt

        if self.cursor_x <= self.rect.left:
            self.cursor_x = self.rect.left
            self.direction = 1
        elif self.cursor_x + 12 >= self.rect.right:
            self.cursor_x = self.rect.right - 12
            self.direction = -1

    def stop(self) -> tuple[str, float]:
        if not self.active:
            return "red", 0.0

        cursor_rect = pygame.Rect(self.cursor_x, self.rect.top, 12, self.rect.height)

        if cursor_rect.colliderect(self.green_rect):
            result = "green"
            multiplier = self.weapon_crit_multiplier
        elif cursor_rect.colliderect(self.yellow_left) or cursor_rect.colliderect(self.yellow_right):
            result = "yellow"
            multiplier = 1.0
        else:
            result = "red"
            multiplier = 0.0

        self.active = False
        return result, multiplier
