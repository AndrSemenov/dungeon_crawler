import pygame
import random

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LOG_LEVEL, MAP, ENEMIES, MAP_SPRITES, PLAYER_START_POS, logger
from src.entities import Player, Enemy
from src.level import Level
from src.render import GameRenderer, SpriteBase
from src.input_handler import InputHandler
from src.states import ExplorationState, CombatState, GameState

class Game:
    def __init__(self):
        # init graphics
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # TODO: mb move to renderer
        # self.screen.fill((0, 0, 0))
        pygame.display.set_caption("Taurus project")
        self.clock = pygame.time.Clock()

        self.player = Player(x=PLAYER_START_POS[0], y=PLAYER_START_POS[1])
        self.map = MAP
        self.sprites = {textures: {texture_name: SpriteBase(texture_path) for texture_name, texture_path in pack.items()} for textures, pack in MAP_SPRITES.items()}
        self.enemies = [Enemy(**e) for e in ENEMIES]

        # init level
        self.level = Level(
            player=self.player,
            map=self.map,
            sprites=self.sprites,
            enemies=self.enemies
        )

        # init renderer
        self.renderer = GameRenderer(self.screen, self.level)

        # init player inputs
        self.input_handler = InputHandler()

        # init state
        self.current_state: GameState = ExplorationState(self)
        self.current_state.on_enter()

        logger.debug("Game initialized successfully!")

    def run(self):
        logger.info("Welcome to the game buddy!")
        self.running = True
        logger.debug("Trying to run game...")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Handle actions
            action_taken = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    if self.input_handler.process_event(event, self.current_state):
                        action_taken = True

            # Update current state
            self.input_handler.update(self.current_state, dt)
            self.current_state.update(dt)
            if isinstance(self.current_state, ExplorationState):
                self.current_state._update_approaches(dt)

            # Render
            self.current_state.render()
            pygame.display.flip()

            if not action_taken:
                pygame.time.wait(10)

    def change_state(self, new_state: GameState):
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()
        logger.info(f"Entering state: {GameState}")

    def update(self):
        # Здесь можно обновлять прогресс приближения врагов и т.д.
        for enemy in self.level.enemies:
            if enemy.charging:
                enemy.charge_progress += 0.075 * self.clock.get_time() / 1000.0
                if enemy.charge_progress >= 1.0:
                    # завершить зарядку, перейти в бой и т.д.
                    pass

    def loop(self):

        self.running = True

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0   # секунды

            action_taken = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    if self.combat_state is None:
                        if self.input_handler.process_event(event, self.level):
                            action_taken = True
                    else:
                        if self.combat_state.still_in_combat_check():
                            self.combat_state.resolve_combat_turn()
                        else:
                            if isinstance(self.combat_state.attacker, Player):
                                if self.combat_state.attacker.alive and not self.combat_state.defender.alive:
                                    self.level.remove_entity(self.combat_state.defender)
                                else:
                                    self.game_over()
                            else:
                                if self.combat_state.defender.alive and not self.combat_state.attacker.alive:
                                    self.level.remove_entity(self.combat_state.attacker)
                                else:
                                    self.game_over()
                            self.combat_state = None

            if action_taken:
                self._get_near_enemies()
                self.combat_state = self._check_combat()

            self.input_handler.update(self.level, dt)

            self.renderer.render()
            pygame.display.flip()

            # Если ничего не произошло — можно немного пропустить цикл
            # (опционально, для экономии CPU)
            if not action_taken:
                pygame.time.wait(10)

    # пример в game.py или в отдельном update_enemies()

    def game_over(self):
        exit()

    def update_enemies(self, dt: float):
        px, py = self.level.player.position
        dx, dy = self.level.player.direction_vectors
        front_x, front_y = px + dx, py + dy

        for enemy in self.level.enemies:
            if enemy.approach and enemy.approach.active:
                enemy.approach.update(dt)
                if enemy.approach.completed:
                    # завершаем приближение
                    self.level.move_entity(enemy, enemy.approach.target_x, enemy.approach.target_y)
                    enemy.approach = None
                    # запускаем бой, если враг теперь на позиции игрока
                    if (enemy.x, enemy.y) == (px, py):
                        self.start_combat(enemy)

            # проверка, может ли враг начать приближение
            elif (enemy.x, enemy.y) == (front_x, front_y):
                if random.random() < enemy.attack_probability:
                    logger.info(f"{enemy.id}")
                    approach = ApproachProcess(
                        target_x=px,
                        target_y=py,
                        duration=0.8 + random.uniform(-0.15, 0.15)  # небольшая вариация
                    )
                    approach.start()
                    enemy.approach = approach
                    # можно здесь проиграть звук "враг заметил", рычание и т.д.

    def _get_near_enemies(self):
        x, y = self.level.player.position
        dx, dy = self.level.player.direction_vectors

        # TODO: should work like raycasting
        # logger.debug(f"Trying to find enemies at: {x + dx}, {y + dy}")
        enemy_in_front = self.level.get_creature_at(x=x + dx, y=y + dy)
        enemy_in_back = self.level.get_creature_at(x=x - dx, y=y - dy)

        # TODO: wtf
        # if enemy_in_front and random.random() < enemy_in_front.attack_probability:
        #     logger.info(enemy_in_front)
        #     self._enemy_charge(enemy_in_front, x, y)
        # if enemy_in_back and random.random() < enemy_in_back.attack_probability:
        #     self._enemy_charge(enemy_in_back, x, y)
        if enemy_in_front or enemy_in_front:
            logger.debug(f"Got near enemies: {enemy_in_front}, {enemy_in_back}")

    def _enemy_charge(self, enemy: Enemy, target_x: int, target_y: int, advantage: int = 2):
        logger.info(f"{enemy.name} [{enemy.id}] charging")
        enemy.charging = True
        # Мгновенное для теста
        # enemy.approach_progress = 1.0
        enemy.charging = False
        self.level.move_entity(enemy, target_x, target_y)
        if (enemy.x, enemy.y) == self.player.position:
            logger.info(f"{enemy.name} charged successfully")
            # self._combat_loop(self.player, enemy)  # Или enemy как attacker, если он инициировал

    # def _combat_loop(self, attacker: Player|Enemy, defender: Enemy|Player):


    #     if isinstance(attacker, Player):
    #         self.input_handler.handle_combat(player=attacker, enemy=defender)
    #     else:
    #         logger.info(f"{attacker.name} [{attacker.id}] attacking {defender.name} [{defender.id}]")
    #         defender.get_damage(attacker.attack())

    #     attacker, defender = defender, attacker

    def _check_combat(self):
        x, y = self.level.player.position
        dx, dy = self.level.player.direction_vectors
        if enemy := self.level.get_creature_at(x=x+dx, y=y+dy):
            return CombatState(self.level.player, enemy, self.input_handler)
        else:
            return None

class CombatState:
    def __init__(self, attacker: Player|Enemy, defender: Enemy|Player, input_handler: InputHandler):
        self.attacker = attacker
        self.defender = defender
        self.input_handler = input_handler

    def still_in_combat_check(self):
        if self.attacker.alive and self.defender.alive:
            return True
        return False

    def resolve_combat_turn(self):
        logger.debug(f"attacker: {self.attacker.name} has hp: {self.attacker.hp_current}")
        if isinstance(self.attacker, Player):
            self.input_handler.handle_combat(player=self.attacker, enemy=self.defender)
        else:
            logger.info(f"{self.attacker.name} [{self.attacker.id}] attacking {self.defender.name} [{self.defender.id}]")
            self.defender.get_damage(self.attacker.attack())
        self.attacker, self.defender = self.defender, self.attacker
