from __future__ import annotations
from typing import Dict

class Level:
    def __init__(self,
                 player,
                 map,
                 sprites,
                 enemies,):
        self.player = player
        self.map = map
        self.sprites = sprites
        self.enemies = enemies

        self.entities_map: Dict[tuple[int, int], 'Enemy'] = {}
        self._rebuild_entities_map()

    def is_walkable(self, x, y):
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]): # че то не понял я в чем смысл, почему нельзя просто ходить по 1-ам
            return self.map[y][x] == 1
        return False

    def get_entity_at(self, x: int, y: int): #-> Enemy|None: # надо поспрашивать нейросеть, мб тут круче сделать какую-то мапу {(x, y): list[entities]}
        self.entities_map.get((x, y))

    def move_entity(self, entity, new_x: int, new_y: int):
        old_pos = (entity.x, entity.y)
        if old_pos in self.entities_map and self.entities_map[old_pos] is entity:
            del self.entities_map[old_pos]
        entity.x = new_x
        entity.y = new_y
        self.entities_map[(new_x, new_y)] = entity

    def remove_entity(self, entity):
        pos = (entity.x, entity.y)
        if pos in self.entities_map and self.entities_map[pos] is entity:
            del self.entities_map[pos]
        if entity in self.enemies:
            self.enemies.remove(entity)

    def _rebuild_entities_map(self):
        """Перестраивает словарь координат → сущность"""
        self.entities_map.clear()
        for enemy in self.enemies:
            pos = (enemy.x, enemy.y)
            # self.entities_map[pos] = self.entities_map.get(pos, []) + [enemy]
            self.entities_map[pos] = enemy



