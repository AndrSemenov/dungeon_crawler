# src/behaviors/approach.py   (новый файл или в mechanics.py)

from dataclasses import dataclass
from typing import Optional

@dataclass
class ApproachProcess:
    """Представляет процесс приближения врага к игроку"""
    target_x: int
    target_y: int
    duration: float = 0.8          # в секундах
    progress: float = 0.0
    start_scale: float = 0.4
    end_scale: float = 0.75
    start_brightness: float = 0.15
    end_brightness: float = 0.5

    active: bool = False
    completed: bool = False

    def update(self, dt: float) -> None:
        if not self.active:
            return

        self.progress += dt / self.duration
        if self.progress >= 1.0:
            self.progress = 1.0
            self.completed = True
            self.active = False

    @property
    def current_scale(self) -> float:
        t = self.progress
        return self.start_scale + (self.end_scale - self.start_scale) * t

    @property
    def current_brightness(self) -> float:
        t = self.progress
        return self.start_brightness + (self.end_brightness - self.start_brightness) * t

    def start(self):
        self.progress = 0.0
        self.completed = False
        self.active = True

    def reset(self):
        self.active = False
        self.completed = False
        self.progress = 0.0