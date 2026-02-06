# ---Импортируем библиотеку pygame---
import pygame

# ---Импортируем движок и объекты---
from src.entities.player import Player
from src.engine.map import Map
from src.engine.engine import GameEngine

# ---Инциализация---
pygame.init()
# ---Создание окна---
screen = pygame.display.set_mode((1024, 1024))
pygame.display.set_caption("Taurus project")
clock = pygame.time.Clock()
FPS = 60
# ---Инициализация карты---
game_map = Map()
# ---Инициализация игрока---
for i, j in ((0, 0), (0, 1), (1, 0), (1, 1)):
    if game_map.map[i][j]:
        player_x, player_y = i, j
        break
player = Player(x=player_x, y=player_y)
# ---Инициализация движка---
engine = GameEngine(screen, player, game_map)
# ---Главный игровой цикл---

while engine.running:
    engine.update()
    engine.render()
    pygame.display.flip()
    clock.tick(FPS)
    if engine.game_over:
        player.HP = player.max_hp
        player.x, player.y = 1, 1

        # 🕳 Показать чёрный экран перед перезапуском
        screen.fill((0, 0, 0))  # черный фон
        font = pygame.font.SysFont(None, 48)
        text = font.render("Вы умерли. Возрождение...", True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                           screen.get_height() // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # 2 секунды паузы
        engine = GameEngine(screen, player, Map())
# ---Закрытие всех модулей Pygame---
pygame.quit()
