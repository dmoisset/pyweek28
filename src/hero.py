from typing import Dict, List, Optional, Set, Tuple

import game
import observer
import treasure
from world import World, Room


class Stat:
    score: int = 0
    damage: int = 0

    def __init__(self, score: int = 0) -> None:
        self.score = score

    @property
    def bonus(self) -> int:
        """Bonus to dice rolls when using this ability"""
        return (self.score - self.damage) // 2

    def heal(self) -> None:
        self.damage = 0


class Hero(observer.Observable):

    OBSERVABLE_FIELDS = {
        "room",
        "max_hit_points",
        "damage",
        "level",
        "strength",
        "agility",
        "health",
        "awareness",
    }
    OBSERVABLE_PROPERTIES = {
        "room": ("x", "y"),
        "max_hit_points": ("hit_points",),
        "damage": ("hit_points",),
    }

    level: int = 1

    strength: Stat
    agility: Stat
    health: Stat
    awareness: Stat
    power: Stat

    room: Room
    previous_room: Optional[Room] = None

    damage: int = 0
    resistances: Set["game.DamageType"]

    inventory: List[treasure.Item]
    worn: Dict[treasure.ItemSlot, treasure.Item]

    def __init__(self, world: World) -> None:
        super().__init__()
        self.strength = Stat(score=6)
        self.agility = Stat(score=2)
        self.health = Stat()
        self.awareness = Stat()
        self.power = Stat()

        self.room = world.levels[0].entrance
        self.resistances = set()

        self.inventory = []
        self.worn = {}

    def stats(self) -> Tuple[Stat, ...]:
        return (self.strength, self.agility, self.health, self.awareness, self.power)

    @property
    def max_hit_points(self) -> int:
        return 7 + (5 + self.health.bonus) * self.level

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

    def heal(self, amount: int) -> None:
        self.damage = max(0, self.damage - amount)

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

    def check_pick_up(self) -> Optional[treasure.Item]:
        assert self.room.loot

        item = self.room.loot
        if item.kind.slot != treasure.ItemSlot.NONE:
            return self.worn.get(item.kind.slot, None)
        else:
            return None

    def pick_up(self) -> None:
        """add `item` from current room to inventory. May drop another"""
        assert self.room.loot

        item = self.room.loot
        self.inventory.append(item)
        self.room.loot = None
        if item.kind.slot != treasure.ItemSlot.NONE:
            # Drop item in slot
            dropped = self.worn.get(item.kind.slot, None)
            self.worn[item.kind.slot] = item
            if dropped:
                self.inventory.remove(dropped)
                self.room.loot = dropped
        self.clean_inventory()

    def clean_inventory(self) -> None:
        # Remove expended items
        new_inventory = [i for i in self.inventory if i.amount > 0]
        # Sort in inventory order (grouping similar stuff together)
        new_inventory.sort(key=treasure.item_sort)
        # Merge stacks of identical items
        i = 0
        while i < len(new_inventory) - 1:
            if new_inventory[i].kind == new_inventory[i + 1].kind:
                new_inventory[i].amount += new_inventory[i + 1].amount
                del new_inventory[i + 1]
            else:
                i += 1
        # Remove worn stuff which is not in inventory
        for slot in list(self.worn.keys()):
            if self.worn[slot] not in new_inventory:
                del self.worn[slot]
        # Update
        self.inventory = new_inventory
