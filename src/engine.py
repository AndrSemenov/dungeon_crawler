import pygame
import random


class GameEngine:
    def __init__(self, screen, player, map):
        self.screen = screen
        self.player = player
        self.map = map
        self.running = True

        # попробовать вынести подгрузку нужных ассетов в отдельный файл, который будет грузить только то, что указано в конфиге уровня
        self.hallway_textures = {

            'hallway': pygame.image.load("assets/hallway_textures/hallway.png"),
            'hallway_first_turn_both': pygame.image.load("assets/hallway_textures/hallway_first_turn_both.png"),
            'hallway_first_turn_left': pygame.image.load("assets/hallway_textures/hallway_first_turn_left.png"),
            'hallway_first_turn_right': pygame.image.load("assets/hallway_textures/hallway_first_turn_right.png"),
            'hallway_second_turn_both': pygame.image.load("assets/hallway_textures/hallway_second_turn_both.png"),
            'hallway_second_turn_right': pygame.image.load("assets/hallway_textures/hallway_second_turn_right.png"),
            'hallway_second_turn_left': pygame.image.load("assets/hallway_textures/hallway_second_turn_left.png"),
            'hallway_second_turn_right_and_first_turn_left': pygame.image.load("assets/hallway_textures/hallway_second_turn_right_and_first_turn_left.png"),
            'hallway_second_turn_left_and_first_turn_right': pygame.image.load("assets/hallway_textures/hallway_second_turn_left_and_first_turn_right.png")
        }
        self.hallway_2block_textures = {

            'hallway_2block': pygame.image.load("assets/hallway_2block_textures/hallway_2block.png"),
            'hallway_2block_first_turn_both': pygame.image.load("assets/hallway_2block_textures/hallway_2block_first_turn_both.png"),
            'hallway_2block_first_turn_left': pygame.image.load("assets/hallway_2block_textures/hallway_2block_first_turn_left.png"),
            'hallway_2block_first_turn_right': pygame.image.load("assets/hallway_2block_textures/hallway_2block_first_turn_right.png"),
            'hallway_2block_second_turn_both': pygame.image.load("assets/hallway_2block_textures/hallway_2block_second_turn_both.png"),
            'hallway_2block_second_turn_right': pygame.image.load("assets/hallway_2block_textures/hallway_2block_second_turn_right.png"),
            'hallway_2block_second_turn_left': pygame.image.load("assets/hallway_2block_textures/hallway_2block_second_turn_left.png"),
            'hallway_2block_second_turn_right_and_first_turn_left': pygame.image.load("assets/hallway_2block_textures/hallway_2block_second_turn_right_and_first_turn_left.png"),
            'hallway_2block_second_turn_left_and_first_turn_right': pygame.image.load("assets/hallway_2block_textures/hallway_2block_second_turn_left_and_first_turn_right.png")
        }

        self.hallway_1block_textures = {

            'hallway_1block': pygame.image.load("assets/hallway_1block_textures/hallway_1block.png"),
            'hallway_1block_turn_both': pygame.image.load("assets/hallway_1block_textures/hallway_1block_turn_both.png"),
            'hallway_1block_turn_left': pygame.image.load("assets/hallway_1block_textures/hallway_1block_turn_left.png"),
            'hallway_1block_turn_right': pygame.image.load("assets/hallway_1block_textures/hallway_1block_turn_right.png")
        }
        self.textures = {'hallway': self.hallway_textures,
        'hallway_2block': self.hallway_2block_textures,
        'hallway_1block': self.hallway_1block_textures,
        'wall_front': pygame.image.load("assets/wall_front.png")
        }

        self.center_x = screen.get_width() // 2
        self.center_y = screen.get_height() // 2

        self.visible_enemies = []

        #боевая система
        self.in_combat = False
        self.current_enemy = None
        self.player_turn = True
        self.awaiting_input = False
        self.log = ''
        self.game_over = False


    def handle_input(self):
        # print("Обработка событий")
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                print(f"Нажата клавиша: {event.key}")
                if event.key == pygame.K_UP:
                    print("движение вперед")
                    self.player.move_forward(self.map)
                elif event.key == pygame.K_LEFT:
                    print("поворот налево")
                    self.player.turn_left()
                elif event.key == pygame.K_RIGHT:
                    print("поворот направо")
                    self.player.turn_right()
                elif event.key == pygame.K_DOWN:
                    print("движение назад")
                    self.player.move_backward(self.map)

    def handle_combat_input(self):
        for event in pygame.event.get():
            print(self.awaiting_input)
            #print('режим боя')
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                print(f"Нажата клавиша: {event.key}")
                print(self.awaiting_input)
                if self.awaiting_input:
                    if event.key == pygame.K_SPACE:
                        self.resolve_combat_turn()



    def resolve_combat_turn(self):
        if self.current_enemy.HP <= 0:
            self.in_combat = False
            self.map.remove_enemy(self.current_enemy)
            print('Враг побежден')
            self.current_enemy = None
            return

        print(self.player.HP)
        print(self.current_enemy.HP)
        if self.player_turn:
            damage = self.player.damage
            self.current_enemy.HP -= damage
            print(f'self.log = f"Вы атаковали: -{damage} HP"')

        else:
            damage = self.current_enemy.damage

            if self.current_enemy.advantage > 1:
                print('враг атакует с преимуществом')
                self.log = 'враг атакует с преимуществом'
                damage *= self.current_enemy.advantage
                self.current_enemy.advantage = 1



            self.player.HP -= damage
            print(f"{self.current_enemy.__class__.__name__} атакует: -{damage} HP")
            self.log = f"{self.current_enemy.__class__.__name__} атакует: -{damage} HP"

        if self.player.HP <= 0:
            print('вы умерли')
            self.log = 'вы умерли'
            self.map.remove_enemy(self.current_enemy)
            self.in_combat = False
            self.current_enemy = None
            self.game_over = True


            return

        print(self.awaiting_input)
        # смена хода и ожидание действия
        self.player_turn = not self.player_turn
        self.awaiting_input = True

    def field_of_view(self):
        self.first_x = self.player.x + self.player.dx[self.player.dir]
        self.first_y = self.player.y + self.player.dy[self.player.dir]

        self.first_turn_right = self.map.is_walkable(self.first_x - self.player.dy[self.player.dir], self.first_y + self.player.dx[self.player.dir])
        self.first_turn_left = self.map.is_walkable(self.first_x + self.player.dy[self.player.dir], self.first_y - self.player.dx[self.player.dir])

        self.second_x = self.player.x + 2 * self.player.dx[self.player.dir]
        self.second_y = self.player.y + 2 * self.player.dy[self.player.dir]

        self.second_turn_right = self.map.is_walkable(self.second_x - self.player.dy[self.player.dir], self.second_y + self.player.dx[self.player.dir])
        self.second_turn_left = self.map.is_walkable(self.second_x + self.player.dy[self.player.dir], self.second_y - self.player.dx[self.player.dir])

        self.third_x = self.player.x + 3 * self.player.dx[self.player.dir]
        self.third_y = self.player.y + 3 * self.player.dy[self.player.dir]

        self.first_cell = self.map.is_walkable(self.first_x, self.first_y)
        self.second_cell = self.map.is_walkable(self.second_x, self.second_y)
        self.third_cell = self.map.is_walkable(self.third_x, self.third_y)

        self.pr_x = self.player.x - self.player.dx[self.player.dir]
        self.pr_y = self.player.y - self.player.dy[self.player.dir]


    def render(self, map_mode=True):

        self.screen.fill((0, 0, 0))

        self.draw_first_person_view()

        self.draw_enemy()



        if map_mode:
            self.render_map()

        font = pygame.font.SysFont(None, 28)
        text = font.render(self.log, True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        if self.in_combat:
            prompt = font.render(
                "Нажмите [SPACE], чтобы продолжить", True, (200, 200, 200)
            )
            self.screen.blit(prompt, (10, 40))

    def update(self):
        # print('вызван update')
        self.field_of_view()
        if not self.in_combat:
            self.check_combat_start()

        if self.in_combat:
            self.handle_combat_input()
        else:
            self.handle_input()

    #отрисовка коридоров
    def draw_first_person_view(self):



        #три клетки впереди свободны, рисуем коридор без тупика
        if self.first_cell and self.second_cell and self.third_cell:

            #если есть оба вторых поворота
            if self.second_turn_right and self.second_turn_left:
                self.screen.blit(self.textures['hallway']['hallway_second_turn_both'], (0, 0))

            #если второй поворот направо
            elif self.second_turn_right:
                #если первый поворот налево
                if self.first_turn_left:
                    self.screen.blit(self.textures['hallway']['hallway_second_turn_right_and_first_turn_left'], (0, 0))

                else:
                    self.screen.blit(self.textures['hallway']['hallway_second_turn_right'], (0, 0))

            #если второй поворот налево
            elif self.second_turn_left:
                #если первый поворот направо
                if self.first_turn_right:
                    self.screen.blit(self.textures['hallway']['hallway_second_turn_left_and_first_turn_right'], (0, 0))

                else:
                    self.screen.blit(self.textures['hallway']['hallway_second_turn_left'], (0, 0))

            #оба первых поворота
            elif self.first_turn_right and self.first_turn_left:
                self.screen.blit(self.textures['hallway']['hallway_first_turn_both'], (0, 0))

            #первый поворот направо
            elif self.first_turn_right:
                self.screen.blit(self.textures['hallway']['hallway_first_turn_right'], (0, 0))

            #первый поворот налево
            elif self.first_turn_left:
                self.screen.blit(self.textures['hallway']['hallway_first_turn_left'], (0, 0))

            #без поворотов
            else:
                 self.screen.blit(self.textures['hallway']['hallway'], (0, 0))




        elif self.first_cell and self.second_cell:

            #если есть оба вторых поворота
            if self.second_turn_right and self.second_turn_left:
                self.screen.blit(self.textures['hallway_2block']['hallway_2block_second_turn_both'], (0, 0))

            #если второй поворот направо
            elif self.second_turn_right:
                #если первый поворот налево
                if self.first_turn_left:
                    self.screen.blit(self.textures['hallway_2block']['hallway_2block_second_turn_right_and_first_turn_left'], (0, 0))

                else:
                    self.screen.blit(self.textures['hallway_2block']['hallway_2block_second_turn_right'], (0, 0))

            #если второй поворот налево
            elif self.second_turn_left:
                #если первый поворот направо
                if self.first_turn_right:
                    self.screen.blit(self.textures['hallway_2block']['hallway_2block_second_turn_left_and_first_turn_right'], (0, 0))

                else:
                    self.screen.blit(self.textures['hallway_2block']['hallway_2block_second_turn_left'], (0, 0))

            #оба первых поворота
            elif self.first_turn_right and self.first_turn_left:
                self.screen.blit(self.textures['hallway_2block']['hallway_2block_first_turn_both'], (0, 0))

            #первый поворот направо
            elif self.first_turn_right:
                self.screen.blit(self.textures['hallway_2block']['hallway_2block_first_turn_right'], (0, 0))

            #первый поворот налево
            elif self.first_turn_left:
                self.screen.blit(self.textures['hallway_2block']['hallway_2block_first_turn_left'], (0, 0))

            #без поворотов
            else:
                 self.screen.blit(self.textures['hallway_2block']['hallway_2block'], (0, 0))



        elif self.first_cell:
            #оба первых поворота
            if self.first_turn_right and self.first_turn_left:
                self.screen.blit(self.textures['hallway_1block']['hallway_1block_turn_both'], (0, 0))

            #первый поворот направо
            elif self.first_turn_right:
                self.screen.blit(self.textures['hallway_1block']['hallway_1block_turn_right'], (0, 0))

            #первый поворот налево
            elif self.first_turn_left:
                self.screen.blit(self.textures['hallway_1block']['hallway_1block_turn_left'], (0, 0))

            #без поворотов
            else:
                 self.screen.blit(self.textures['hallway_1block']['hallway_1block'], (0, 0))
        else:
            self.screen.blit(self.textures["wall_front"], (0, 0))

    #отрисовка врагов
    def draw_enemy(self):
        for dist, (fx, fy, scale, br) in enumerate([

            (self.second_x, self.second_y, 0.4, 0.15),
            (self.first_x, self.first_y, 0.75, 0.5)
        ]):
            enemy = self.map.get_enemy_at(fx, fy)

            if not enemy:
                continue



            enemy.render_state(self.first_x, self.first_y, scale, br, self.map)
            interp_scale, interp_brightness = enemy.scale, enemy.brightness


            original = enemy.get_dimmed_sprite(factor = interp_brightness)
            new_size = (int(original.get_width() * interp_scale), int(original.get_height() * interp_scale))
            scaled = pygame.transform.scale(original, new_size)
            self.screen.blit(scaled, (self.center_x - new_size[0] // 2, self.center_y - new_size[1] // 2))

    #отрисовка мини-карты
    def render_map(self):
        tile_size = 20
        map_data = self.map.map

        for y in range(len(map_data)):
            for x in range(len(map_data[y])):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)

                if map_data[y][x] == 0:
                    color = (80, 80, 80)  # стена
                else:
                    color = (0, 0, 0)  # проход

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)  # граница клеток

        # Игрок
        px = self.player.x * tile_size
        py = self.player.y * tile_size
        center_x = px + tile_size // 2
        center_y = py + tile_size // 2
        end_x = center_x + self.player.dx[self.player.dir] * tile_size // 2
        end_y = center_y + self.player.dy[self.player.dir] * tile_size // 2
        player_rect = pygame.Rect(px, py, tile_size, tile_size)
        pygame.draw.rect(self.screen, (255, 0, 0), player_rect)
        pygame.draw.line(self.screen, (0, 255, 0), (center_x, center_y), (end_x, end_y), 2)

    def check_combat_start(self):
        if self.in_combat:
            return

        enemy_in_front = self.map.get_enemy_at(self.first_x, self.first_y)

        enemy_in_back = self.map.get_enemy_at(self.pr_x, self.pr_y)

        if enemy_in_front:
            print(enemy_in_front.HP)
            if enemy_in_front.in_combat:
                self.in_combat = True
                self.current_enemy = enemy_in_front
                self.player_turn = False
                self.awaiting_input = True
                self.log = f"{enemy_in_front.__class__.__name__} атакует вас!"
                enemy_in_front.advantage = 2

            else:
                self.in_combat = True
                self.current_enemy = enemy_in_front
                self.player_turn = True
                self.awaiting_input = True
                self.log = f"Вы напали на {enemy_in_front.__class__.__name__}!"

        elif enemy_in_back:
            self.in_combat = True
            self.current_enemy = enemy_in_back
            self.player.opposite_dir()
            self.player_turn = False
            self.awaiting_input = True
            self.log = f"{enemy_in_back.__class__.__name__} атакует вас со спины!"
            enemy_in_back.advantage = 10






