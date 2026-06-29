from __future__ import annotations
import pygame
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

from src.level import Level
from src.constants import logger
from pygame.surface import Surface

if TYPE_CHECKING:
    from src.entities import Enemy, Entity
    from src.combat.qte import TimingBar
    from src.animation import Animator


@dataclass
class FOVState:
    first_cell: bool
    second_cell: bool
    third_cell: bool
    first_turn_right: bool
    first_turn_left: bool
    second_turn_right: bool
    second_turn_left: bool


class SpriteBase:
    def __init__(self, image_path: Path):
        self.sprite = pygame.image.load(image_path)

    def draw(self, surface: pygame.Surface, x: float = 0.0, y: float = 0.0):
        surface.blit(self.sprite, dest=(x, y))


class SpriteEntity(SpriteBase):
    def __init__(self, image_path: Path):
        super().__init__(image_path)
        self.approach_progress = 0.0
        self.animator: Optional['Animator'] = None

    def get_current_surface(self) -> pygame.Surface:
        if self.animator and self.animator.active and self.animator.current_frame is not None:
            return self.animator.current_frame
        return self.sprite

    def get_dimmed_sprite(self, factor: float = 0.5):
        # TODO: должно наверное работать как шейдер поверх спрайта
        dimmed = self.get_current_surface().copy()
        v = max(0, min(255, int(255 * factor)))
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

        self.minimap_size = 270
        self.minimap_padding = 2
        self.minimap_rect = pygame.Rect(
            self.minimap_padding,
            self.minimap_padding,
            self.minimap_size,
            self.minimap_size
        )

        self.color_wall   = (40, 40, 60)
        self.color_floor  = (100, 100, 120)
        self.color_player = (220, 80, 80)
        self.color_enemy  = (180, 140, 60)

        self._damage_flash: float = 0.0   # remaining seconds of red flash
        self._flash_duration: float = 0.4

    def get_field_of_view_state(self) -> FOVState:
        x, y = self.player.position
        dx, dy = self.player.direction_vectors

        first_x  = x + dx;       first_y  = y + dy
        second_x = x + 2 * dx;   second_y = y + 2 * dy
        third_x  = x + 3 * dx;   third_y  = y + 3 * dy

        return FOVState(
            first_cell=self.level.is_walkable(first_x, first_y),
            second_cell=self.level.is_walkable(second_x, second_y),
            third_cell=self.level.is_walkable(third_x, third_y),
            first_turn_right=self.level.is_walkable(first_x - dy, first_y + dx),
            first_turn_left=self.level.is_walkable(first_x + dy, first_y - dx),
            second_turn_right=self.level.is_walkable(second_x - dy, second_y + dx),
            second_turn_left=self.level.is_walkable(second_x + dy, second_y - dx),
        )

    def draw_hallways(self, fov: FOVState):
        if fov.first_cell and fov.second_cell and fov.third_cell:

            if fov.second_turn_right and fov.second_turn_left:
                self.level.sprites['hallway']['hallway_second_turn_both'].draw(self.screen)
            elif fov.second_turn_right:
                if fov.first_turn_left:
                    self.level.sprites['hallway']['hallway_second_turn_right_and_first_turn_left'].draw(self.screen)
                else:
                    self.level.sprites['hallway']['hallway_second_turn_right'].draw(self.screen)
            elif fov.second_turn_left:
                if fov.first_turn_right:
                    self.level.sprites['hallway']['hallway_second_turn_left_and_first_turn_right'].draw(self.screen)
                else:
                    self.level.sprites['hallway']['hallway_second_turn_left'].draw(self.screen)
            elif fov.first_turn_right and fov.first_turn_left:
                self.level.sprites['hallway']['hallway_first_turn_both'].draw(self.screen)
            elif fov.first_turn_right:
                self.level.sprites['hallway']['hallway_first_turn_right'].draw(self.screen)
            elif fov.first_turn_left:
                self.level.sprites['hallway']['hallway_first_turn_left'].draw(self.screen)
            else:
                self.level.sprites['hallway']['hallway'].draw(self.screen)

        elif fov.first_cell and fov.second_cell:

            if fov.second_turn_right and fov.second_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_second_turn_both'].draw(self.screen)
            elif fov.second_turn_right:
                if fov.first_turn_left:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_right_and_first_turn_left'].draw(self.screen)
                else:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_right'].draw(self.screen)
            elif fov.second_turn_left:
                if fov.first_turn_right:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_left_and_first_turn_right'].draw(self.screen)
                else:
                    self.level.sprites['hallway_2block']['hallway_2block_second_turn_left'].draw(self.screen)
            elif fov.first_turn_right and fov.first_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_both'].draw(self.screen)
            elif fov.first_turn_right:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_right'].draw(self.screen)
            elif fov.first_turn_left:
                self.level.sprites['hallway_2block']['hallway_2block_first_turn_left'].draw(self.screen)
            else:
                self.level.sprites['hallway_2block']['hallway_2block'].draw(self.screen)

        elif fov.first_cell:

            if fov.first_turn_right and fov.first_turn_left:
                self.level.sprites['hallway_1block']['hallway_1block_turn_both'].draw(self.screen)
            elif fov.first_turn_right:
                self.level.sprites['hallway_1block']['hallway_1block_turn_right'].draw(self.screen)
            elif fov.first_turn_left:
                self.level.sprites['hallway_1block']['hallway_1block_turn_left'].draw(self.screen)
            else:
                self.level.sprites['hallway_1block']['hallway_1block'].draw(self.screen)

        else:
            self.level.sprites["wall_front"]["wall_front"].draw(self.screen)

    def draw_entities(self):
        for entity, depth in self.get_visible_entities():
            params = entity.get_render_params(depth)

            original = entity.sprite.get_dimmed_sprite(factor=params["brightness"])
            new_size = (int(original.get_width() * params["scale"]),
                        int(original.get_height() * params["scale"]))
            scaled = pygame.transform.scale(original, new_size)

            draw_x = self.center_x - new_size[0] // 2
            draw_y = self.center_y - new_size[1] // 2

            self.screen.blit(scaled, (draw_x, draw_y))

    def draw_minimap(self):
        minimap = pygame.Surface((self.minimap_size, self.minimap_size))
        minimap.fill((20, 20, 30))

        map_h = len(self.level.map)
        map_w = max(len(row) for row in self.level.map) if map_h > 0 else 1

        scale_x = self.minimap_size / map_w
        scale_y = self.minimap_size / map_h
        cell_size = max(1, int(min(scale_x, scale_y)))

        offset_x = (self.minimap_size - map_w * cell_size) // 2
        offset_y = (self.minimap_size - map_h * cell_size) // 2

        px, py = self.player.position

        for y in range(map_h):
            for x in range(len(self.level.map[y])):
                color = self.color_wall if self.level.map[y][x] == 0 else self.color_floor
                pygame.draw.rect(minimap, color, pygame.Rect(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    cell_size, cell_size
                ))

        pygame.draw.circle(
            minimap, self.color_player,
            (px * cell_size + offset_x + cell_size // 2, py * cell_size + offset_y + cell_size // 2),
            max(3, cell_size // 2)
        )

        for enemy in self.level.enemies:
            ex, ey = enemy.position
            pygame.draw.circle(
                minimap, self.color_enemy,
                (ex * cell_size + offset_x + cell_size // 2, ey * cell_size + offset_y + cell_size // 2),
                max(2, cell_size // 3)
            )

        self.screen.blit(minimap, self.minimap_rect.topleft)

    def draw_weapon(self):
        weapon = self.player.inventory.current_weapon
        if not weapon.animator or not weapon.animator.active:
            return
        frame = weapon.animator.current_frame
        if frame is None:
            return
        scaled = pygame.transform.scale(frame, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))

    def trigger_damage_flash(self):
        self._damage_flash = self._flash_duration

    def _draw_damage_flash(self, dt: float):
        if self._damage_flash <= 0:
            return
        self._damage_flash = max(0.0, self._damage_flash - dt)
        alpha = int(180 * (self._damage_flash / self._flash_duration))
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((200, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    def draw_qte(self, timing_bar: 'TimingBar'):
        pygame.draw.rect(self.screen, (80, 20, 20), timing_bar.rect)
        pygame.draw.rect(self.screen, (255, 200, 0), timing_bar.yellow_left)
        pygame.draw.rect(self.screen, (255, 200, 0), timing_bar.yellow_right)
        pygame.draw.rect(self.screen, (0, 255, 100), timing_bar.green_rect)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (timing_bar.cursor_x, timing_bar.rect.top - 8, 12, timing_bar.rect.height + 16),
                         border_radius=4)

    def render(self, qte: Optional['TimingBar'] = None, dt: float = 0.0):
        fov = self.get_field_of_view_state()
        self.draw_hallways(fov)
        self.draw_entities()
        self.draw_weapon()
        self.draw_minimap()
        if qte and qte.active:
            self.draw_qte(qte)
        self._draw_damage_flash(dt)

    def get_visible_entities(self) -> List[Tuple['Entity', int]]:
        px, py = self.player.position
        dx, dy = self.player.direction_vectors
        visible = []

        for depth in [1, 2]:
            wx = px + depth * dx
            wy = py + depth * dy

            if not self.level.is_walkable(wx, wy):
                break

            for entity in self.level.get_entities_at(wx, wy):
                if entity is self.player or not getattr(entity, 'is_renderable', False):
                    continue
                visible.append((entity, depth))

        return visible
