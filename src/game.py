import pygame
import random

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LOG_LEVEL, MAP, ENEMIES, MAP_SPRITES, PLAYER_START_POS, logger
from src.entities import Player, Enemy
from src.level import Level
from src.render import GameRenderer, SpriteBase
from src.input_handler import InputHandler
from src.states import ExplorationState, CombatState, GameState

class Game:
    def __init__(self):
        # init graphics
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # TODO: mb move to renderer
        # self.screen.fill((0, 0, 0))
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

        # init state
        self.current_state: GameState = ExplorationState(self)
        self.current_state.on_enter()

        logger.debug("Game initialized successfully!")

    def run(self):
        logger.info("Welcome to the game buddy!")
        self.running = True
        logger.debug("Trying to run game...")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Handle actions
            action_taken = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    if self.input_handler.process_event(event, self.current_state):
                        action_taken = True

            # Update current state
            self.input_handler.update(self.current_state, dt)
            self.current_state.update(dt)
            if isinstance(self.current_state, ExplorationState):
                self.current_state._update_approaches(dt)

            # Render
            self.current_state.render()
            pygame.display.flip()

            if not action_taken:
                pygame.time.wait(10)

    def change_state(self, new_state: GameState):
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()
        logger.info(f"Entering state: {GameState}")