import pygame

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, MAP, ENEMIES, MAP_SPRITES, PLAYER_START_POS, ASSETS_PATH, PLAYER_CONFIG, logger
from src.entities import Player, Enemy
from src.level import Level
from src.render import GameRenderer, SpriteBase
from src.input_handler import InputHandler
from src.states import ExplorationState, GameState
from src.utils.config import load_config


class Game:
    def __init__(self, config_overrides: dict = {}):
        """Инициализация игры с возможностью переопределения конфигов"""
        config = load_config(config_overrides)

        # init graphics
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Taurus project")
        self.clock = pygame.time.Clock()

        self.player = Player(
            x=PLAYER_START_POS[0],
            y=PLAYER_START_POS[1]
        )
        weapon_key = PLAYER_CONFIG.get("starting_weapon", "rusty_sword")
        self._load_weapon_animations(self.player.inventory.current_weapon, weapon_key)
        self.map = MAP
        self.sprites = {
            textures: {
                texture_name: SpriteBase(texture_path)
                for texture_name, texture_path in pack.items()
            }
            for textures, pack in MAP_SPRITES.items()
        }
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
            self.current_state.render(dt)
            pygame.display.flip()

            if not action_taken:
                pygame.time.wait(10)

    def _load_weapon_animations(self, weapon, weapon_key: str):
        from src.animation import Animation, AnimationFrame, Animator
        anim_dir = ASSETS_PATH / "weapons" / weapon_key
        animator = Animator()
        # single-frame states: idle (loop), windup (loop), strike (one-shot)
        states = {
            "idle":   ("idle.png",    True,  1.0),
            "windup": ("windup.png",  True,  1.0),
            "strike": ("strike.png",  False, 0.2),
        }
        for name, (filename, loop, duration) in states.items():
            path = anim_dir / filename
            try:
                surface = pygame.image.load(str(path)).convert_alpha()
                animator.add(name, Animation([AnimationFrame(surface, duration)], loop=loop))
            except Exception as e:
                logger.warning(f"Weapon sprite not found: {path} ({e})")
        weapon.animator = animator
        animator.play("idle")

    def change_state(self, new_state: GameState):
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()
        logger.info(f"Entering state: {type(self.current_state).__name__}")