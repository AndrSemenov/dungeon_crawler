from dataclasses import dataclass


@dataclass
class QTEConfig:
    base_speed: float = 420.0
    acceleration: float = 0.0
    green_offset_pct: float = 0.0
    randomize_offset: bool = True
    random_range: float = 0.85
    green_crit_multiplier: float = 1.6
    yellow_damage_coef: float = 0.75
    stamina_cost_on_miss: int = 5
    bar_width: int = 520
    bar_height: int = 48