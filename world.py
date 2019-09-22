from enum import Enum, auto
from typing import Dict, List, Optional


class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, +1)
    EAST = (+1, 0)
    WEST = (-1, 0)


class Terrain(Enum):
    EMPTY = auto()
    DOOR = auto()
    TRAP = auto()
    STAIRS_UP = auto()
    STAIRS_DOWN = auto()


class DoorKind(Enum):
    WOOD = auto()
    SILVER = auto()
    GOLD = auto()


class Door:
    kind: DoorKind
    hide_dc: int = 0  # Difficulty of finding if hidden. 0 if found or not hidden

    def reveal(self):
        self.hide_dc = 0


class Trap:
    hide_dc: int = 0  # Difficulty of finding if hidden. 0 if found or not hidden

    def reveal(self):
        self.hide_dc = 0


class Room:
    terrain: Terrain = Terrain.EMPTY
    neighbors: Dict[Direction, "Room"]

    # Doors
    door: Optional[Door] = None  # None means no door

    # Traps
    trap: Optional[Trap] = None  # None means no trap

    seen: bool = False

    def __init__(self):
        self.neighbors = {}

    @property
    def allows_sight(self) -> bool:
        return self.door is None

    def reveal_hidden(self, check: int) -> None:
        if self.door and 0 < self.door.hide_dc <= check:
            self.door.reveal()
        elif self.trap and 0 < self.trap.hide_dc <= check:
            self.trap.reveal()

    def look(self):
        self.seen = True


class Level:
    entrance: Room

    def __init__(self):
        self.entrance = Room()


class World:
    levels: List[Level]

    def __init__(self):
        self.levels = [Level()]
