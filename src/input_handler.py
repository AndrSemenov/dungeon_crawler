import pygame
from src.entities import Player, Enemy
from src.game import logger
from src.level import Level

class InputAction:
    TURN_LEFT = "TURN_LEFT"
    TURN_RIGHT = "TURN_RIGHT"
    MOVE_FORWARD = "MOVE_FORWARD"
    MOVE_BACKWARD = "MOVE_BACKWARD"
    ATTACK = "ATTACK"
    ESCAPE = "ESCAPE"

class InputHandler:
    def __init__(self):
        self.keys_held = set()

    def process_event(self, event: pygame.event.Event, current_state) -> bool:
        """Обрабатывает одиночные нажатия (KEYDOWN)"""
        if event.type != pygame.KEYDOWN:
            return False

        action = None

        if event.key == pygame.K_LEFT:
            action = InputAction.TURN_LEFT
        elif event.key == pygame.K_RIGHT:
            action = InputAction.TURN_RIGHT
        elif event.key == pygame.K_UP:
            action = InputAction.MOVE_FORWARD
        elif event.key == pygame.K_DOWN:
            action = InputAction.MOVE_BACKWARD
        elif event.key == pygame.K_SPACE:
            action = InputAction.ATTACK
        elif event.key == pygame.K_ESCAPE:
            action = InputAction.ESCAPE

        if action:
            return current_state.handle_action(action)

        return False

    def update(self, current_state, dt: float = 0.0):
        """Для зажатых клавиш (пока не используем активно)"""
        pass

# class InputHandler:
#     def __init__(self):
#         self.keys_held = set()

# # TODO: накидал сам, потом навайбкодил на основе, в идеале раскурить некоторые моменты здесь
#     def process_event(self, event: pygame.event.Event, level: Level):
#         """
#         Обрабатываем события ввода.
#         Возвращает True, если было выполнено действие игрока.
#         """
#         if event.type != pygame.KEYDOWN:
#             return False

#         player = level.player
#         action_taken = False

#         # Повороты
#         if event.key == pygame.K_LEFT:
#             player.turn_left()
#             action_taken = True

#         elif event.key == pygame.K_RIGHT:
#             player.turn_right()
#             action_taken = True

#         # Движение
#         elif event.key == pygame.K_UP:
#             player.move_forward(level)
#             action_taken = True

#         elif event.key == pygame.K_DOWN:
#             player.move_backward(level)
#             action_taken = True

#         # Дополнительные действия (примеры)
#         elif event.key == pygame.K_m:
#             # переключение миникарты (если ты её уже добавил)
#             pass

#         elif event.key == pygame.K_SPACE:
#             # осмотр / взаимодействие / атака (потом реализуем)
#             pass

#         if action_taken:
#             # можно здесь добавить небольшой таймер, чтобы не спамили слишком быстро
#             # self.last_action_time = pygame.time.get_ticks() / 1000.0
#             pass

#         return action_taken

#     def update(self, level: Level, dt: float = 0.0):
#         player = level.player

#         # Повороты — мгновенные, по нажатию
#         if pygame.K_LEFT in self.keys_held:
#             player.turn_left()
#             self.keys_held.discard(pygame.K_LEFT)   # одноразово

#         if pygame.K_RIGHT in self.keys_held:
#             player.turn_right()
#             self.keys_held.discard(pygame.K_RIGHT)

#         # Движение — можно сделать как мгновенное, так и зажатое
#         if pygame.K_UP in self.keys_held:
#             player.move_forward(level)

#         if pygame.K_DOWN in self.keys_held:
#             player.move_backward(level)

#     def handle_combat(self, player: Player, enemy: Enemy):
#         keys = pygame.key.get_pressed()
#         # logger.debug(f"Pressed key: {keys}")

#         if keys[pygame.K_SPACE]:
#             logger.info(f"{player.name} [{player.id}] attacking {enemy.name} [{enemy.id}]")
#             enemy.get_damage(player.attack()) # TODO: refactor логика обработки атаки должны быть в каком-то комбат манагере
