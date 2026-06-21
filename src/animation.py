from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import pygame


@dataclass
class AnimationFrame:
    surface: pygame.Surface
    duration: float  # seconds


class Animation:
    """Sequence of frames, optionally looping."""

    def __init__(self, frames: list[AnimationFrame], loop: bool = True):
        self.frames = frames
        self.loop = loop
        self._index = 0
        self._elapsed = 0.0
        self.active = False
        self.completed = False

    def start(self):
        self._index = 0
        self._elapsed = 0.0
        self.active = True
        self.completed = False

    def stop(self):
        self.active = False

    def update(self, dt: float):
        if not self.active:
            return
        self._elapsed += dt
        while self._elapsed >= self.frames[self._index].duration:
            self._elapsed -= self.frames[self._index].duration
            next_index = self._index + 1
            if next_index < len(self.frames):
                self._index = next_index
            elif self.loop:
                self._index = 0
            else:
                self.completed = True
                self.active = False
                return

    @property
    def current_frame(self) -> pygame.Surface:
        return self.frames[self._index].surface

    @property
    def frame_index(self) -> int:
        return self._index


class Animator:
    """Manages named animations for a single entity; only one plays at a time."""

    def __init__(self):
        self._animations: dict[str, Animation] = {}
        self._current: Optional[str] = None

    def add(self, name: str, animation: Animation):
        self._animations[name] = animation

    def play(self, name: str):
        if name not in self._animations:
            return
        if self._current and self._current != name:
            self._animations[self._current].stop()
        self._current = name
        self._animations[name].start()

    def stop(self):
        if self._current:
            self._animations[self._current].stop()
            self._current = None

    def update(self, dt: float):
        if self._current:
            anim = self._animations[self._current]
            anim.update(dt)
            if anim.completed:
                self._current = None

    @property
    def active(self) -> bool:
        return self._current is not None and self._animations[self._current].active

    @property
    def current_frame(self) -> Optional[pygame.Surface]:
        if self.active:
            return self._animations[self._current].current_frame
        return None

    @property
    def current_animation(self) -> Optional[Animation]:
        if self._current:
            return self._animations[self._current]
        return None
