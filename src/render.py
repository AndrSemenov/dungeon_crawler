from __future__ import annotations
import pygame
from pathlib import Path
from src.level import Level
# from src.entities import Enemy
from src.constants import logger
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

class GameRenderer:
    def __init__(self, screen: Surface, level: Level):
        self.screen = screen
        self.level = level
        self.player = level.player
        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2
        self.visible_enemies = []

        # Параметры миникарты
        self.minimap_size = 120
        self.minimap_padding = 10
        self.minimap_rect = pygame.Rect(
            self.screen.get_width() - self.minimap_size - self.minimap_padding,
            self.minimap_padding,
            self.minimap_size,
            self.minimap_size
        )

        # Цвета для миникарты
        self.color_wall   = (40, 40, 60)
        self.color_floor  = (100, 100, 120)
        self.color_player = (220, 80, 80)
        self.color_enemy  = (180, 140, 60)

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
        for depth, (fx, fy, base_scale, base_br) in enumerate([

            (self.second_x, self.second_y, 0.4, 0.15),
            (self.first_x, self.first_y, 0.75, 0.5)
        ]):
            entity = self.level.get_entity_at(fx, fy)
            if not entity:
                continue



            # if isinstance(entity, Enemy) and entity.approach and entity.approach.active:
            #     scale = entity.approach.current_scale
            #     brightness = entity.approach.current_brightness
            # else:
            #     scale = base_scale
            #     brightness = base_br

            scale = base_scale
            brightness = base_br

            original = entity.sprite.get_dimmed_sprite(factor=brightness)
            new_size = (int(original.get_width() * scale), int(original.get_height() * scale))
            scaled = pygame.transform.scale(original, new_size)
            self.screen.blit(scaled, (self.center_x - new_size[0]//2, self.center_y - new_size[1]//2))

    def draw_minimap(self):
        # Создаём временную поверхность
        minimap = pygame.Surface((self.minimap_size, self.minimap_size))
        minimap.fill((20, 20, 30))  # тёмный фон

        map_h = len(self.level.map)
        map_w = max(len(row) for row in self.level.map) if map_h > 0 else 1

        cell_size = max(1, self.minimap_size // max(map_w, map_h))

        px, py = self.player.position

        for y in range(map_h):
            for x in range(len(self.level.map[y])):
                if self.level.map[y][x] == 0:
                    color = self.color_wall
                else:
                    color = self.color_floor

                # Затемнение неисследованных клеток (если захочешь)
                # if not self.level.explored[y][x]:
                #     color = tuple(c // 3 for c in color)

                rect = pygame.Rect(
                    x * cell_size,
                    y * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(minimap, color, rect)

        # Игрок
        pygame.draw.circle(
            minimap,
            self.color_player,
            (px * cell_size + cell_size // 2, py * cell_size + cell_size // 2),
            max(3, cell_size // 2)
        )

        # Враги
        for enemy in self.level.enemies:
            ex, ey = enemy.position
            pygame.draw.circle(
                minimap,
                self.color_enemy,
                (ex * cell_size + cell_size // 2, ey * cell_size + cell_size // 2),
                max(2, cell_size // 3)
            )

        # Рисуем миникарту на экран
        self.screen.blit(minimap, self.minimap_rect.topleft)

    def render(self):
        self.get_field_of_view_state()
        # logger.debug(f"Player pos: {self.player.position}, dir: {self.player.direction_vectors}")
        # logger.debug(f"FOV: first({self.first_x},{self.first_y}), second({self.second_x},{self.second_y}), third({self.third_x},{self.third_y})")
        self.draw_hallways()
        self.draw_entities()

        # Миникарта в правом верхнем углу
        self.draw_minimap()


