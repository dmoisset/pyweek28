from enum import Enum
import random
from typing import Iterator, List, Optional

from wasabi2d import sounds

import hero
from observer import Observable, Message
from menu import Menu, MenuItem
from world import World, Direction, Level
import treasure
from util import roll


class DamageType(Enum):
    FIRE = "fire"
    ICE = "ice"
    PHYSICAL = "physical"


class MenuID(Enum):
    DOOR = "door"
    MONSTER = "monster"
    TRAP = "trap"


SEARCH_TIME = 1
MOVE_TIME = 1
BREAK_TIME = 3
UNLOCK_TIME = 1
FIGHT_TIME = 2
ESCAPE_TIME = 1
DISARM_TIME = 4
REST_TIME = 96


def key_iterator() -> Iterator[str]:
    """Return an iterable on optional keys"""
    return iter(
        "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    )  # 'I' skipped for people coming from inventory


class Game(Observable):

    OBSERVABLE_FIELDS = {"time", "win", "current_level"}

    hero: hero.Hero
    world: World
    current_level: Level

    _time: int = 0
    MAX_TIME: int = 24 * 12 * 7  # 7 Days time limit

    win: Optional[bool] = None  # True when win, False when lost

    _events: List[Menu]

    def __init__(self) -> None:
        super().__init__()
        self.world = World()
        self.hero = hero.Hero(self.world)
        self.current_level = self.hero.room.level
        self.hero.register(self)  # Look for the hero status
        self._events = []
        self.look()

    @property
    def time(self) -> int:
        return self._time

    @time.setter
    def time(self, value: int) -> None:
        self._time = value
        if value >= self.MAX_TIME:
            # You lost!
            self.win = False

    def notify(self, obj: Observable, msg: Message) -> None:
        if obj is self.hero and self.hero.hit_points == 0:
            # You lost!
            self.win = False

    def add_message(self, message: str, subtitle: str = "") -> None:
        if self.win is not None:
            # no need for extra messages
            return
        self._events.append(Menu(title=message, subtitle=subtitle))
        self.request_notify({"events": self._events})

    def add_menu(self, menu: Menu) -> None:
        if self.win is not None:
            # no need for extra menus
            return
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

    def extend(self, entries: List[MenuItem], menu: MenuID) -> None:
        """Add extra options"""
        shortcut = key_iterator()
        # Extend with inventory items
        for item in self.hero.inventory:
            if menu == MenuID.DOOR:
                options = treasure.door_options(self, item)
            elif menu == MenuID.MONSTER:
                options = treasure.monster_options(self, item)
            else:
                options = ()
            for t, st, a in options:
                k = next(shortcut)
                entries.append(
                    MenuItem(
                        key=k, label=f"[{k}] {t}", subtitle=st, action=a, color="green"
                    )
                )

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
            self.hero.enter(new_room)
            self.look()
            self.visit_room()

    def visit_room(self, **kwargs: str) -> None:
        """Trigger actions when reentering a room"""
        room = self.hero.room
        if room.monster:
            self.monster_encounter()
        elif room.is_entrance():
            self.visit_entrance()
        elif room.is_exit():
            self.visit_exit()
        elif room.door:
            self.visit_door(**kwargs)
        elif room.trap:
            self.visit_trap(**kwargs)
        elif room.loot:
            self.visit_treasure()

    def hero_level_up(self, level: int) -> None:
        increases_left = 2

        def powerup(ability: str) -> None:
            nonlocal increases_left
            s = getattr(self.hero, ability)
            s.score += 2
            setattr(self.hero, ability, s)
            increases_left -= 1
            if increases_left:
                self.add_menu(
                    Menu(
                        title=f"You still have {increases_left} ability "
                        f"increase{'s'*(increases_left != 1)}",
                        subtitle=f"You can increase the same ability multiple times",
                        entries=entries,
                    )
                )

        if level > self.hero.level:
            diff = level - self.hero.level
            self.hero.level = level
            entries = [
                MenuItem(
                    key="K_1",
                    label="[1] Increase strength",
                    subtitle="Improve 5% your effectiveness at combat and breaking doors",
                    action=lambda: powerup("strength"),
                ),
                MenuItem(
                    key="K_2",
                    label="[2] Increase agility",
                    subtitle="Improve 5% your chance of escaping and disarming traps",
                    action=lambda: powerup("agility"),
                ),
                MenuItem(
                    key="K_3",
                    label="[3] Increase health",
                    subtitle="Gives you an extra hit point per level",
                    action=lambda: powerup("health"),
                ),
                MenuItem(
                    key="K_4",
                    label="[4] Increase awareness",
                    subtitle="Improve 5% your chance of detecting traps and secret doors",
                    action=lambda: powerup("awareness"),
                ),
            ]
            self.add_menu(
                Menu(
                    title=f"You have gained {diff} level{'' if diff == 1 else 's'}!",
                    subtitle=f"You can increase {increases_left} of your abilities",
                    entries=entries,
                )
            )

    # Stairs

    def visit_entrance(self) -> None:
        below = self.world.level_below(self.current_level)
        if below is not None:
            entries = [
                MenuItem(
                    key="K_1",
                    label="[1] Yes, go down",
                    action=lambda: self.go_to_level(below, enter=False),  # type: ignore
                ),
                MenuItem(key="K_2", label="[2] Stay here", action=lambda: None),
            ]
            self.add_menu(
                Menu(
                    title=f"The stairs go down to floor {self.world.level_number(below)+1}",
                    subtitle="Go down?",
                    entries=entries,
                )
            )

    def visit_exit(self) -> None:
        above = self.world.level_above(self.current_level)
        if above is not None:
            entries = [
                MenuItem(
                    key="K_1",
                    label="[1] Yes, go up",
                    action=lambda: self.go_to_level(above, enter=True),  # type: ignore
                ),
                MenuItem(key="K_2", label="[2] Stay here", action=lambda: None),
            ]
            self.add_menu(
                Menu(
                    title=f"The stairs go up to floor {self.world.level_number(above)+1}",
                    subtitle="Go up?",
                    entries=entries,
                )
            )
        else:
            self.win = True

    def go_to_level(self, new_level: Level, enter: bool) -> None:
        self.time += MOVE_TIME
        self.current_level = new_level
        self.hero.room = new_level.entrance if enter else new_level.exit
        self.hero_level_up(self.world.level_number(new_level) + 1)
        self.look()

    # Monsters

    def monster_encounter(self) -> None:
        assert self.hero.room.monster

        entries = [
            MenuItem(
                key="K_1",
                label="[1] Chaaaaarge!",
                subtitle="The monster dies, but may hurt you.",
                action=self.fight,
            ),
            MenuItem(
                key="K_2",
                label="[2] Try to escape",
                subtitle="You retreat, but the monster may hurt you.",
                action=self.escape,
            ),
        ]
        self.extend(entries, MenuID.MONSTER)
        self.add_menu(
            Menu(
                title="There is a monster here!",
                subtitle="What next?",
                entries=entries,
                cancel=self.escape,
            )
        )

    def fight(self, bonus: int = 0) -> None:
        assert self.hero.room.monster
        monster = self.hero.room.monster

        self.time += FIGHT_TIME
        check = self.hero.strength.bonus + roll() + bonus
        if check >= monster.ac:
            if bonus == 0:  # FIXME: this shouldn't know about the boots
                sounds.fight.play()
            else:
                sounds.kungfu.play()
            if random.random() <= monster.drop_rate:
                self.hero.room.loot = treasure.Item.random()
                self.visit_treasure("The monster dies and drops a {}")
            else:
                self.add_message("You defeat the monster!")
        else:
            sounds.roar.play()
            monster.attack(self)
        self.hero.room.monster = None

    def escape(self, bonus: int = 0) -> None:
        assert self.hero.room.monster
        monster = self.hero.room.monster
        self.time += ESCAPE_TIME
        check = self.hero.agility.bonus + roll() + bonus
        if check < monster.escape_dc:
            sounds.roar.play()
            monster.attack(self)
        self.hero.retreat()

    # Doors

    def visit_door(self, title: str = "There is a door here") -> None:
        entries = [
            MenuItem(
                key="K_1",
                label="[1] Break it",
                subtitle="If the door is trapped, this will trigger the trap",
                action=self.break_door,
            )
        ]
        if self.hero.room.trap is None or self.hero.room.trap.hide_dc > 0:
            entries.append(
                MenuItem(
                    key="K_2", label="[2] Check it for traps", action=self.search_traps
                )
            )
        else:
            entries.append(
                MenuItem(
                    key="K_2",
                    label="[2] Disarm trap",
                    subtitle="Failure will trigger the trap",
                    action=self.disarm_trap,
                )
            )
        entries.append(
            MenuItem(key="K_3", label="[3] Leave it alone", action=self.hero.retreat)
        )
        self.extend(entries, MenuID.DOOR)
        self.add_menu(
            Menu(
                title=title,
                subtitle="What next?",
                entries=entries,
                cancel=self.hero.retreat,
            )
        )

    def break_door(self, bonus: int = 0) -> None:
        self.time += BREAK_TIME
        check = self.hero.strength.bonus + roll() + bonus
        assert self.hero.room.door
        sounds.force.play()
        if check >= self.hero.room.door.break_dc:
            self.hero.room.door = None
            if self.hero.room.trap:
                self.trigger_trap("As the door breaks, a trap within it is triggered!")
                # The trap is destroyed with the door
                self.hero.room.trap = None
            else:
                self.add_message("Crash! the door opens!")
        else:
            if self.hero.room.trap:
                self.trigger_trap("The door was trapped! you triggered it!")
                self.visit_door("...and the (trapped) door resists")
            else:
                self.visit_door("WHAAAM! The door resists...")
        self.look()

    def unlock_door(self, key: treasure.Item) -> None:
        self.time += UNLOCK_TIME
        self.hero.room.door = None
        sounds.unlock.play()
        if self.hero.room.trap:
            self.trigger_trap("As the door unlocks, a trap within it is triggered!")
            # The trap is destroyed with the door
            self.hero.room.trap = None
        else:
            self.add_message("Click! the door opens!")
        key.amount -= 1
        self.hero.clean_inventory()
        self.look()

    def search_traps(self) -> None:
        """Search for traps within door"""
        self.time += SEARCH_TIME
        check = self.hero.awareness.bonus + roll()
        self.hero.room.reveal_traps(check)
        self.look()
        if self.hero.room.trap is None or self.hero.room.trap.hide_dc > 0:
            self.visit_room(title="Doesn't seem to be trapped...")
        else:
            self.visit_room(title="It's a trap!")

    # Traps

    def disarm_trap(self) -> None:
        assert self.hero.room.trap
        assert self.hero.room.trap.hide_dc == 0

        self.time += DISARM_TIME
        trap = self.hero.room.trap
        check = self.hero.agility.bonus + roll()
        if check >= trap.disarm_dc:
            self.add_message("You disarm it!")
            self.hero.room.trap = None
            self.visit_room()
            sounds.disarm.play()
        elif check >= trap.disarm_dc // 2:
            self.visit_room(title="This seems difficult to disarm...")
        else:
            self.trigger_trap("You triggered the trap trying to disarm it!")
            self.visit_room()

    def trigger_trap(self, title: str = "You stepped on a trap!") -> None:
        assert self.hero.room.trap

        trap = self.hero.room.trap
        self.add_message(title)
        trap.reveal()
        self.hero.take_damage(1, DamageType.PHYSICAL)

    def visit_trap(self, title: str = "You get carefully closer to the trap") -> None:
        assert self.hero.room.trap

        trap = self.hero.room.trap
        if trap.hide_dc != 0:
            self.trigger_trap()
        else:
            entries = [
                MenuItem(key="K_1", label="[1] Retreat", action=self.hero.retreat),
                MenuItem(
                    key="K_2",
                    label="[2] Disarm trap",
                    subtitle="Failure MAY trigger the trap",
                    action=self.disarm_trap,
                ),
                MenuItem(
                    key="K_3",
                    label="[3] Walk through trap",
                    subtitle="Will trigger the trap, but you'll be able to walk past",
                    action=self.trigger_trap,
                ),
            ]
            self.add_menu(
                Menu(
                    title=title,
                    subtitle="What next?",
                    entries=entries,
                    cancel=self.hero.retreat,
                )
            )

    # Loot

    def visit_treasure(self, title: str = "There is a {} here") -> None:
        assert self.hero.room.loot

        item = self.hero.room.loot

        drop = self.hero.check_pick_up()
        if drop:
            if drop.kind is item.kind:
                self.add_message(f"The {item.kind.name} here are exactly like yours.")
                return
            else:
                subtitle = f"You will have to drop your {drop.kind.name}"
        else:
            subtitle = ""

        entries = [
            MenuItem(
                key="K_1",
                label="[1] Pick it up",
                subtitle=subtitle,
                action=self.hero.pick_up,
            ),
            MenuItem(key="K_2", label="[2] Leave it", action=lambda: None),
        ]
        self.add_menu(
            Menu(
                title=title.format(item.kind.name),
                subtitle=item.kind.description,
                entries=entries,
            )
        )

    # Other actions

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
        self.add_message("Nothing like some sleep to feel better...")

    def inventory(self) -> None:
        entries = []
        key = key_iterator()
        for i in self.hero.inventory:
            n = f"{i.amount}×" if i.amount != 1 else ""
            if i.kind.from_inventory:
                k = next(key)
                entries.append(
                    MenuItem(
                        key=k,
                        label=f"[{k}] {n}{i.kind.name}",
                        subtitle=i.kind.from_inventory,
                        action=lambda i=i: treasure.use_from_inventory(  # type: ignore
                            self, i
                        ),
                    )
                )
            else:
                entries.append(
                    MenuItem(key="UNKNOWN", label=n + i.kind.name, action=lambda: None)
                )
        subtitle = "You have no items on yourself" if not self.hero.inventory else ""
        self.add_menu(Menu(title="Inventory", subtitle=subtitle, entries=entries))
