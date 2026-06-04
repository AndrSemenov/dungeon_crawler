import pygame
import sys
import random

# ================= CONFIG =================
WINDOW_SIZE = (1024, 1024)
FPS = 60

BAR_WIDTH = 400
BAR_HEIGHT = 40
BAR_Y = 400

CURSOR_WIDTH_PCT = 0.02

BASE_SPEED = 800
ACCELERATION = 1

GREEN_OFFSET_PCT = 0.0  # смещение от центра (-1..1)
RANDOMIZE_GREEN_OFFSET = True
RANDOM_OFFSET_RANGE = 1.0

ACTION_KEY = pygame.K_SPACE
START_QTE_BUTTON = 1  # LMB
RESTART_KEY = pygame.K_r

META = 1

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# ================= MODELS =================
class Player:
    def __init__(self):
        self.hp = 40
        self.max_stamina = 100
        self.stamina = 100
        self.defense = 5
        self.attack_speed = 2
        self.attack_cd = 0.5
        self.cd_timer = 0
        self.stamina_regen = 4


class Enemy:
    def __init__(self):
        self.hp = 60
        self.attack = 10
        self.defense = 2
        self.damage = 8
        self.attack_speed = 6
        self.timer = self.attack_speed


class Weapon:
    def __init__(self):
        self.attack = 15
        self.damage = 5
        self.crit = 3
        self.stamina_cost = 10
        self.reduce_coef = 0.5


# ================= TIMING BAR =================
class TimingBar:
    def __init__(self, rect):
        self.current_offset = 0.0
        self.rect = rect
        self.active = False

        self.green = pygame.Rect(0, 0, 0, 0)
        self.yellow_l = pygame.Rect(0, 0, 0, 0)
        self.yellow_r = pygame.Rect(0, 0, 0, 0)

        self.cursor_width = int(self.rect.width * CURSOR_WIDTH_PCT)
        self.cursor_x = self.rect.left

    def start(self, atk, defense, crit_coef):
        self.active = True

        base_hit = atk / (atk + defense)
        hit = min(0.95, base_hit * (1 - (1 - base_hit) ** (META * 0.08)))
        crit = min(0.5, 0.1 * crit_coef)

        self.green_pct = hit * crit
        self.yellow_pct = hit - self.green_pct

        self.cursor_x = self.rect.left
        self.speed = BASE_SPEED
        self.direction = 1

        self._calc_zones()

        # random offset
        if RANDOMIZE_GREEN_OFFSET:
            self.current_offset = random.uniform(
                -RANDOM_OFFSET_RANGE, RANDOM_OFFSET_RANGE
            )
        else:
            self.current_offset = GREEN_OFFSET_PCT

    def _calc_zones(self):
        w = self.rect.width

        g = w * self.green_pct
        y_total = w * self.yellow_pct
        y_half = y_total / 2

        # 🔥 ВОТ ГЛАВНОЕ ИЗМЕНЕНИЕ
        center = self.rect.left + w / 2 + self.current_offset * (w / 2)

        self.green = pygame.Rect(center - g / 2, self.rect.top, g, self.rect.height)

        self.yellow_l = pygame.Rect(
            self.green.left - y_half, self.rect.top, y_half, self.rect.height
        )

        self.yellow_r = pygame.Rect(
            self.green.right, self.rect.top, y_half, self.rect.height
        )

    def update(self, dt):
        if not self.active:
            return

        self.cursor_x += self.direction * self.speed * dt

        if self.cursor_x <= self.rect.left:
            self.cursor_x = self.rect.left
            self.direction = 1

        if self.cursor_x + self.cursor_width >= self.rect.right:
            self.cursor_x = self.rect.right - self.cursor_width
            self.direction = -1

    def stop(self):
        if not self.active:
            return None

        rect = pygame.Rect(
            self.cursor_x, self.rect.top, self.cursor_width, self.rect.height
        )

        if rect.colliderect(self.green):
            result = "green"
        elif rect.colliderect(self.yellow_l) or rect.colliderect(self.yellow_r):
            result = "yellow"
        else:
            result = "red"

        self.active = False
        return result

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

        if self.active:
            pygame.draw.rect(screen, YELLOW, self.yellow_l.clip(self.rect))
            pygame.draw.rect(screen, YELLOW, self.yellow_r.clip(self.rect))
            pygame.draw.rect(screen, GREEN, self.green.clip(self.rect))

            pygame.draw.rect(
                screen,
                BLACK,
                (self.cursor_x, self.rect.top, self.cursor_width, self.rect.height),
            )


# ================= COMBAT TEST =================
class CombatTest:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 64)

        self.reset()

    def reset(self):
        self.player = Player()
        self.enemy = Enemy()
        self.weapon = Weapon()

        rect = pygame.Rect(
            (WINDOW_SIZE[0] - BAR_WIDTH) // 2, BAR_Y, BAR_WIDTH, BAR_HEIGHT
        )
        self.qte = TimingBar(rect)

        self.log = []
        self.state = "fight"  # fight / win / lose

    def add_log(self, text):
        self.log.append(text)
        if len(self.log) > 10:
            self.log.pop(0)

    def update(self, dt):
        if self.state != "fight":
            return

        self.enemy.timer -= dt
        self.player.cd_timer -= dt

        if self.enemy.timer <= 0:
            self.enemy.timer = self.enemy.attack_speed
            self.enemy_attack()

        self.qte.update(dt)

        if not self.qte.active:
            self.player.stamina += self.player.stamina_regen * dt
            if self.player.stamina > self.player.max_stamina:
                self.player.stamina = self.player.max_stamina

        # check end
        if self.enemy.hp <= 0:
            self.state = "win"
            self.add_log("Enemy defeated!")

        if self.player.hp <= 0:
            self.state = "lose"
            self.add_log("Player died!")

    def enemy_attack(self):
        base_hit = self.enemy.attack / (self.enemy.attack + self.player.defense)

        enemy_crit = 1

        if self.qte.active:
            self.qte.active = False
            self.add_log("QTE interrupted! Enemy advantage")
            enemy_crit = 2

        if random.random() < base_hit:
            self.player.hp -= self.enemy.damage * enemy_crit
            self.add_log(f"Enemy hits {self.enemy.damage * enemy_crit}")
        else:
            self.add_log("Enemy missed")

    def start_qte(self):
        if self.state != "fight":
            return
        if self.player.cd_timer <= 0:
            self.qte.start(self.weapon.attack, self.enemy.defense, self.weapon.crit)

    def resolve_qte(self, result):
        if self.state != "fight":
            return

        if result == "green":
            dmg = (self.weapon.damage * self.weapon.crit) * (self.player.stamina / 100)
            self.enemy.hp -= dmg
            self.add_log(f"CRIT {round(dmg, 2)}")

        elif result == "yellow":
            dmg = (self.weapon.damage * self.weapon.reduce_coef) * (
                (self.player.stamina / 100)
            )
            self.enemy.hp -= dmg
            self.player.stamina -= self.weapon.stamina_cost
            self.add_log(f"HIT {round(dmg, 2)}")

        else:
            self.add_log("FAIL → enemy bonus attack")
            self.enemy_attack()

        self.player.cd_timer = self.player.attack_cd

    def draw(self):
        self.screen.fill((30, 30, 30))

        self.qte.draw(self.screen)

        # Player
        self._draw_text(f"HP: {round(self.player.hp)}", 20, 900)
        self._draw_text(f"STA: {round(self.player.stamina)}", 20, 930)

        # Enemy
        self._draw_text(f"HP: {round(self.enemy.hp)}", 800, 900)
        self._draw_text(f"ATK: {self.enemy.attack}", 800, 930)

        # Timer
        if self.state == "fight":
            self._draw_text(f"Enemy in: {round(self.enemy.timer,1)}", 420, 50)

        # Log
        y = 700
        for line in self.log[-8:]:
            self._draw_text(line, 400, y)
            y += 25

        # End state
        if self.state == "win":
            self._draw_big("YOU WIN", 400, 200)
            self._draw_text("Press R to restart", 400, 260)
        elif self.state == "lose":
            self._draw_big("YOU DIED", 400, 200)
            self._draw_text("Press R to restart", 400, 260)

    def _draw_text(self, text, x, y):
        t = self.font.render(text, True, WHITE)
        self.screen.blit(t, (x, y))

    def _draw_big(self, text, x, y):
        t = self.big_font.render(text, True, WHITE)
        self.screen.blit(t, (x, y))


# ================= MAIN =================
def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    game = CombatTest(screen)

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == START_QTE_BUTTON:
                    game.start_qte()

            if event.type == pygame.KEYDOWN:
                if event.key == ACTION_KEY:
                    result = game.qte.stop()
                    if result:
                        game.resolve_qte(result)

                if event.key == RESTART_KEY:
                    if game.state != "fight":
                        game.reset()

        game.update(dt)
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
