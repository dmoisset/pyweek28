from typing import Optional, Set, Tuple

import game
import observer
from world import World, Room


class Stat:
    score: int = 0
    damage: int = 0

    @property
    def bonus(self) -> int:
        """Bonus to dice rolls when using this ability"""
        return (self.score - self.damage) // 2

    def heal(self) -> None:
        self.damage = 0


class Hero(observer.Observable):

    OBSERVABLE_FIELDS = {"room", "max_hit_points", "damage"}
    OBSERVABLE_PROPERTIES = {
        "room": ("x", "y"),
        "max_hit_points": ("hit_points",),
        "damage": ("hit_points",),
    }

    strength: Stat
    agility: Stat
    health: Stat
    awareness: Stat
    power: Stat

    room: Room
    previous_room: Optional[Room] = None

    max_hit_points: int
    damage: int = 0

    resistances: Set["game.DamageType"]

    def __init__(self, world: World) -> None:
        super().__init__()
        self.strength = Stat()
        self.agility = Stat()
        self.health = Stat()
        self.awareness = Stat()
        self.power = Stat()

        self.room = world.levels[0].entrance
        self.resistances = set()
        self.max_hit_points = 10  # FIXME: HP FORMULA BASED ON STATS!

    def stats(self) -> Tuple[Stat, ...]:
        return (self.strength, self.agility, self.health, self.awareness, self.power)

    @property
    def hit_points(self) -> int:
        hp = self.max_hit_points - self.damage
        return max(hp, 0)

    def rest(self) -> None:
        self.damage = 0
        for s in self.stats():
            s.heal()

    def take_damage(self, amount: int, kind: "game.DamageType") -> None:
        if kind in self.resistances:
            amount //= 2
        self.damage = min(self.max_hit_points, self.damage + amount)

    def enter(self, room: Room) -> None:
        assert room is not self.room
        self.previous_room = self.room
        self.room = room

    def retreat(self) -> None:
        assert self.previous_room is not None
        self.room = self.previous_room
        self.previous_room = None

    @property
    def x(self) -> int:
        return self.room.x

    @property
    def y(self) -> int:
        return self.room.y
