from enum import Enum
import random

import game
import treasure


class TrapKind(Enum):
    ROCK = "rock"  # A rock falls from the ceiling and deals damage
    SPIKED_PIT = "pit"  # fall in pit; take damage, lose time
    WEB = "web"  # Entangled, lose time
    ACID = "acid"  # Pool of acid. Either dissolves boots or applies damage


ESCAPE_TIMES = {TrapKind.SPIKED_PIT: 2, TrapKind.WEB: 12}

DAMAGE = {TrapKind.SPIKED_PIT: 1, TrapKind.ROCK: 2}

NAMES = {
    TrapKind.SPIKED_PIT: "spiked pit",
    TrapKind.WEB: "sticky web",
    TrapKind.ROCK: "falling rock trap",
    TrapKind.ACID: "pool of acid",
}

FREQUENCIES = {TrapKind.SPIKED_PIT: 2, TrapKind.ROCK: 2}


class Trap:
    hide_dc: int = 12  # Difficulty of finding if hidden. 0 if found or not hidden
    disarm_dc: int = 15

    kind: TrapKind

    def __init__(self) -> None:
        selection = []
        for k in TrapKind:
            selection += [k] * FREQUENCIES.get(k, 1)
        self.kind = random.choice(selection)

    def trigger(self, g: "game.Game") -> None:
        g.hero.take_damage(DAMAGE.get(self.kind, 0), game.DamageType.PHYSICAL)
        g.time += ESCAPE_TIMES.get(self.kind, 0)
        if self.kind == TrapKind.ACID:
            boots = g.hero.worn.get(treasure.ItemSlot.BOOTS, None)
            if boots:
                boots.amount -= 1
                g.hero.clean_inventory()
            else:
                g.hero.take_damage(2, game.DamageType.PHYSICAL)

    def description(self, g: "game.Game") -> str:
        if self.kind == TrapKind.ROCK:
            return "A trapdoor drops a rock on your head. It hurts."
        elif self.kind == TrapKind.SPIKED_PIT:
            return "The fall is painful, and it takes some time to get out"
        elif self.kind == TrapKind.WEB:
            return "You spend a long time unsticking yourself"
        elif self.kind == TrapKind.ACID:
            if g.hero.worn.get(treasure.ItemSlot.BOOTS, None):
                return "Your boots dissolve, they are completely ruined"
            else:
                return "With no protective shoes, your feet are hurt"
        else:
            raise NotImplementedError  # We forgot to describe a trap kind

    @property
    def name(self) -> str:
        return NAMES[self.kind]

    def reveal(self) -> None:
        self.hide_dc = 0
