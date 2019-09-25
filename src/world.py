from enum import Enum, auto
from typing import Dict, List, Optional

import observer


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


class Door(observer.Observable):

    OBSERVABLE_FIELDS = {"hide_dc"}

    kind: DoorKind
    hide_dc: int = 0  # Difficulty of finding if hidden. 0 if found or not hidden
    break_dc: int = 15

    def reveal(self) -> None:
        self.hide_dc = 0


class Trap:
    hide_dc: int = 0  # Difficulty of finding if hidden. 0 if found or not hidden

    def reveal(self) -> None:
        self.hide_dc = 0


class Room(observer.Observable):

    OBSERVABLE_FIELDS = {"seen"}

    level: "Level"
    x: int
    y: int

    terrain: Terrain = Terrain.EMPTY
    neighbors: Dict[Direction, "Room"]

    # Doors
    door: Optional[Door] = None  # None means no door

    # Traps
    trap: Optional[Trap] = None  # None means no trap

    seen: bool = False

    def __init__(self, level: "Level", x: int = 0, y: int = 0) -> None:
        self.neighbors = {}
        self.level = level
        self.x = x
        self.y = y
        super().__init__()

    @property
    def allows_sight(self) -> bool:
        """True if it's possible to see beyond this square"""
        return self.door is None

    @property
    def visible(self) -> bool:
        """True if it's possible to see this square"""
        return self.door is None or self.door.hide_dc == 0

    def reveal_hidden(self, check: int) -> None:
        if self.door and 0 < self.door.hide_dc <= check:
            self.door.reveal()
        elif self.trap and 0 < self.trap.hide_dc <= check:
            self.trap.reveal()

    def look(self) -> None:
        self.seen = True


class Level:
    entrance: Room

    def __init__(self, name: str) -> None:
        filename = f"maps/{name}.map"
        with open(filename, "r") as f:
            lines = f.readlines()
        width = len(lines[0])
        height = len(lines)
        if height % 2 == 0:
            raise ValueError(
                f"Malformed map, first line has height={height}, should be odd"
            )
        if width % 2:
            raise ValueError(
                f"Malformed map, first line has width={width}, should be even"
            )
        if any(len(l) != width for l in lines):
            raise ValueError(
                f"Malformed map, some lines have width different to {width}"
            )

        grid = [
            [Room(self, x, y) for x in range(width // 2 - 1)]
            for y in range(height // 2)
        ]

        # set a default entrance
        self.entrance = grid[0][0]

        for x in range(width // 2 - 1):
            rx = 2 * x + 1
            for y in range(height // 2):
                ry = 2 * y + 1
                room = grid[y][x]
                # Parse walls
                for d in Direction:
                    dx, dy = d.value
                    if lines[ry + dy][rx + dx] == " ":
                        # There is no wall in given direction, connect rooms
                        room.neighbors[d] = grid[y + dy][x + dx]
                # Parse room terrain
                terrain = lines[ry][rx]
                if terrain == "#":  # Door
                    room.door = Door()
                elif terrain == "S":  # Secret door
                    room.door = Door()
                    room.door.hide_dc = 15
                elif terrain == "<":  # Staircase down
                    self.entrance = room
                elif terrain == ">":  # Staircase up
                    pass  # FIXME
                elif terrain == " ":
                    pass
                else:
                    raise ValueError(
                        f"line {ry+1} char {rx+1}: unknown room type {terrain!r}"
                    )


class World:
    levels: List[Level]

    def __init__(self) -> None:
        self.levels = [Level("level0")]
