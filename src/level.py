from src.entities import Player, Enemy
from typing import Sequence


class Level:
    def __init__(self,
                 player: Player,
                 map: Sequence[Sequence[int]],
                 enemies: Sequence[Enemy]): # TODO: maybe should use something like set
        self.player = player
        self.map = map
        self.enemies = enemies

        self.explored = [[False for x in range(len(self.map[y]))] for y in range(len(self.map))] # зачем нужно?

    def is_walkable(self, x, y):
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]): # че то не понял я в чем смысл, почему нельзя просто ходить по 1-ам
            return self.map[y][x] == 1
        return False

    def get_enemy_at(self, x, y): # надо поспрашивать нейросеть, мб тут круче сделать какую-то мапу {(x, y): list[entities]}
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy
        return None
