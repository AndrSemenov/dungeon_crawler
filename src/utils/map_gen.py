import random
from collections import deque

class MazeChecker:

    @staticmethod
    def is_point_in_maze(maze: list, x: int, y: int) -> bool:
        """Проверяет принадлежность точки к лабиринту"""
        height = len(maze)
        width = len(maze[0])

        return 0 <= x < width and 0 <= y < height

    @staticmethod
    def is_road(maze: list, x: int, y: int) -> bool:
        """Определяет проход или стена"""
        if MazeChecker.is_point_in_maze(maze, x, y):
            return bool(maze[y][x])
        return False

    @staticmethod
    def is_visitible(maze: list, x: int, y: int) -> bool:
        """Можно ли посетить точку"""
        return (
            MazeChecker.is_point_in_maze(maze, x, y)
            and not MazeChecker.is_road(maze, x, y)
        )


class MazeGenerator:

    def __init__(self, width, height):
        self.dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))

        # создаём прямоугольный лабиринт
        self.maze = [[0] * width for _ in range(height)]

        # стартовая точка (по чётным координатам)
        start_point = (
            random.randrange(0, width, 2),
            random.randrange(0, height, 2)
        )

        self.to_visit = {start_point}

        while self.to_visit:
            x, y = random.choice(list(self.to_visit))
            self.to_visit.remove((x, y))

            self.maze[y][x] = 1
            self._connect(x, y)
            self._add_visit_points(x, y)

    def _connect(self, x, y):
        for dx, dy in random.sample(self.dirs, len(self.dirs)):
            nx, ny = x + dx * 2, y + dy * 2

            if MazeChecker.is_road(self.maze, nx, ny):
                self.maze[y + dy][x + dx] = 1
                break

    def _add_visit_points(self, x, y):
        for dx, dy in self.dirs:
            nx, ny = x + dx * 2, y + dy * 2

            if MazeChecker.is_visitible(self.maze, nx, ny):
                self.to_visit.add((nx, ny))


class EnemyGenerator:
    def __init__(self, maze: list, config):
        self.maze = maze
        self.config = config

        self.height = len(maze[0])
        self.width = len(maze)

        self.zone_width = self.width // 3

    def generate(self):
        enemies = []

        for enemy_name, count in self.config["spawn"].items():
            enemy_data = self.config["enemies"][enemy_name]
            difficulty = enemy_data["difficulty"]

            # 🔥 БОСС (difficulty = 4)
            if difficulty == 4:
                pos = self.find_boss_position()

                if pos:
                    x, y = pos
                    enemies.append({
                        "name": enemy_name,
                        "asset": enemy_data["asset"],
                        "hp_max": enemy_data["hp_max"],
                        "damage": enemy_data["damage"],
                        "x": x,
                        "y": y,
                    })
                else:
                    print("⚠️ Не удалось найти позицию для босса")

                continue

            # 👇 обычные враги
            positions = self._get_spawn_positions(difficulty, count)

            for x, y in positions:
                enemies.append({
                    "name": enemy_name,
                    "asset": enemy_data["asset"],
                    "hp_max": enemy_data["hp_max"],
                    "damage": enemy_data["damage"],
                    "x": x,
                    "y": y,
                })

        return enemies

    def _get_spawn_positions(self, difficulty, count):
        """Случайные позиции в зоне сложности"""
        positions = []

        zone_min_x = self.zone_width * (difficulty - 1)
        zone_max_x = self.zone_width * difficulty

        attempts = 0
        max_attempts = count * 20

        while len(positions) < count and attempts < max_attempts:
            x = random.randint(zone_min_x, zone_max_x - 1)
            y = random.randint(0, self.height - 1)

            if self.maze[x][y] == 1 and (y, x) not in positions:
                positions.append((y, x))

            attempts += 1

        if len(positions) < count:
            print(f"⚠️ Смогли заспавнить только {len(positions)} из {count} врагов сложности {difficulty}")

        return positions

    def find_boss_position(self):
        """Ищет ближайшую проходимую клетку к правому нижнему углу"""
        start = (self.width - 1, self.height - 1)

        visited = set()
        queue = deque([start])

        while queue:
            x, y = queue.popleft()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            if 0 <= x < self.width and 0 <= y < self.height:
                if self.maze[x][y] == 1:
                    return y, x

                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    queue.append((x + dx, y + dy))

        return None