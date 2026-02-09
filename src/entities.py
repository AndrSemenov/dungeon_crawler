from abc import abstractmethod
from src.constants import logger
from src.render import SpriteEntity
from src.utils.rpg import Inventory, Attributes
from src.level import Level
from src.utils.directions import Direction, DIRECTION_VECTORS
from typing import Optional
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
            self.sprite = SpriteEntity(sprite_path)
        else:
            # TODO: add some placeholder, like blackpink textures in hl2
            self.sprite = None

class Creature(Entity):
    """Base class for creature. Like entity but can take damage, die, move
    """
    def __init__(self,
                 sprite_path: Optional[Path],
                 hp_max: int, # TODO: should be hp_max, hp_current, probably defined somewhere else
                 x: int = 0,
                 y: int = 0,
                 direction: Direction = Direction.NORTH):

        self.name = "Base creature"

        self.hp_max = hp_max
        self.hp_current = hp_max

        if self.hp_current > 0:
            self.alive = True
        else:
            self.alive = False

        super().__init__(x=x, y=y, sprite_path=sprite_path)
        self.direction = direction

    @abstractmethod
    def attack(self) -> int:
        ...

    def modify_hp(self, amount: int) -> None:
        logger.debug(f"Entity (id={self.id}, name={self.name}) change hp by {amount}")
        if amount < 0 and self.alive:
            logger.info(f"{self.name} [{self.id}] has lost {amount} HP")
            self.hp_current -= amount
        elif amount > 0 and self.alive:
            logger.info(f"{self.name} [{self.id}] has restored {amount} HP")
            self.hp_current += min(amount, self.hp_max - self.hp_current)
        self.alive_check()

    def alive_check(self) -> None:
        if self.hp_current and self.alive <= 0:
            logger.info(f"{self.name} [{self.id}] has died")
            self.alive = False

    @property
    def health(self) -> tuple[int, int]:
        return self.hp_current, self.hp_max

    # TODO: mb shoud be one method with different args?
    # def move_forward(self, level: Level):
    #     dx, dy = self.direction_vectors
    #     new_x = self.x + dx
    #     new_y = self.y + dy

    #     logger.debug(f"{self.name} [{self.id}] is trying to move forward to {new_x, new_y}")
    #     if level.is_walkable(new_x, new_y): # TODO: не нравится, что проверка проходимости вызывается в классе игрока, как будто это должна хенделить игра
    #         self.x = new_x
    #         self.y = new_y

    # def move_backward(self, level: Level):
    #     dx, dy = self.direction_vectors
    #     new_x = self.x - dx
    #     new_y = self.y - dy

    #     logger.debug(f"{self.name} [{self.id}] is trying to move backward to {new_x, new_y}")
    #     if level.is_walkable(new_x, new_y):
    #         self.x = new_x
    #         self.y = new_y

    # def move_forward(self, level: Level):
    #     dx, dy = self.direction_vectors
    #     new_x = self.x + dx
    #     new_y = self.y + dy
    #     if level.is_walkable(new_x, new_y):
    #         # Проверяем, что клетка свободна от других сущностей
    #         if level.get_entity_at(new_x, new_y) is None:
    #             level.move_entity(self, new_x, new_y)
    #             return True
    #     return False

    # def move_backward(self, level: Level):
    #     dx, dy = self.direction_vectors
    #     new_x = self.x - dx
    #     new_y = self.y - dy
    #     if level.is_walkable(new_x, new_y):
    #         if level.get_entity_at(new_x, new_y) is None:
    #             level.move_entity(self, new_x, new_y)
    #             return True
    #     return False

    def try_move(self, level: Level, dx: int, dy: int) -> bool:
        """
        Пытается переместить существо на смещение (dx, dy).
        Возвращает True, если перемещение успешно.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        if not level.is_walkable(new_x, new_y):
            return False

        if level.get_entity_at(new_x, new_y) is not None:
            # Можно позже добавить обработку столкновения / атаки
            return False

        level.move_entity(self, new_x, new_y)
        return True

    def move_forward(self, level: Level) -> bool:
        dx, dy = self.direction_vectors
        return self.try_move(level, dx, dy)

    def move_backward(self, level: Level) -> bool:
        dx, dy = self.direction_vectors
        return self.try_move(level, -dx, -dy)

    def turn_left(self):
        logger.debug(f"{self.name} [{self.id}] is rotating left")
        self.direction = Direction((self.direction.value - 1) % 4)

    def turn_right(self):
        logger.debug(f"{self.name} [{self.id}] is rotating right")
        self.direction = Direction((self.direction.value + 1) % 4)

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    @property
    def direction_vectors(self) -> tuple[int, int]:
        dx, dy = DIRECTION_VECTORS[self.direction]
        return dx, dy

class Player(Creature):
    """Player class. Acting with inventory
    """
    def __init__(self,
                 inventory: Inventory = Inventory(),
                 attributes: Attributes = Attributes(),
                 sprite_path: Optional[Path] = None,
                 hp_max: int = 10,
                 x: int = 0,
                 y: int = 0,
                 direction: Direction = Direction.NORTH):
        self.name = "Player"
        self.inventory = inventory
        super().__init__(x=x, y=y, direction=direction, sprite_path=sprite_path, hp_max=hp_max)

    def attack(self):
        """Attack throw"""
        # logger.debug(f"Attacking with weapon...")
        # self.inventory.weapon.attack_modifer + self.attributes[self.inventory.weapon.attack_modifier_type]
        # logger.debug(f"Attack throw...")
        # logger.info(f"")

        return self.inventory.damage


class Enemy(Creature):
    def __init__(self,
                 name: str,
                 hp_max: int,
                 damage: int,
                 asset: str,
                 attack_probability: float = 0.01, # TODO: refactor
                 x: int = 0,
                 y: int = 0,
                 sprite_root_dir: Path = Path("data/assets/enemies")
                 ):

        self.name = name
        super().__init__(x=x, y=y, sprite_path=sprite_root_dir / asset, hp_max=hp_max)
        self.damage = damage
        self.attack_probability = attack_probability

        self.combat_state = {
            "charging": False,
            "charge_progress": 0.0,
            "in_combat": False,
            "advantage": 1.0,
        }

        @property
        def charging(self) -> bool:
            return self.combat_state["charging"]

        # мб должно быть в какой-то отдельной логике типа паттернов поведения
        # в этих классах хочется иметь только все, что относится к энитити
        # self.approaching = False
        # self.trigger = False
        # self.approach_progress = 0.0
        # self.in_combat = False

        self.advantage = 1

    def attack(self) -> int:
        return self.damage


