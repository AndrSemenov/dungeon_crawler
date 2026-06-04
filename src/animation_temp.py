"""
Система спрайтовой анимации для врагов и других сущностей.
Поддерживает воспроизведение последовательности фреймов с заданной скоростью.
"""
from __future__ import annotations
from pathlib import Path
import pygame
from dataclasses import dataclass
from typing import Optional, Dict, List
from src.constants import logger


@dataclass
class AnimationFrame:
    """Один фрейм анимации"""
    image: pygame.Surface
    duration: float  # Длительность фрейма в секундах


class AnimationState:
    """Состояние анимации (набор фреймов, которые воспроизводятся по очереди)"""
    def __init__(self, name: str, frames: List[pygame.Surface], 
                 frame_duration: float = 0.1, loop: bool = True):
        self.name = name
        self.frames = [AnimationFrame(frame, frame_duration) for frame in frames]
        self.loop = loop
        self.current_frame_index = 0
        self.elapsed_time = 0.0
        self.finished = False
    
    def update(self, dt: float) -> None:
        """Обновить состояние анимации"""
        if self.finished and not self.loop:
            return
        
        self.elapsed_time += dt
        current_frame = self.frames[self.current_frame_index]
        
        if self.elapsed_time >= current_frame.duration:
            self.elapsed_time -= current_frame.duration
            self.current_frame_index += 1
            
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self) -> pygame.Surface:
        """Получить текущий фрейм"""
        return self.frames[self.current_frame_index].image
    
    def reset(self) -> None:
        """Сбросить анимацию"""
        self.current_frame_index = 0
        self.elapsed_time = 0.0
        self.finished = False


class SpriteAnimator:
    """Управляет переключением между различными состояниями анимации"""
    def __init__(self):
        self.animations: Dict[str, AnimationState] = {}
        self.current_animation: Optional[AnimationState] = None
        self.brightness_factor = 1.0
        self.scale_factor = 1.0
    
    def add_animation(self, name: str, frames: List[pygame.Surface], 
                      frame_duration: float = 0.1, loop: bool = True) -> None:
        """Добавить новую анимацию"""
        animation = AnimationState(name, frames, frame_duration, loop)
        self.animations[name] = animation
    
    def set_animation(self, name: str) -> bool:
        """Переключиться на другую анимацию"""
        if name not in self.animations:
            logger.warning(f"Animation '{name}' not found in animator")
            return False
        
        if self.current_animation is not None:
            self.current_animation.reset()
        
        self.current_animation = self.animations[name]
        return True
    
    def update(self, dt: float) -> None:
        """Обновить текущую анимацию"""
        if self.current_animation is not None:
            self.current_animation.update(dt)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Получить текущий фрейм с применением эффектов"""
        if self.current_animation is None:
            return None
        
        frame = self.current_animation.get_current_frame()
        
        # Применяем эффекты (яркость и масштаб)
        frame = self._apply_brightness(frame, self.brightness_factor)
        frame = self._apply_scale(frame, self.scale_factor)
        
        return frame
    
    @staticmethod
    def _apply_brightness(surface: pygame.Surface, factor: float) -> pygame.Surface:
        """Применить эффект яркости"""
        if factor >= 1.0:
            return surface
        
        result = surface.copy()
        v = max(0, min(255, int(255 * factor)))
        result.fill((v, v, v, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return result
    
    @staticmethod
    def _apply_scale(surface: pygame.Surface, factor: float) -> pygame.Surface:
        """Применить масштабирование"""
        if factor >= 1.0 - 0.01:  # Примерно 1.0
            return surface
        
        new_size = (
            int(surface.get_width() * factor),
            int(surface.get_height() * factor)
        )
        return pygame.transform.scale(surface, new_size)


class AnimatedSprite:
    """Спрайт с поддержкой анимации"""
    def __init__(self):
        self.animator = SpriteAnimator()
    
    def add_animation(self, name: str, frame_paths: List[Path], 
                      frame_duration: float = 0.1, loop: bool = True) -> None:
        """Добавить анимацию по пути к фреймам"""
        frames = []
        for frame_path in frame_paths:
            if frame_path.exists():
                try:
                    frame = pygame.image.load(frame_path)
                    frames.append(frame)
                except pygame.error as e:
                    logger.error(f"Failed to load frame {frame_path}: {e}")
            else:
                logger.warning(f"Frame path does not exist: {frame_path}")
        
        if frames:
            self.animator.add_animation(name, frames, frame_duration, loop)
        else:
            logger.warning(f"No valid frames loaded for animation '{name}'")
    
    def set_animation(self, name: str) -> bool:
        """Переключиться на другую анимацию"""
        return self.animator.set_animation(name)
    
    def update(self, dt: float) -> None:
        """Обновить анимацию"""
        self.animator.update(dt)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Получить текущий фрейм"""
        return self.animator.get_current_frame()
    
    @property
    def brightness_factor(self) -> float:
        return self.animator.brightness_factor
    
    @brightness_factor.setter
    def brightness_factor(self, value: float):
        self.animator.brightness_factor = value
    
    @property
    def scale_factor(self) -> float:
        return self.animator.scale_factor
    
    @scale_factor.setter
    def scale_factor(self, value: float):
        self.animator.scale_factor = value
