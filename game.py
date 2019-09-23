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
        for nr in room.neighbors:
            room.reveal_hidden(check)

    def move(self, direction: Direction) -> None:
        self.time += MOVE_TIME
        room = self.hero.room
        if direction in room.neighbors:
            new_room = room.neighbors[direction]
            if new_room.door and new_room.door.hide_dc != 0:
                # Hidden door; not moving
                return
            # todo: handle traps, monster, etcetc
            self.hero.enter(new_room)

    def look(self) -> None:
        """Mark as seen rooms that are within line of sight"""
        start = self.hero.room
        start.look()
        for d in Direction:
            room = start
            while d in room.neighbors and room.neighbors[d].allows_sight:
                room = room.neighbors[d]
                room.look()

    def rest(self) -> None:
        self.time += REST_TIME
        self.hero.rest()
