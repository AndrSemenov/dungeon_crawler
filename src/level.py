from __future__ import annotations
from typing import Dict, List, Optional
# from src.constants import logger # TODO: логгер можно не испортировать, достаточно создать в мейне и в остальных файлах, нужно поспрашивать ллм как правильнее сделать

class Level:
    def __init__(self, player, map: List[List[int]], sprites: Dict, enemies: List):
        self.player = player
        self.map = map
        self.sprites = sprites
        self.enemies = enemies

        self.entities_map: Dict[tuple[int, int], List] = {}
        self._rebuild_entities_map()

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]): # че то не понял я в чем смысл, почему нельзя просто ходить по 1-ам
            return self.map[y][x] == 1
        return False

    def get_entities_at(self, x: int, y: int) -> List: #-> Enemy|None: # надо поспрашивать нейросеть, мб тут круче сделать какую-то мапу {(x, y): list[entities]}
        return self.entities_map.get((x, y), [])

    def get_creature_at(self, x: int, y: int) -> 'Creature' | None:
        creatures = [e for e in self.get_entities_at(x, y) if hasattr(e, "alive")] # only one alive creature in pos
        assert len(creatures) < 2, f"There is more than one alive creature in {x, y}. Creatures: {creatures}"
        return creatures[0] if creatures else None

    def move_entity(self, entity, new_x: int, new_y: int) -> bool:
        old_pos = (entity.x, entity.y)
        new_pos = (new_x, new_y)

        if old_pos == new_pos:
            return False

        if old_pos in self.entities_map and entity in self.entities_map[old_pos]:
            self.entities_map[old_pos].remove(entity)
            if not self.entities_map[old_pos]:
                del self.entities_map[old_pos]

        if new_pos not in self.entities_map:
            self.entities_map[new_pos] = []
        self.entities_map[new_pos].append(entity)

        entity.x, entity.y = new_pos

        return True

    def remove_entity(self, entity):
        pos = (entity.x, entity.y)
        if pos in self.entities_map and entity in self.entities_map[pos]:
            self.entities_map[pos].remove(entity)
            if not self.entities_map[pos]:
                del self.entities_map[pos]

        if entity in self.enemies:
            self.enemies.remove(entity)

    def _rebuild_entities_map(self):
        """Перестраивает словарь координат → сущность"""
        self.entities_map.clear()

        self.entities_map.setdefault((self.player.x, self.player.y), []).append(self.player)

        for enemy in self.enemies:
            self.entities_map.setdefault((enemy.x, enemy.y), []).append(enemy)



