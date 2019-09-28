from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Tuple, NamedTuple
import random

import game


class ItemSlot(Enum):
    NONE = ""
    BOOTS = "boots"
    HEADGEAR = "headgear"
    CLOAK = "cloak"


@dataclass
class ItemKind:
    id: str
    name: str
    description: str
    frequency: int = 4  # 4 is very common, 1 is rarest
    slot: ItemSlot = ItemSlot.NONE
    from_inventory: str = ""


KINDS = [
    ItemKind(
        "pot",
        name="Healing Potion",
        description="Increases your current hit points",
        from_inventory="Takes away some of your damage",
    ),
    ItemKind(
        "key.wood",
        name="Wooden Key",
        description="Automatically opens wooden doors",
        frequency=3,
    ),
    ItemKind(
        "boots.escape",
        name="Boots of Escaping",
        description="Improves your chances of escaping a monster by 20%",
        frequency=2,
        slot=ItemSlot.BOOTS,
    ),
]

KINDS_BY_ID = {k.id: k for k in KINDS}


def random_kind() -> ItemKind:
    weighted_list: List[ItemKind] = []
    for k in KINDS:
        weighted_list += [k] * k.frequency
    return random.choice(weighted_list)


class Item:
    kind: ItemKind
    amount: int = 1

    def __init__(self, kind_id: str):
        self.kind = KINDS_BY_ID[kind_id]

    @classmethod
    def random(cls) -> "Item":
        self: Item = object.__new__(cls)
        self.kind = random_kind()
        return self


def item_sort(i: Item) -> Tuple[str, str]:
    """Key for sorting items"""
    group = i.kind.slot.value or "~"  # Send non slotted items to the bottom
    return (group, i.kind.id)


def use_from_inventory(g: "game.Game", item: Item) -> None:
    assert item.kind.from_inventory
    assert item.amount > 0
    assert item in g.hero.inventory

    if item.kind.id == "pot":
        g.hero.heal(5)
        item.amount -= 1
    else:
        raise ValueError(f"Item kind [{item.kind.id}] not implemented yet!")
    g.hero.clean_inventory()


# Item abilities
class Option(NamedTuple):
    title: str
    subtitle: str
    action: Callable[[], None]


def door_options(g: "game.Game", item: Item) -> Iterable[Option]:
    assert g.hero.room.door is not None
    if item.kind.id == "key.wood":
        yield Option(
            "Unlock with your wooden key",
            "This discards the key but ensures the door is opened. Triggers traps.",
            action=lambda: g.unlock_door(item),
        )
