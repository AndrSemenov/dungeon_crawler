import pygame
from src.game import logger
from src.mechanics import Inventory, Attributes
from typing import Optional, Any
from pathlib import Path

class Entity:
    """Base class for any game object. Can be placed and rendered
    """
    _next_id = 0

    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 sprite_path: Optional[Path] = None):
        self.id = Entity._next_id
        Entity._next_id += 1
        self.name = "Base entity"

        self.y = y
        self.x = x

        if sprite_path is not None:
            self.sprite = pygame.image.load(sprite_path)
        else:
            # TODO: add some placeholder, like blackpink textures in hl2
            self.sprite = None

class Creature(Entity):
    """Base class for creature. Like entity but can take damage, die, move
    """
    def __init__(self,
                 sprite_path: Path,
                 hp_max: int, # TODO: should be hp_max, hp_current, probably defined somewhere else
                 x: int = 0,
                 y: int = 0):
        self.name = "Base creature"

        self.hp_max = hp_max
        self.hp_current = hp_max

        if self.hp_current > 0:
            self.alive = True
        else:
            self.alive = False

        super().__init__(x=x, y=y, sprite_path=sprite_path)

    # def take_damage(self, damage: int = 0):
    #     logger.debug(f"Entity (id={self.id}, name={self.name}) taking {damage} damage")
    #     if damage > 0 and self.alive:
    #         self.health_points -= damage
    #     if self.health_points >= 0:
    #         logger.info(f"{self.name} dies!")
    #         self.alive = False

    def modify_hp(self, amount: int) -> None:
        logger.debug(f"Entity (id={self.id}, name={self.name}) change hp by {amount}")
        if amount < 0 and self.alive:
            self.hp_current -= amount
        elif amount > 0 and self.alive:
            self.hp_current += min(amount, self.hp_max - self.hp_current)
        self.alive_check()

    def alive_check(self) -> None:
        if self.hp_current and self.alive <= 0:
            self.alive = False

    @property
    def is_alive(self) -> bool:
        return self.alive

    @property
    def get_health(self) -> tuple[int, int]:
        return self.hp_current, self.hp_max


class Player(Creature):
    """Player class. Acting with inventory
    """
    def __init__(self,
                 sprite_path: Path,
                 inventory: Inventory,
                 attributes: Attributes,
                 hp_max: int = 10,
                 x: int = 0,
                 y: int = 0):
        self.inventory = inventory
        super().__init__(x=x, y=y, sprite_path=sprite_path, hp_max=hp_max)

    def attack(self):
        """Attack throw"""
        # logger.debug(f"Attacking with weapon...")
        # self.inventory.weapon.attack_modifer + self.attributes[self.inventory.weapon.attack_modifier_type]
        # logger.debug(f"Attack throw...")
        # logger.info(f"")

        return NotImplemented

class Enemy(Creature):
    def __init__(self,
                 name: str,
                 hp_max: int,
                 damage: int,
                 attack_probability: float = 0.01, # TODO: refactor
                 x: int = 0,
                 y: int = 0,
                 sprite_root_dir: Path = Path("data/assets/enemies")
                 ):

        self.name = name
        super().__init__(x=x, y=y, sprite_path=sprite_root_dir / self.name, hp_max=hp_max)
        self.damage = damage
        self.attack_probability = attack_probability

        self.approaching = False
        self.trigger = False
        self.approach_progress = 0.0
        self.in_combat = False

        self.advantage = 1
        
    def get_dimmed_sprite 



