from typing import Optional, Set

from game import DamageType
from world import Room


class Stat:
    score: int
    damage: int

    @property
    def bonus(self) -> int:
        """Bonus to dice rolls when using this ability"""
        return (self.score - self.damage) // 2

    def heal(self):
        self.damage = 0


class Hero:
    strength: Stat
    agility: Stat
    health: Stat
    awareness: Stat
    power: Stat

    room: Room
    previous_room: Optional[Room] = None

    def stats(self):
        return (self.strength, self.agility, self.health, self.awareness, self.power)

    hit_points: int
    max_hit_points: int

    resistances: Set[DamageType]

    def rest(self) -> None:
        self.hit_points = self.max_hit_points
        for s in self.stats():
            s.heal()

    def take_damage(self, amount: int, kind: DamageType) -> None:
        if kind in self.resistances:
            amount //= 2
        self.hit_points = max(0, self.hit_points - amount)

    def enter(self, room: Room) -> None:
        assert room is not self.room
        self.previous_room = self.room
        self.room = room

    def retreat(self) -> None:
        assert self.previous_room is not None
        self.room = self.previous_room
        self.previous_room = None
