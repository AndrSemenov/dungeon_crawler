import argparse
import pygame
import random
import logging

from src.game import Game
from src.utils.config import load_config
from src.constants import logger

def parse_args():
    parser = argparse.ArgumentParser(description="Taurus — dungeon crawler")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-minimap", action="store_true", help="Disable minimap")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        logger.info(f"Using seed: {args.seed}")

    if args.debug:
        logger.setLevel(logging.DEBUG)

    pygame.init()

    config_overrides = {
        "show_minimap": not args.no_minimap,
    }

    game = Game(config_overrides=config_overrides)

    try:
        game.run()
    except Exception as e:
        logger.exception("Критическая ошибка в главном цикле")
    finally:
        pygame.quit()
        logger.info("Game terminated")