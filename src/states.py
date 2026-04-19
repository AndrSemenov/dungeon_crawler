from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
import time
import random

from src.entities import Enemy
from src.constants import logger
from src.input_handler import InputAction
from src.behaviors.approach import ApproachProcess

if TYPE_CHECKING:
    from src.game import Game
    from src.level import Level

class GameState(ABC):
    def __init__(self, game: Game):
        self.game = game
        self.level: Level = game.level

    @abstractmethod
    def handle_action(self, action: str) -> bool:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.game.renderer.render()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def __str__(self) -> str:
        return self.__name__

class ExplorationState(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.last_approach_check = time.time()

    def handle_action(self, action: str) -> bool:
        player = self.level.player

        if action == InputAction.TURN_LEFT:
            player.turn_left()
            return True
        elif action == InputAction.TURN_RIGHT:
            player.turn_right()
            return True
        elif action == InputAction.MOVE_FORWARD:
            return self._try_move_forward()
        elif action == InputAction.MOVE_BACKWARD:
            return self._try_move_backward()
        elif action == InputAction.ESCAPE:
            return True

        return False

    def _check_position_ahead(self, x: int, y: int) -> bool:
        """Проверяет, что находится на целевой клетке"""
        creatures_there = self.level.get_creature_at(x, y)
        if creatures_there:
            enemy = creatures_there
            if isinstance(enemy, Enemy):
                logger.info(f"Player stepped next to {enemy.name} → starting combat")
                self.game.change_state(CombatState(self.game, enemy))
                return True
        return False

    def _try_move_forward(self) -> bool:
        player = self.level.player
        dx, dy = player.direction_vectors
        new_x = player.x + dx
        new_y = player.y + dy

        if player.try_move(self.level, dx, dy):
            return True

        # Проверка на вход в бой
        return self._check_for_immediate_combat(new_x, new_y)

    def _try_move_backward(self) -> bool:
        player = self.level.player
        dx, dy = player.direction_vectors
        new_x = player.x - dx
        new_y = player.y - dy

        if player.try_move(self.level, -dx, -dy):
            return True

        return self._check_for_immediate_combat(new_x, new_y)

    def _check_for_immediate_combat(self, x: int, y: int) -> bool:
        """Если игрок пытается наступить на клетку с врагом — сразу бой"""
        creatures_there = self.level.get_creature_at(x, y)
        if creatures_there:
            enemy = creatures_there
            if isinstance(enemy, Enemy):
                logger.info(f"Player moved next to {enemy.name} → immediate combat")
                self.game.change_state(CombatState(self.game, enemy))
                return True
        return False

    def update(self, dt: float) -> None:
        """Проверка: может ли враг сам начать approach, когда стоит рядом с игроком"""
        now = time.time()
        if now - self.last_approach_check < 0.5:   # проверяем не чаще раза в 0.5 сек
            return
        self.last_approach_check = now

        px, py = self.level.player.position
        dx, dy = self.level.player.direction_vectors

        # Check for combat with nearest enemies
        for direction in [(dx, dy), (-dx, -dy)]:
            check_x = px + direction[0]
            check_y = py + direction[1]
            if self.level.get_creature_at(check_x, check_y):
                enemy = self.level.get_creature_at(check_x, check_y)
                if isinstance(enemy, Enemy):
                    logger.info(f"Player is now adjacent to {enemy.name} → starting combat")
                    self.game.change_state(CombatState(self.game, enemy))
                    return

        # Check enemy charge
        mid_x = px + dx
        mid_y = py + dy
        enemy_x = px + 2 * dx
        enemy_y = py + 2 * dy

        if (self.level.is_walkable(mid_x, mid_y) and
            not self.level.get_creature_at(mid_x, mid_y) and
            self.level.get_creature_at(enemy_x, enemy_y)):

            enemy = self.level.get_creature_at(enemy_x, enemy_y)
            if isinstance(enemy, Enemy) and not getattr(enemy, 'approach', None):
                if random.random() < 0.75: # TODO: should be defined in enemy config
                    approach = ApproachProcess(
                        target_x=mid_x,
                        target_y=mid_y,
                        duration=1.2
                    )
                    approach.start()
                    enemy.approach = approach
                    logger.info(f"{enemy.name} starts APPROACH from 2 cells away!")

    # TODO: какое-то говно, нужно сделать отдельный апдейтер для всех процессов, которые могут происходить в игре
    def _update_approaches(self, dt: float):
        """Вызывается каждый кадр — обновляет все активные approach"""
        for enemy in self.level.enemies:
            if hasattr(enemy, 'approach') and enemy.approach and enemy.approach.active:
                enemy.approach.update(dt)

                if enemy.approach.completed:
                    logger.info(f"{enemy.name} finished approach → starting combat!")
                    self.level.move_entity(enemy, enemy.approach.target_x, enemy.approach.target_y)
                    self.game.change_state(CombatState(self.game, enemy))
                    enemy.approach = None

class CombatState(GameState):
    def __init__(self, game: Game, enemy: Optional['Enemy'] = None):
        super().__init__(game)
        self.enemy = enemy
        self.last_enemy_attack_time = time.time()

    def on_enter(self) -> None:
        if self.enemy:
            logger.info(f"→ Entered combat with {self.enemy.name} [{self.enemy.id}]")
        self.last_enemy_attack_time = time.time()

    def handle_action(self, action: str) -> bool:
        if action == InputAction.ATTACK and self.enemy:
            logger.info(f"Player attacks {self.enemy.name}!")
            damage = self.level.player.attack()
            self.enemy.get_damage(damage)

            if not self.enemy.alive:
                logger.info(f"{self.enemy.name} died!")
                self.level.remove_entity(self.enemy)
                self.game.change_state(ExplorationState(self.game))
                return True

            return True

        elif action == InputAction.MOVE_BACKWARD:
            logger.info("Retreated from combat")
            self.game.change_state(ExplorationState(self.game))
            return True

        return False

    def update(self, dt: float) -> None:
        """Автоматическая атака врага каждые ~1.8 секунды"""
        if not self.enemy or not self.enemy.alive:
            return

        now = time.time()
        if now - self.last_enemy_attack_time >= 1.8: # TODO: must be param defined by amount of enemy attacks in turn + random
            damage = self.enemy.attack()
            self.level.player.get_damage(damage)
            logger.info(f"{self.enemy.name} attacks player for {damage} damage!")

            self.last_enemy_attack_time = now

            # Если игрок умер — конец боя
            if not self.level.player.alive:
                logger.info("Player died!")
                self._end_combat(game_over=True)

    def _end_combat(self, game_over: bool = False):
        if self.enemy and not self.enemy.alive:
            logger.info(f"{self.enemy.name} died! Removing from level.")
            self.level.remove_entity(self.enemy)

        if game_over:
            logger.info("GAME OVER")
            # TODO: позже сделаем экран смерти
            self.game.running = False
        else:
            self.game.change_state(ExplorationState(self.game))