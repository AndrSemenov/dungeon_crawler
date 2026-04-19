class Inventory:
    """Inventory for player. Only weapon and armour
    """

    def __init__(self) -> None:
        self.weapon = NotImplemented

    # TODO: должно апдейтиться при обновлении активного оружия
    @property
    def damage(self) -> int:
        """Just weapon damage. Maybe dice throw"""
        # return self.weapon.damage
        return 2

    # TODO:
    # @property
    # def armour(self):
    #     """How much damage will be ignored"""
    #     return self.armour.


class Attributes:
    """Attributes for player. Placeholder for something like stats, levels, modifiers and etc.
    """
    def __init__(self):
        pass
