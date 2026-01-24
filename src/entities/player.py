class Player:
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]

    opposite = {0: 2, 1: 3, 2: 0, 3: 1}

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = 0
        self.damage = 2
        self.max_hp = 10
        self.HP = 10

    def opposite_dir(self):
           self.dir =self.opposite[self.dir]


# направления 0 - север, 1 - восток, 2 - юг, 3 - запад
    def turn_left(self):
        if self.dir - 1 > -1:
            self.dir -= 1
        else:
            self.dir = 3

    def turn_right(self):
        if self.dir + 1 < 4:
            self.dir += 1
        else:
            self.dir = 0

    def move_forward(self, map):
        if map.is_walkable(self.x + self.dx[self.dir], self.y + self.dy[self.dir]):
            self.x += self.dx[self.dir]
            self.y += self.dy[self.dir]
            print(self.x, self.y)
        else:
            print("Впереди стена")

    def move_backward(self, map):
        if map.is_walkable(self.x - self.dx[self.dir], self.y - self.dy[self.dir]):
            self.x -= self.dx[self.dir]
            self.y -= self.dy[self.dir]
            print(self.x, self.y)
        else:
            print("Сзади стена")
