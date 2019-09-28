from enum import Enum, auto
import random
from typing import Dict, List, Optional

import game
import observer
import treasure

DOOR_TRAP_PROBABILITY = 0.6


class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, +1)
    EAST = (+1, 0)
    WEST = (-1, 0)

    def opposite(self) -> "Direction":
        x, y = self.value
        return Direction((-x, -y))


class DoorKind(Enum):
    WOOD = auto()
    SILVER = auto()
    GOLD = auto()


class Door(observer.Observable):

    OBSERVABLE_FIELDS = {"hide_dc"}

    kind: DoorKind
    hide_dc: int = 0  # Difficulty of finding if hidden. 0 if found or not hidden
    break_dc: int = 12

    def reveal(self) -> None:
        self.hide_dc = 0


class Trap:
    hide_dc: int = 12  # Difficulty of finding if hidden. 0 if found or not hidden
    disarm_dc: int = 15

    def reveal(self) -> None:
        self.hide_dc = 0


class Monster:
    ac: int = 12
    escape_dc: int = 10
    damage: int = 2

    def attack(self, g: "game.Game") -> None:
        """Called when the monster successfully lands an attack. Bad stuff happens"""
        g.hero.take_damage(self.damage, game.DamageType.PHYSICAL)


class Room(observer.Observable):

    OBSERVABLE_FIELDS = {"seen", "trap", "door", "monster", "loot"}

    level: "Level"
    x: int
    y: int

    neighbors: Dict[Direction, "Room"]

    # Doors
    door: Optional[Door] = None  # None means no door

    # Traps
    trap: Optional[Trap] = None  # None means no trap

    # Monsters
    monster: Optional[Monster] = None  # None means no monster

    # Treasure
    loot: Optional[treasure.Item] = None

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
        if self.door:
            # we nest the conditions. If there's a door we can't find a trap within from a
            # neighbor square; we need to check it from within
            if 0 < self.door.hide_dc <= check:
                self.door.reveal()
        else:
            self.reveal_traps(check)

    def reveal_traps(self, check: int) -> None:
        if self.trap and 0 < self.trap.hide_dc <= check:
            self.trap.reveal()

    def look(self) -> None:
        self.seen = True

    def validate(self) -> None:
        if self.door:
            if len(self.neighbors) != 2:
                raise ValueError(
                    f"room[{self.y}][{self.x}]: doors should have exactly 2 exits!"
                )
            d0, d1 = self.neighbors.keys()
            d0x, d0y = d0.value
            d1x, d1y = d1.value
            if d0x * d1x + d0y * d1y == 0:
                raise ValueError(
                    f"room[{self.y}][{self.x}]: doors should have 2 opposite exits!"
                )

    def is_entrance(self) -> bool:
        return self.level.entrance is self

    def is_exit(self) -> bool:
        return self.level.exit is self


def _inside(room: Room, d: Direction, width: int, height: int) -> bool:
    rx, ry = room.x, room.y
    dx, dy = d.value
    return (0 <= rx + dx < width) and (0 <= ry + dy < height)


class Level:
    entrance: Room
    exit: Room

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
                    if random.random() <= DOOR_TRAP_PROBABILITY:
                        room.trap = Trap()
                elif terrain == "S":  # Secret door
                    room.door = Door()
                    room.door.hide_dc = 10
                    if random.random() <= DOOR_TRAP_PROBABILITY:
                        room.trap = Trap()
                elif terrain == "<":  # Staircase down
                    self.entrance = room
                elif terrain == ">":  # Staircase up
                    self.exit = room
                elif terrain == " ":
                    pass
                elif terrain == "^":  # Standalone Trap
                    room.trap = Trap()
                elif terrain == "M":  # Monster
                    room.monster = Monster()
                elif terrain == "$":  # Random treasure
                    room.loot = treasure.Item.random()
                else:
                    raise ValueError(
                        f"line {ry+1} char {rx+1}: unknown room type {terrain!r}"
                    )
                room.validate()
        if "exit" not in vars(self):
            raise ValueError("Map has no exit!")

    @classmethod
    def random(cls, width: int = 24, height: int = 15) -> None:
        OPENNESS = 0.1  # Ratio of rooms that get an extra wall removed
        DOOR_DENSITY = 0.6  # Ratio of valid door locations that get a door
        DOOR_SECRECY = 0.2  # Percentage of doors that are made secret
        TRAP_DENSITY = 0.05  # Ratio of free locations made a standalone trap
        MONSTER_DENSITY = 0.1  # Ratio of free locations made a monster
        LOOT_DENSITY = 0.1  # Ratio of free locations made treasure

        # 0. Create grid
        self = object.__new__(cls)
        grid = [[Room(self, x, y) for x in range(width)] for y in range(height)]
        self.entrance = grid[0][0]
        self.exit = grid[height - 1][width - 1]

        # 1. Connect rooms until getting a spanning tree
        connected = {(0, 0)}
        frontier = [(0, 0)]
        while len(connected) < width * height:
            random.shuffle(frontier)
            fx, fy = frontier[-1]
            # compute neighbors
            neighbors = []
            if fx + 1 < width and (fx + 1, fy) not in connected:
                neighbors.append((fx + 1, fy, Direction.EAST))
            if fx - 1 >= 0 and (fx - 1, fy) not in connected:
                neighbors.append((fx - 1, fy, Direction.WEST))
            if fy + 1 < height and (fx, fy + 1) not in connected:
                neighbors.append((fx, fy + 1, Direction.SOUTH))
            if fy - 1 >= 0 and (fx, fy - 1) not in connected:
                neighbors.append((fx, fy - 1, Direction.NORTH))
            if neighbors:
                nx, ny, d = random.choice(neighbors)
                new_room = grid[ny][nx]
                grid[fy][fx].neighbors[d] = new_room
                new_room.neighbors[d.opposite()] = grid[fy][fx]
                connected.add((nx, ny))
                frontier.append((nx, ny))
            else:
                frontier.pop()

        # 2. Break down more walls to open it up a bit
        rooms = sum(grid, [])
        for _ in range(int(width * height * OPENNESS)):
            r = random.choice(rooms)
            walls = [
                d
                for d in Direction
                if d not in r.neighbors and _inside(r, d, width, height)
            ]
            if walls:
                # tear down random wall w
                w = random.choice(walls)
                dx, dy = w.value
                n = grid[r.y + dy][r.x + dx]
                r.neighbors[w] = n
                n.neighbors[w.opposite()] = r

        # 3. Add doors
        rooms.remove(self.exit)
        rooms.remove(self.entrance)
        random.shuffle(rooms)
        valid_door_locations = [
            r
            for r in rooms
            if len(r.neighbors) == 2
            and tuple(r.neighbors.keys())[0] == tuple(r.neighbors.keys())[1].opposite()
        ]
        door_count = int(len(valid_door_locations) * DOOR_DENSITY)
        for _ in range(door_count):
            r = valid_door_locations.pop()
            r.door = Door()
            if random.random() <= DOOR_SECRECY:
                r.door.hide_dc = 10
            if random.random() <= DOOR_TRAP_PROBABILITY:
                r.trap = Trap()
            rooms.remove(r)

        # 4. Add traps
        trap_count = int(len(rooms) * TRAP_DENSITY)
        for _ in range(trap_count):
            r = rooms.pop()
            r.trap = Trap()

        # 5. Add monsters
        monster_count = int(len(rooms) * MONSTER_DENSITY)
        for _ in range(monster_count):
            r = rooms.pop()
            r.monster = Monster()

        # 6. Add loot
        loot_count = int(len(rooms) * LOOT_DENSITY)
        for _ in range(loot_count):
            r = rooms.pop()
            r.loot = treasure.Item.random()

        return self


class World:
    levels: List[Level]

    def __init__(self) -> None:
        self.levels = [
            Level.random(),
            Level.random(),
            Level.random(),
            Level.random(),
            Level.random(),
            Level.random(),
        ]

    def level_number(self, l: Level) -> int:
        return self.levels.index(l)

    def level_above(self, l: Level) -> Optional[Level]:
        i = self.level_number(l)
        return self.levels[i + 1] if i + 1 < len(self.levels) else None

    def level_below(self, l: Level) -> Optional[Level]:
        i = self.level_number(l)
        return self.levels[i - 1] if i > 0 else None
