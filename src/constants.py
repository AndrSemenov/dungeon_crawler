import yaml
import sys
import logging
from src.utils import map_gen

from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
ASSETS_PATH = ROOT_PATH / "data/assets"
SETTINGS_PATH = ROOT_PATH / "configs/default.yaml"
CONFIGS_PATH = ROOT_PATH / "data/configs"

with SETTINGS_PATH.open(encoding="utf-8") as f:
    config = yaml.safe_load(f)

for conf in ["enemies", "items", "level", "player"]:
    with (CONFIGS_PATH / f"{conf}.yaml").open(encoding="utf-8") as f:
        config.update(yaml.safe_load(f))

# LOGGING
LOG_LEVEL = "DEBUG"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# GRAPHICS
SCREEN_WIDTH: int = config["graphics"]["screen_width"]
SCREEN_HEIGHT: int = config["graphics"]["screen_height"]
FPS: int = config["graphics"]["fps"]

# LEVEL
MAP: list[list[int]] = map_gen.MazeGenerator(25, 75).maze

MAP_SPRITES: dict[str, dict[str, Path]] = {
    "hallway": {
        "hallway": ASSETS_PATH / "hallway_textures/hallway.png",
        "hallway_first_turn_both": ASSETS_PATH / "hallway_textures/hallway_first_turn_both.png",
        "hallway_first_turn_left": ASSETS_PATH / "hallway_textures/hallway_first_turn_left.png",
        "hallway_first_turn_right": ASSETS_PATH / "hallway_textures/hallway_first_turn_right.png",
        "hallway_second_turn_both": ASSETS_PATH / "hallway_textures/hallway_second_turn_both.png",
        "hallway_second_turn_right": ASSETS_PATH / "hallway_textures/hallway_second_turn_right.png",
        "hallway_second_turn_left": ASSETS_PATH / "hallway_textures/hallway_second_turn_left.png",
        "hallway_second_turn_right_and_first_turn_left": ASSETS_PATH / "hallway_textures/hallway_second_turn_right_and_first_turn_left.png",
        "hallway_second_turn_left_and_first_turn_right": ASSETS_PATH / "hallway_textures/hallway_second_turn_left_and_first_turn_right.png",
    },
    "hallway_2block": {
        "hallway_2block": ASSETS_PATH / "hallway_2block_textures/hallway_2block.png",
        "hallway_2block_first_turn_both": ASSETS_PATH / "hallway_2block_textures/hallway_2block_first_turn_both.png",
        "hallway_2block_first_turn_left": ASSETS_PATH / "hallway_2block_textures/hallway_2block_first_turn_left.png",
        "hallway_2block_first_turn_right": ASSETS_PATH / "hallway_2block_textures/hallway_2block_first_turn_right.png",
        "hallway_2block_second_turn_both": ASSETS_PATH / "hallway_2block_textures/hallway_2block_second_turn_both.png",
        "hallway_2block_second_turn_right": ASSETS_PATH / "hallway_2block_textures/hallway_2block_second_turn_right.png",
        "hallway_2block_second_turn_left": ASSETS_PATH / "hallway_2block_textures/hallway_2block_second_turn_left.png",
        "hallway_2block_second_turn_right_and_first_turn_left": ASSETS_PATH / "hallway_2block_textures/hallway_2block_second_turn_right_and_first_turn_left.png",
        "hallway_2block_second_turn_left_and_first_turn_right": ASSETS_PATH / "hallway_2block_textures/hallway_2block_second_turn_left_and_first_turn_right.png",
    },
    "hallway_1block": {
        "hallway_1block": ASSETS_PATH / "hallway_1block_textures/hallway_1block.png",
        "hallway_1block_turn_both": ASSETS_PATH / "hallway_1block_textures/hallway_1block_turn_both.png",
        "hallway_1block_turn_left": ASSETS_PATH / "hallway_1block_textures/hallway_1block_turn_left.png",
        "hallway_1block_turn_right": ASSETS_PATH / "hallway_1block_textures/hallway_1block_turn_right.png",
    },
    "wall_front": {
        "wall_front": ASSETS_PATH / "wall_front.png"
    }
}



# LOAD ENEMIES
ENEMIES = map_gen.EnemyGenerator(MAP, config).generate()

# LOAD PLAYER
# TODO: get from map config
PLAYER_START_POS = pos = next((i, j) for i, row in enumerate(MAP)
                    for j, val in enumerate(row)
                    if val == 1)

PLAYER_CONFIG = config.get("player", {})

DEFAULT_ATTRIBUTES = PLAYER_CONFIG.get("attributes", {
    "hp_max": 30,
    "defense": 3,
    "stamina_max": 100,
})

DEFAULT_WEAPON = config.get("weapons", {}).get(PLAYER_CONFIG.get("starting_weapon", "rusty_sword"))

QTE_CONFIG = config.get("combat", {}).get("qte", {})