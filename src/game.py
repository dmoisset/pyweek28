from enum import Enum

import hero
from world import World, Direction
from menu import Menu, MenuItem, run
from util import roll


class DamageType(Enum):
    FIRE = "fire"
    ICE = "ice"
    PHYSICAL = "physical"


SEARCH_TIME = 1
MOVE_TIME = 1
BREAK_TIME = 2
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
            if new_room.door:
                self.visit_door()

    def visit_door(self, title: str = "There is a door here") -> None:
        def break_door() -> None:
            self.time += BREAK_TIME
            check = self.hero.strength.bonus + roll()
            assert self.hero.room.door
            if check >= self.hero.room.door.break_dc:
                self.hero.room.door = None
            else:
                self.visit_door("The door resists!")
            self.look()

        def search_traps() -> None:
            self.time += SEARCH_TIME
            check = self.hero.awareness.bonus + roll()
            self.hero.room.reveal_hidden(check)
            # TODO: give feedback if something happened/didn't happen
            self.look()

        def disarm_trap() -> None:
            raise NotImplementedError

        entries = [MenuItem(key="1", label="Break it", action=break_door)]
        if self.hero.room.trap is None or self.hero.room.trap.hide_dc > 0:
            entries.append(
                MenuItem(key="2", label="Check it for traps", action=search_traps)
            )
        else:
            entries.append(MenuItem(key="2", label="Disarm trap", action=disarm_trap))
        m = Menu(
            title=title,
            subtitle="What next?",
            entries=entries,
            cancel=self.hero.retreat,
        )
        run(m)

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
