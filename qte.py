import pygame
import sys

# ================= CONFIG =================
WINDOW_SIZE = (1024, 1024)
FPS = 60



# Timing bar config
BAR_WIDTH = 400
BAR_HEIGHT = 40
BAR_Y = 500

# Характеристики врага
DEF = 10

# Характеристики игрока
META = 1 # метапрогресс
ATK = 10 #

# Характеристики оружия
CRIT = 3

YELLOW_WIDTH_PCT = 0.25
GREEN_WIDTH_PCT = YELLOW_WIDTH_PCT * (CRIT / 10)
GREEN_OFFSET_PCT = 0.0  # offset from center (-1 to 1 of half-width)
RANDOMIZE_GREEN_OFFSET = True
RANDOM_OFFSET_RANGE = 1.0  # max absolute offset as fraction of half-width (0..1)

CURSOR_WIDTH_PCT = 0.02

START_POS_PCT = 0.0  # from left

BASE_SPEED = 600  # pixels per second
ACCELERATION = 0.0  # pixels per second^2

TIME_LIMIT = 4  # seconds

ACTION_KEY = pygame.K_SPACE

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# ================= CLASS =================
class TimingBar:
    def __init__(self, rect):
        self.rect = rect
        self.reset()

    def reset(self):
        import random

        self.time = 0
        self.active = True
        self.result = None

        self.direction = 1
        self.speed = BASE_SPEED

        self.cursor_width = int(self.rect.width * CURSOR_WIDTH_PCT)
        self.cursor_x = self.rect.left + self.rect.width * START_POS_PCT

        # randomize green offset if enabled
        if RANDOMIZE_GREEN_OFFSET:
            self.current_offset = random.uniform(
                -RANDOM_OFFSET_RANGE, RANDOM_OFFSET_RANGE
            )
        else:
            self.current_offset = GREEN_OFFSET_PCT

        self._calculate_zones()

    def _calculate_zones(self):
        w = self.rect.width

        green_w = w * GREEN_WIDTH_PCT
        yellow_w = w * YELLOW_WIDTH_PCT

        center = self.rect.left + w / 2 + self.current_offset * (w / 2)

        self.green_zone = pygame.Rect(
            center - green_w / 2, self.rect.top, green_w, self.rect.height
        )

        self.yellow_left = pygame.Rect(
            self.green_zone.left - yellow_w,
            self.rect.top,
            yellow_w,
            self.rect.height,
        )

        self.yellow_right = pygame.Rect(
            self.green_zone.right,
            self.rect.top,
            yellow_w,
            self.rect.height,
        )

    def update(self, dt):
        if not self.active:
            return

        self.time += dt
        if self.time > TIME_LIMIT:
            self.result = "fail"
            self.active = False
            return

        # movement
        self.speed += ACCELERATION * dt
        self.cursor_x += self.direction * self.speed * dt

        if self.cursor_x <= self.rect.left:
            self.cursor_x = self.rect.left
            self.direction = 1

        if self.cursor_x + self.cursor_width >= self.rect.right:
            self.cursor_x = self.rect.right - self.cursor_width
            self.direction = -1

        self._zone_hooks()

    def _zone_hooks(self):
        zone = self._get_zone()

        # placeholder hooks
        if zone == "green":
            self.on_enter_green()
        elif zone == "yellow":
            self.on_enter_yellow()
        else:
            self.on_enter_red()

    def handle_input(self):
        if not self.active:
            return

        zone = self._get_zone()
        self.result = zone
        self.active = False

        # press hooks
        if zone == "green":
            self.on_press_green()
        elif zone == "yellow":
            self.on_press_yellow()
        else:
            self.on_press_red()

    def _get_zone(self):
        cursor_rect = pygame.Rect(
            self.cursor_x, self.rect.top, self.cursor_width, self.rect.height
        )

        if cursor_rect.colliderect(self.green_zone):
            return "green"
        elif cursor_rect.colliderect(self.yellow_left) or cursor_rect.colliderect(
            self.yellow_right
        ):
            return "yellow"
        else:
            return "fail"

    # ===== Hooks =====
    def on_enter_green(self):
        pass

    def on_enter_yellow(self):
        pass

    def on_enter_red(self):
        pass

    def on_press_green(self):
        pass

    def on_press_yellow(self):
        pass

    def on_press_red(self):
        pass

    # ===== Draw =====
    def draw(self, screen, font):
        # red base
        pygame.draw.rect(screen, RED, self.rect)

        # yellow
        pygame.draw.rect(screen, YELLOW, self.yellow_left.clip(self.rect))
        pygame.draw.rect(screen, YELLOW, self.yellow_right.clip(self.rect))

        # green
        pygame.draw.rect(screen, GREEN, self.green_zone.clip(self.rect))

        # cursor
        cursor_rect = pygame.Rect(
            self.cursor_x, self.rect.top, self.cursor_width, self.rect.height
        )
        pygame.draw.rect(screen, BLACK, cursor_rect)

        # result text
        if self.result:
            text_map = {
                "green": "идеально",
                "yellow": "успех",
                "fail": "провал",
            }
            text = font.render(text_map[self.result], True, WHITE)
            screen.blit(
                text, (self.rect.centerx - text.get_width() // 2, self.rect.bottom + 20)
            )


# ================= MAIN =================
def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    bar_rect = pygame.Rect(
        (WINDOW_SIZE[0] - BAR_WIDTH) // 2,
        BAR_Y,
        BAR_WIDTH,
        BAR_HEIGHT,
    )

    bar = TimingBar(bar_rect)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == ACTION_KEY:
                    if bar.active:
                        bar.handle_input()
                    else:
                        bar.reset()

        bar.update(dt)

        screen.fill((30, 30, 30))
        bar.draw(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
