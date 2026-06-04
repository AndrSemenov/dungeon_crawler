#!/usr/bin/env python3
"""
Скрипт для тестирования системы спрайтовой анимации врагов
"""

import sys
from pathlib import Path

# Добавляем root в путь
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from src.game import Game
from src.entities import Enemy


def test_animation_system():
    """Проверить что система анимации работает"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ СПРАЙТОВОЙ АНИМАЦИИ")
    print("=" * 60 + "\n")

    # Инициализируем pygame
    pygame.init()

    try:
        # Импортируем Game
        print("[1] Загрузка игры...")
        game = Game()
        print("✓ Игра загружена успешно\n")

        # Проверяем врагов
        print("[2] Проверка врагов...")
        print(f"   Всего врагов: {len(game.level.enemies)}")

        for enemy in game.level.enemies:
            if hasattr(enemy, "sprite") and enemy.sprite:
                has_anim = (
                    hasattr(enemy.sprite, "has_animation")
                    and enemy.sprite.has_animation()
                )
                print(f"   - {enemy.name}: анимация={'✓' if has_anim else '✗'}")

                if has_anim:
                    print(f"      Тип аниматора: {type(enemy.sprite.animated_sprite)}")

        print("\n✓ Система анимации работает корректно!\n")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        pygame.quit()


if __name__ == "__main__":
    success = test_animation_system()
    sys.exit(0 if success else 1)
