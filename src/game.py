from enum import Enum

import hero
from world import World, Direction
from util import roll


class DamageType(Enum):
    FIRE = "fire"
    ICE = "ice"
    PHYSICAL = "physical"


SEARCH_TIME = 1
MOVE_TIME = 1
REST_TIME = 48


class Game:
    hero: hero.Hero
    world: World

    time: int = 0
    MAX_TIME: int = 100

    def __init__(self) -> None:
        self.world = World()
        self.hero = hero.Hero(self.world)
        self.look()

    def search(self) -> None:
        self.time += SEARCH_TIME
        room = self.hero.room
        check = self.hero.awareness.bonus + roll()
        for nr in room.neighbors.values():
            nr.reveal_hidden(check)
        self.look()

    def move(self, direction: Direction) -> None:
        self.time += MOVE_TIME
        room = self.hero.room
        if direction in room.neighbors:
            new_room = room.neighbors[direction]
            if not new_room.visible:
                # Hidden door; not moving
                return
            # TODO: handle traps, monster, etc etc
            self.hero.enter(new_room)
            self.look()

    def look(self) -> None:
        """Mark as seen rooms that are within line of sight"""
        start = self.hero.room
        start.look()
        for d in Direction:
            room = start
            while room.allows_sight and d in room.neighbors:
                room.look()
                room = room.neighbors[d]
            if room.visible:
                # We got to a room that blocks vision, but can be looked at
                room.look()

    def rest(self) -> None:
        self.time += REST_TIME
        self.hero.rest()
