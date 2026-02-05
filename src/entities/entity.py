import pygame
from src.game import logger
from typing import Optional
from pathlib import Path

class Entity:
    """Base class for any game object
    """
    _next_id = 0

    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 sprite_path: Optional[Path] = None):
        self.id = Entity._next_id
        Entity._next_id += 1

        self.y = y
        self.x = x

        if sprite_path is not None:
            self.sprite = pygame.image.load(sprite_path)
