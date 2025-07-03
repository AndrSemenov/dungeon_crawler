import enemy

class Map:
    def __init__(self):
        self.map = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0],
        ]

        self.enemies = {enemy.Skeleton(5, 1), enemy.Skeleton(4, 1)}

        self.explored = [[False for x in range(len(self.map[y]))] for y in range(len(self.map))]

    def is_walkable(self, x, y):
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]):
            return self.map[y][x] == 1
        return False

    def get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return enemy
        return None

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)


#print(Map().get_enemy_at(1, 5))
