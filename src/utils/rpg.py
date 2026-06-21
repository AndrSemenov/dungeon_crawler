from dataclasses import dataclass
from typing import Optional

@dataclass
class Weapon:
    """Player weapon stats
    """

    # damage = base_damage * modifier

    # modifier:
    #   if qte == red then 0.0
    #   elif qte == yellow then 1.0
    #   else then weapon.crit_multiplier

    # yellow zone width = weapon.accuracy / (weapon.accuracy + enemy_defense + 1.0)

    name: str
    base_damage: int
    accuracy: float = 1.0
    attack_speed: float = 1.0 # TODO: should define qte freq
    crit_chance: float = 0.2
    crit_multiplier: float = 1.5
    stamina_cost: int = 10
    qte_speed_bonus: float = 0.0


@dataclass
class Attributes:
    """Base creature attributes
    """
    hp_max: int = 30
    hp_current: int = 30
    defense: int = 3
    stamina_max: int = 100
    stamina_current: int = 100

    def __post_init__(self):
        self.hp_current = min(self.hp_current, self.hp_max)
        self.stamina_current = min(self.stamina_current, self.stamina_max)


class Inventory:
    """Inventory for player
    """

    def __init__(self, current_weapon: Optional[Weapon] = None) -> None:
        self.current_weapon = current_weapon or Weapon(
            name="Fists",
            base_damage=2,
            crit_multiplier=1.0,
            stamina_cost=0,
            qte_speed_bonus=0.0
        )

    # TODO: должно апдейтиться при обновлении активного оружия
    @property
    def damage(self) -> int:
        """Just weapon damage. Maybe dice throw"""
        # return self.weapon.damage
        return self.current_weapon.base_damage

    # TODO:
    # @property
    # def armour(self):
    #     """How much damage will be ignored"""
    #     return self.armour.
