from abc import abstractmethod
from src.constants import logger
from src.render import SpriteEntity
from src.utils.rpg import Inventory, Attributes, Weapon
from src.utils.directions import Direction, DIRECTION_VECTORS
from src.behaviors.approach import ApproachProcess
from src.level import Level
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

    def __str__(self) -> str:
        return f"{self.name, self.id}"

    @property
    def is_renderable(self) -> bool:
        return self.sprite is not None

    def get_render_params(self, depth: int) -> dict:
        return {
            "scale": 0.75 if depth == 1 else 0.4,
            "brightness": 0.5 if depth == 1 else 0.15,
        }

class Item(Entity):
    pass

class Creature(Entity):
    """Base class for creature. Like entity but can take damage, die, move
    """
    def __init__(self,
                 sprite_path: Optional[Path],
                 attributes: Attributes,
                 x: int = 0,
                 y: int = 0,
                 direction: Direction = Direction.NORTH):

        super().__init__(x=x, y=y, sprite_path=sprite_path)

        self.name = "Base creature"

        self.attributes = attributes

        if self.attributes.hp_current > 0:
            self.alive = True
        else:
            self.alive = False

        self.direction = direction

    def __bool__(self) -> bool:
        return self.alive

    @abstractmethod
    def attack(self) -> int:
        ...

    def get_damage(self, amount: int) -> None:
        assert amount >= 0, f"{self.name} [{self.id}] should get positive amount of damage! Got {amount} damage"
        assert self.alive, f"{self.name} [{self.id}] should be alive to take damage!"
        logger.debug(f"Entity (id={self.id}, name={self.name}) change hp by {amount}")
        if amount > 0:
            self.attributes.hp_current -= amount
        self.alive_check()

    def alive_check(self) -> None:
        if self.attributes.hp_current <= 0 and self.alive:
            logger.info(f"{self.name} [{self.id}] has died")
            self.alive = False

    @property
    def health(self) -> tuple[int, int]:
        return self.attributes.hp_current, self.attributes.hp_max

    def try_move(self, level: Level, dx: int, dy: int) -> bool:
        """
        Пытается переместить существо на смещение (dx, dy).
        Возвращает True, если перемещение успешно.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        if not level.is_walkable(new_x, new_y):
            logger.debug(f"{self.name} [{self.id}] tries to move and been blocked by wall at ({new_x}, {new_y})")
            return False

        creatures_there = level.get_creature_at(new_x, new_y)

        if creatures_there:
            logger.debug(f"{self.name} [{self.id}] tries to move and found creature(s) at ({new_x}, {new_y}): {creatures_there}")
            return False

        success = level.move_entity(self, new_x, new_y)
        if success:
            logger.debug(f"{self.name} [{self.id}] moved to ({new_x}, {new_y})")
        return success

    def move_forward(self, level: Level) -> bool:
        logger.debug(f"{self.name} [{self.id}] is moving forward")
        dx, dy = self.direction_vectors
        return self.try_move(level, dx, dy)

    def move_backward(self, level: Level) -> bool:
        logger.debug(f"{self.name} [{self.id}] is moving backward")
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
                 inventory: Optional[Inventory] = None,
                 attributes: Optional[Attributes] = None,
                 sprite_path: Optional[Path] = None,
                 x: int = 0,
                 y: int = 0,
                 direction: Direction = Direction.NORTH):

        from src.constants import DEFAULT_ATTRIBUTES, DEFAULT_WEAPON

        if attributes is None:
            attributes = Attributes(**DEFAULT_ATTRIBUTES)

        if inventory is None:
            weapon = Weapon(**DEFAULT_WEAPON)
            inventory = Inventory(current_weapon=weapon)

        super().__init__(attributes=attributes, sprite_path=sprite_path, x=x, y=y, direction=direction)

        self.name = "Player"
        self.inventory = inventory

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
                 defense: int = 0,
                 attack_speed: float = 3.0,
                 base_attack_probability: float = 0.01, # TODO: refactor
                 animations: Optional[dict] = None,
                 x: int = 0,
                 y: int = 0,
                 sprite_root_dir: Path = Path("data/assets/enemies")
                 ):
        attributes = Attributes(
            hp_max=hp_max,
            defense=defense
        )
        super().__init__(attributes=attributes, sprite_path=sprite_root_dir / asset, x=x, y=y)

        self.name = name
        self.damage = damage
        self.attack_speed = attack_speed
        self.attack_windup: float = 0.0  # duration of attack windup frame, set from animation config
        self.approach: Optional[ApproachProcess] = None

        if animations and self.sprite:
            self._load_animations(animations, sprite_root_dir)

    def _load_animations(self, config: dict, sprite_root_dir: Path) -> None:
        import pygame
        from src.animation import Animation, AnimationFrame, Animator

        animator = Animator()
        for anim_name, anim_cfg in config.items():
            frame_duration = anim_cfg.get("frame_duration", 0.2)
            loop = anim_cfg.get("loop", True)
            frames = []
            for filename in anim_cfg.get("frames", []):
                path = sprite_root_dir / filename
                try:
                    surface = pygame.image.load(str(path)).convert_alpha()
                    frames.append(AnimationFrame(surface=surface, duration=frame_duration))
                except Exception as e:
                    logger.warning(f"Failed to load animation frame {path}: {e}")

            if frames:
                animator.add(anim_name, Animation(frames, loop=loop))
                if anim_name == "attack":
                    self.attack_windup = frame_duration

        self.sprite.animator = animator

        self.combat_state = {
            "charging": False,
            "charge_progress": 0.0,
            "in_combat": False,
            "advantage": 1.0,
        }

    @property
    def charging(self) -> bool:
        return self.combat_state["charging"]

    @charging.setter
    def charging(self, value: bool):
        self.combat_state["charging"] = value

    @property
    def charge_progress(self) -> float:
        return self.combat_state["charge_progress"]

    @charge_progress.setter
    def charge_progress(self, value: float):
        self.combat_state["charge_progress"] = max(0.0, min(1.0, value))

    @property
    def attack_probability(self) -> float:
        # Можно будет модифицировать в зависимости от состояния
        return self.base_attack_probability

        # мб должно быть в какой-то отдельной логике типа паттернов поведения
        # в этих классах хочется иметь только все, что относится к энитити

    def attack(self) -> int:
        return self.damage

    def get_render_params(self, depth: int) -> dict:
        params = super().get_render_params(depth)

        if self.approach and self.approach.active:
            params["scale"] = self.approach.current_scale
            params["brightness"] = self.approach.current_brightness

        return params


