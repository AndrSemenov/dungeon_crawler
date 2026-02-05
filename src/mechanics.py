class Inventory:
    """Inventory for player. Only weapon and armour
    """

    def __init__(self) -> None:
        self.weapon = NotImplemented

    #
    # @property
    # def damage(self):
    #     """Just weapon damage. Maybe dice throw"""
    #     return self.weapon.damage

    # @property
    # def armour(self):
    #     """How much damage will be ignored"""
    #     return self.armour.


class Attributes:
    """Attributes for player. Placeholder for something like stats, levels, modifiers and etc.
    """
