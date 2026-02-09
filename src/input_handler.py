import pygame
from src.entities import Player, Enemy
from src.game import logger
from src.level import Level

class InputHandler:
    def handle_movement(self, level: Level):
        player = level.player
        keys = pygame.key.get_pressed()
        # logger.debug(f"Pressed key: {keys}")

        moved = False
        if keys[pygame.K_UP]:
            moved = player.move_forward(level)
        if keys[pygame.K_DOWN]:
            moved = player.move_backward(level)
        if keys[pygame.K_LEFT]:
            player.turn_left()
        if keys[pygame.K_RIGHT]:
            player.turn_right()

    def handle_combat(self, player: Player, enemy: Enemy):
        keys = pygame.key.get_pressed()
        # logger.debug(f"Pressed key: {keys}")

        if keys[pygame.K_SPACE]:
            logger.info(f"{player.name} [{player.id}] attacking {enemy.name} [{enemy.id}]")
            enemy.modify_hp(player.attack()) # TODO: refactor логика обработки атаки должны быть в каком-то комбат манагере
