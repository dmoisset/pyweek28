from typing import Any, cast, List
from typing_extensions import Protocol

from wasabi2d import Scene, run, event, keys, animate
from wasabi2d.constants import keymods

import game
import hero
import world
import observer

# Layers
FLOOR_LAYER = 0
HERO_LAYER = 10

# Dimension
ROOM_SPACING = 80
ROOM_SIZE = 72
DOORWAY_SIZE = ROOM_SIZE - 2


class RoomView:
    FLOOR_COLOR = ["#55555500", "#55555580", "#555555ff"]

    def __init__(self, scene: Scene, room: world.Room) -> None:
        floor = scene.layers[FLOOR_LAYER]
        self.room = room
        self.floor = floor.add_rect(
            width=ROOM_SIZE, height=ROOM_SIZE, fill=True, color=self.FLOOR_COLOR[0]
        )
        self.floor.pos = (room.x * ROOM_SPACING, room.y * ROOM_SPACING)
        self.east_doorway = self.south_doorway = None
        if world.Direction.EAST in room.neighbors:
            self.east_doorway = floor.add_rect(
                width=ROOM_SPACING - ROOM_SIZE, height=DOORWAY_SIZE, fill=True
            )
            self.east_doorway.pos = (
                (room.x + 0.5) * ROOM_SPACING,
                room.y * ROOM_SPACING,
            )

        if world.Direction.SOUTH in room.neighbors:
            self.south_doorway = floor.add_rect(
                width=DOORWAY_SIZE, height=ROOM_SPACING - ROOM_SIZE, fill=True
            )
            self.south_doorway.pos = (
                room.x * ROOM_SPACING,
                (room.y + 0.5) * ROOM_SPACING,
            )

        # Initial update
        self.notify(room, {})
        room.register(self)
        if self.east_doorway:
            room.neighbors[world.Direction.EAST].register(self)
        if self.south_doorway:
            room.neighbors[world.Direction.SOUTH].register(self)

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        room = self.room
        # Show/Hide
        self.floor.color = self.FLOOR_COLOR[2 * int(room.seen)]
        if self.east_doorway:
            visible = int(room.seen) + (room.neighbors[world.Direction.EAST].seen)
            self.east_doorway.color = self.FLOOR_COLOR[visible]
        if self.south_doorway:
            visible = int(room.seen) + int(room.neighbors[world.Direction.SOUTH].seen)
            self.south_doorway.color = self.FLOOR_COLOR[visible]


class HeroView:
    def __init__(self, scene: Scene, hero: hero.Hero) -> None:
        self.scene = scene
        self.sprite = scene.layers[HERO_LAYER].add_sprite("hero")
        self.sprite.scale = 0.18
        self.notify(hero, {})
        hero.register(self)

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        pc = cast(hero.Hero, obj)
        animate(self.sprite, pos=(pc.x * ROOM_SPACING, pc.y * ROOM_SPACING))
        animate(
            self.scene.camera,
            duration=0.2,
            pos=(pc.x * ROOM_SPACING, pc.y * ROOM_SPACING),
        )


class Controller(Protocol):
    scene: Scene

    def activate(self, scene: Scene) -> None:
        ...

    def on_key_up(self, key: keys, mod: keymods) -> None:
        ...


class MapController:
    def __init__(self) -> None:
        self.game = game.Game()

    def activate(self, scene: Scene) -> None:
        self.scene = scene
        self.scene.camera.pos = (0, 0)
        self.show_map()
        self.show_hero()

    def show_map(self) -> None:
        shown_rooms = set()
        level = self.game.hero.room.level
        pending_rooms = [level.entrance]
        while pending_rooms:
            room = pending_rooms.pop(-1)
            shown_rooms.add(room)
            RoomView(self.scene, room)

            for n in room.neighbors.values():
                if n not in shown_rooms:
                    pending_rooms.append(n)

    def show_hero(self) -> None:
        HeroView(self.scene, self.game.hero)

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key == keys.RIGHT:
            self.game.move(world.Direction.EAST)
        elif key == keys.UP:
            self.game.move(world.Direction.NORTH)
        elif key == keys.LEFT:
            self.game.move(world.Direction.WEST)
        elif key == keys.DOWN:
            self.game.move(world.Direction.SOUTH)


class EventManager:

    stack: List[Controller]

    def __init__(self) -> None:
        self.scene = Scene()
        self.stack = []

    def push(self, c: Controller) -> None:
        c.activate(self.scene)
        self.stack.append(c)

    def pop(self) -> None:
        del self.stack[-1]

    def update(self, keyboard: Any) -> None:
        observer.dispatch_events()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        self.stack[-1].on_key_up(key, mod)

    def run(self) -> None:
        assert self.stack, "Nothing to do, no controllers set up"
        event(self.update)
        event(self.on_key_up)
        run()


UI = EventManager()
