import yaml
import logging

from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "default.yaml"

with CONFIG_PATH.open(encoding="utf-8") as f:
    config = yaml.safe_load(f)

# LOGGING
LOG_LEVEL = "DEBUG"

# GRAPHICS
SCREEN_WIDTH: int = config["screen_width"]
SCREEN_HEIGHT: int = config["screen_height"]
FPS: int = config["fps"]

# LOAD LEVEL
# TODO: get from map generator
MAP: list[list[int]] = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 0, 1, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0],
]

# LOAD ENEMIES
# TODO: get from map config
ENEMIES = [
    {"cfg": "skeleton", "pos_x": 5, "pos_y": 1},
    {"cfg": "skeleton", "pos_x": 4, "pos_y": 1}
]

# LOAD PLAYER
# TODO: get from map config
PLAYER_START_POS = (1, 1)