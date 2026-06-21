import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(overrides: Dict[str, Any] = {}) -> Dict:
    """Загружает конфигурацию из yaml файлов с возможностью переопределения"""
    ROOT_PATH = Path(__file__).parent.parent.parent
    SETTINGS_PATH = ROOT_PATH / "configs/default.yaml"
    CONFIGS_PATH = ROOT_PATH / "data/configs"

    with SETTINGS_PATH.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for conf in ["enemies", "items", "level", "player"]:
        conf_path = CONFIGS_PATH / f"{conf}.yaml"
        if conf_path.exists():
            with conf_path.open(encoding="utf-8") as f:
                config.update(yaml.safe_load(f) or {})

    if overrides:
        config.update(overrides)

    return config