from enum import Enum
from typing import List

import hero
from observer import Observable
from menu import Menu, MenuItem
from world import World, Direction
from util import roll


class DamageType(Enum):
    FIRE = "fire"
    ICE = "ice"
    PHYSICAL = "physical"


SEARCH_TIME = 1
MOVE_TIME = 1
BREAK_TIME = 2
REST_TIME = 96


class Game(Observable):

    OBSERVABLE_FIELDS = {"time"}

    hero: hero.Hero
    world: World

    time: int = 0
    MAX_TIME: int = 100

    _events: List[Menu]

    def __init__(self) -> None:
        super().__init__()
        self.world = World()
        self.hero = hero.Hero(self.world)
        self._events = []
        self.look()

    def add_message(self, message: str, subtitle: str = "") -> None:
        self._events.append(Menu(title=message, subtitle=subtitle))
        self.request_notify({"events": self._events})

    def add_menu(self, menu: Menu) -> None:
        self._events.append(menu)
        self.request_notify({"events": self._events})

    def pop_events(self) -> List[Menu]:
        result = self._events
        self._events = []
        return result

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
        if room.door is not None:
            # the only way out from a door, is away
            self.hero.retreat()
            return
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
                self.add_message("Crash! the door opens!")
            else:
                self.visit_door("WHAAAM! The door resists...")
            self.look()

        def search_traps() -> None:
            self.time += SEARCH_TIME
            check = self.hero.awareness.bonus + roll()
            self.hero.room.reveal_hidden(check)
            # TODO: give feedback if something happened/didn't happen
            self.look()
            if self.hero.room.trap is None or self.hero.room.trap.hide_dc > 0:
                self.visit_door("Doesn't seem to be trapped...")
            else:
                self.visit_door("It's a trap!")

        def disarm_trap() -> None:
            raise NotImplementedError

        entries = [
            MenuItem(
                key="K_1",
                label="[1] Break it",
                subtitle="If the door is trapped, this will trigger the trap",
                action=break_door,
            )
        ]
        if self.hero.room.trap is None or self.hero.room.trap.hide_dc > 0:
            entries.append(
                MenuItem(key="K_2", label="[2] Check it for traps", action=search_traps)
            )
        else:
            entries.append(
                MenuItem(
                    key="K_2",
                    label="[2] Disarm trap",
                    subtitle="Failure will trigger the trap",
                    action=disarm_trap,
                )
            )
        entries.append(
            MenuItem(key="K_3", label="[3] Leave it alone", action=self.hero.retreat)
        )
        self.add_menu(
            Menu(
                title=title,
                subtitle="What next?",
                entries=entries,
                cancel=self.hero.retreat,
            )
        )

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
