import pygame
import random

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LOG_LEVEL, MAP, ENEMIES, MAP_SPRITES, PLAYER_START_POS, logger
from src.entities import Player, Enemy
from src.level import Level
from src.render import GameRenderer, SpriteBase
from src.input_handler import InputHandler

class Game:
    def __init__(self):
        # init graphics
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # TODO: mb move to renderer
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("Taurus project")
        self.clock = pygame.time.Clock()

        self.player = Player(x=PLAYER_START_POS[0], y=PLAYER_START_POS[1])
        self.map = MAP
        self.sprites = {textures: {texture_name: SpriteBase(texture_path) for texture_name, texture_path in pack.items()} for textures, pack in MAP_SPRITES.items()}
        self.enemies = [Enemy(**e) for e in ENEMIES]

        # init level
        self.level = Level(
            player=self.player,
            map=self.map,
            sprites=self.sprites,
            enemies=self.enemies
        )

        # init renderer
        self.renderer = GameRenderer(self.screen, self.level)

        # init player inputs
        self.input_handler = InputHandler()

        self.running = False # idk
        logger.debug("Game initialized successfully!")

    def run(self):
        self.running = True
        logger.debug("Trying to run game...")

        self.in_combat = False
        self.loop()

    def update(self):
        if not self.in_combat:
            self._check_combat()
            self._get_near_enemies()
            self.input_handler.handle_movement(self.level)

    def loop(self):
        logger.info("Welcome to the game buddy!")
        self.combat_lock = False

        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.renderer.render()
            pygame.display.flip()
            self.clock.tick(FPS)
            self.update()

    def _get_near_enemies(self):
        x, y = self.level.player.position
        dx, dy = self.level.player.direction_vectors

        # TODO: should work like raycasting
        enemy_in_front = self.level.get_entity_at(x=x + dx, y=y + dy)
        enemy_in_back = self.level.get_entity_at(x=x - dx, y=y - dy)

        # return enemy_in_front, enemy_in_back

        # TODO: wtf
        if enemy_in_front and random.random() < enemy_in_front.attack_probability:
            self._enemy_charge(enemy_in_front, x, y)
        if enemy_in_back and random.random() < enemy_in_back.attack_probability:
            self._enemy_charge(enemy_in_back, x, y)

    def _enemy_charge(self, enemy: Enemy, target_x: int, target_y: int):
        logger.info(f"{enemy.name} [{enemy.id}] charging")
        enemy.charging = True
        approach_progress = 0.0

        while approach_progress < 1.0:
            approach_progress += 0.075
            yield approach_progress

        approach_progress = 0.0
        enemy.charging = False
        enemy.x, enemy.y = target_x, target_y

        if enemy.position == self.level.player.position:
            logger.info(f"{enemy.name} [{enemy.id}] charged successfully")
            self._combat_loop(enemy, self.level.player)

    def _combat_loop(self, attacker: Player|Enemy, defender: Enemy|Player):
        self.in_combat = True
        while all((attacker.alive, defender.alive)):
            if isinstance(attacker, Player):
                self.input_handler.handle_combat(player=attacker, enemy=defender)
            else:
                logger.info(f"{attacker.name} [{attacker.id}] attacking {defender.name} [{defender.id}]")
                defender.modify_hp(attacker.attack())
            attacker, defender = defender, attacker

    def _check_combat(self):
        if enemy := self.level.get_entity_at(*self.level.player.position):
            self._combat_loop(self.level.player, enemy)
