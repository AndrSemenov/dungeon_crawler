from enum import Enum

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

DIRECTION_VECTORS = {
    Direction.NORTH: (0, -1),
    Direction.EAST:  (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST:  (-1, 0)
}