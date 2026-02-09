from __future__ import annotations
import pygame
from pathlib import Path
from src.level import Level
from pygame.surface import Surface

class SpriteBase:
    def __init__(self, image_path: Path):
        self.sprite = pygame.image.load(image_path)

    def draw(self, surface: pygame.Surface, x: float = 0.0, y: float = 0.0):
        surface.blit(self.sprite, dest=(x, y))

class SpriteEntity(SpriteBase):
    def __init__(self, image_path: Path):
        super().__init__(image_path)
        self.approach_progress = 0.0

    def get_dimmed_sprite(self, factor: float = 0.5):
        # TODO: должно наверное работать как шейдер поверх спрайта
        dimmed = self.sprite.copy()
        v = max(0, min(255, int(255 * factor)))  # Clamp value
        dimmed.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dimmed

    def update_state(self):
        self.scale = 0.4 + (0.75 - 0.4) * self.approach_progress
        self.brightness = 0.15 + (0.5 - 0.15) * self.approach_progress

    # def render_state(self, first_x, first_y, scale, br, map):
    #     # TODO: это по сути анимация нужно че то подумать, как с ней работать
    #     if self.approaching:
    #         self.approach_progress += 0.075  # скорость приближения

    #         if self.approach_progress >= 1:
    #             self.approach_progress = 0.0
    #             self.approaching = False
    #             self.x, self.y = first_x, first_y  # переместить врага ближе
    #             self.in_combat = True

    #         self.scale = 0.4 + (0.75 - 0.4) * self.approach_progress
    #         self.brightness = 0.15 + (0.5 - 0.15) * self.approach_progress

    #     # TODO: wtf
    #     elif scale == 0.4 and random.random() < self.attack_probability and not map.get_enemy_at(first_x, first_y):
    #         self.approaching = True
    #         self.trigger = True
    #         self.scale = scale
    #         self.brightness = br
    #     elif scale == 0.4 and self.trigger:
    #         self.approaching = True
    #         self.scale = scale
    #         self.brightness = br
    #     else:
    #         self.scale = scale
    #         self.brightness = br

    #     if self.x == first_x and self.y == first_y and self.scale == 0.4:
    #         self.scale = 0.75
    #         self.brightness = 0.5


# class Sprite:
#     def __init__(self, image_path: Path):
#         self.sprite = pygame.image.load(image_path)


#     def update_brightness(self):
#         return NotImplemented


#     def draw(self, surface: pygame.Surface, x: float, y: float):
#         surface.blit(self.sprite, (x, y))

class GameRenderer:
    def __init__(self, screen: Surface, level: Level):
        self.screen = screen
        self.level = level
        self.player = level.player
        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2
        self.visible_enemies = []

    # TODO: refactor
    def get_field_of_view_state(self):
        x, y = self.player.position
        dx, dy = self.player.direction_vectors

        self.first_x = x + dx
        self.first_y = y + dy

        self.first_turn_right = self.level.is_walkable(self.first_x - dy, self.first_y + dx)
        self.first_turn_left = self.level.is_walkable(self.first_x + dy, self.first_y - dx)

        self.second_x = x + 2 * dx
        self.second_y = y + 2 * dy

        self.second_turn_right = self.level.is_walkable(self.second_x - dy, self.second_y + dx)
        self.second_turn_left = self.level.is_walkable(self.second_x + dy, self.second_y - dx)

        self.third_x = x + 3 * dx
        self.third_y = y + 3 * dy

        self.first_cell = self.level.is_walkable(self.first_x, self.first_y)
        self.second_cell = self.level.is_walkable(self.second_x, self.second_y)
        self.third_cell = self.level.is_walkable(self.third_x, self.third_y)

        self.pr_x = x - dx
        self.pr_y = y - dy

    def draw_hallways(self):
        #три клетки впереди свободны, рисуем коридор без тупика
        if self.first_cell and self.second_cell and self.third_cell:

            #если есть оба вторых поворота
            if self.second_turn_right and self.second_turn_left:
                self.level.sprites['hallway']['hallway_second_turn_both'].draw(self.screen)

            #если второй поворот направо
            elif self.second_turn_right:
                #если первый поворот налево
                if self.first_turn_left:
                    self.level.sprites['hallway']['hallway_second_turn_right_and_first_turn_left'].draw(self.screen)
                else:
                    self.level.sprites['hallway']['hallway_second_turn_right'].draw(self.screen)

            #если второй поворот налево
            elif self.second_turn_left:
                #если первый поворот направо
                if self.first_turn_right:
                    self.level.sprites['hallway']['hallway_second_turn_left_and_first_turn_right'].draw(self.screen)
                else:
                    self.level.sprites['hallway']['hallway_second_turn_left'].draw(self.screen)

            #оба первых поворота
            elif self.first_turn_right and self.first_turn_left:
                self.level.sprites['hallway']['hallway_first_turn_both'].draw(self.screen)

            #первый поворот направо
            elif self.first_turn_right:
                self.level.sprites['hallway']['hallway_first_turn_right'].draw(self.screen)

            #первый поворот налево
            elif self.first_turn_left:
                self.level.sprites['hallway']['hallway_first_turn_left'].draw(self.screen)

            #без поворотов
            else:
                 self.level.sprites['hallway']['hallway'].draw(self.screen)

        elif self.first_cell and self.second_cell:
            #если есть оба вторых поворота
            if self.second_turn_right and self.second_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_second_turn_both'].draw(self.screen)
            #если второй поворот направо
            elif self.second_turn_right:
                #если первый поворот налево
                if self.first_turn_left:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_right_and_first_turn_left'].draw(self.screen)
                else:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_right'].draw(self.screen)
            #если второй поворот налево
            elif self.second_turn_left:
                #если первый поворот направо
                if self.first_turn_right:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_left_and_first_turn_right'].draw(self.screen)
                else:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_left'].draw(self.screen)
            #оба первых поворота
            elif self.first_turn_right and self.first_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_both'].draw(self.screen)
            #первый поворот направо
            elif self.first_turn_right:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_right'].draw(self.screen)
            #первый поворот налево
            elif self.first_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_left'].draw(self.screen)
            #без поворотов
            else:
                 self.level.sprites['hallway_2block']['hallway_2block'].draw(self.screen)
        elif self.first_cell:
            #оба первых поворота
            if self.first_turn_right and self.first_turn_left:
                self.level.sprites['hallway_1block']['hallway_1block_turn_both'].draw(self.screen)
            #первый поворот направо
            elif self.first_turn_right:
                self.level.sprites['hallway_1block']['hallway_1block_turn_right'].draw(self.screen)
            #первый поворот налево
            elif self.first_turn_left:
                self.level.sprites['hallway_1block']['hallway_1block_turn_left'].draw(self.screen)
            #без поворотов
            else:
                 self.level.sprites['hallway_1block']['hallway_1block'].draw(self.screen)
        else:
            self.level.sprites["wall_front"]["wall_front"].draw(self.screen)

    def draw_entities(self):
        # TODO: refactor
        for _, (fx, fy, scale, br) in enumerate([

            (self.second_x, self.second_y, 0.4, 0.15),
            (self.first_x, self.first_y, 0.75, 0.5)
        ]):
            entity = self.level.get_entity_at(fx, fy)

            if entity is None:
                continue
            elif entity.charging:
                entity.sprite.approach_progress += 0.075
                entity.sprite.scale = 0.4 + (0.75 - 0.4) * entity.sprite.approach_progress
                entity.sprite.brightness = 0.15 + (0.5 - 0.15) * entity.sprite.approach_progress
            else:
                entity.sprite.scale = scale
                entity.sprite.brightness = br

            interp_scale, interp_brightness = entity.sprite.scale, entity.sprite.brightness
            original = entity.sprite.get_dimmed_sprite(factor = interp_brightness)
            new_size = (int(original.get_width() * interp_scale), int(original.get_height() * interp_scale))
            scaled = pygame.transform.scale(original, new_size)
            self.screen.blit(scaled, (self.center_x - new_size[0] // 2, self.center_y - new_size[1] // 2))

    def render(self):
        self.get_field_of_view_state()
        self.draw_hallways()
        self.draw_entities()


