import sys
import pygame
import logging

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LOG_LEVEL, MAP
from src.entities import Player, Enemy
from src.map import Map
from src.level import Level

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        # init graphics
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # init level
        self.level = Level(
            player=Player(x=1, y=1),
            map=
        )

        logger.debug("Game initialized successfully!")

    def run(self):