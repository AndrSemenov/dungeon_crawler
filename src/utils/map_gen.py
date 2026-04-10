import random


class MazeChecker:

    @staticmethod
    def is_point_in_maze(maze: list, x: int, y: int) -> bool:
        """Проверяет принадлежность точки к лабиринту"""
        size = len(maze)

        if -1 < x < size and -1 < y < size:
            return True
        else:
            return False

    @staticmethod
    def is_road(maze: list, x: int, y: int) -> bool:
        """Определяет проход или стена"""

        if MazeChecker.is_point_in_maze(maze, x, y):
            return bool(maze[y][x])
        else:
            return False

    def is_visitible(maze: list, x: int, y: int) -> bool:
        """"""

        if MazeChecker.is_point_in_maze(maze, x, y) and not MazeChecker.is_road(maze, x, y):
            return True
        else:
            return False


class MazeGenerator:

    def __init__(self, size):
        self.dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
        self.maze = [[0] * size for _ in range(size)]
        start_point = (random.randrange(0, size, 2), random.randrange(0, size, 2))
        self.to_visit = set()
        self.to_visit.add(start_point)
        print(start_point, self.to_visit)

        while self.to_visit:
            x, y = random.choice(list(self.to_visit))
            self.to_visit.remove((x, y))
            self.maze[y][x] = 1
            self._connect(x, y)
            self._add_visit_points(x, y)



    def _connect(self, x, y):
        for dir in random.sample(self.dirs, len(self.dirs)):
            if MazeChecker.is_road(self.maze, x + dir[0] * 2, y + dir[1] * 2):
                self.maze[y + dir[1]][x + dir[0]] = 1
                break

    def _add_visit_points(self, x, y):
        for dir in self.dirs:
            if MazeChecker.is_visitible(self.maze, x + dir[0] * 2, y + dir[1] * 2):
                self.to_visit.add((x + dir[0] * 2, y + dir[1] * 2))
