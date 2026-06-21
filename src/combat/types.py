from dataclasses import dataclass


@dataclass
class QTEConfig:
    base_speed: float = 4200.0
    base_crit_chance: float = 0.2
    acceleration: float = 0.0
    green_offset_pct: float = 0.0
    randomize_offset: bool = True
    random_range: float = 0.85
    stamina_cost_on_miss: int = 5
    bar_width: int = 520
    bar_height: int = 48