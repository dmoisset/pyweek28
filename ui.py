from typing import Any, cast

from wasabi2d import Scene, run, event, keys
from wasabi2d.constants import keymods

import game
import world
import observer

# Layers
FLOOR_LAYER = 0

# Dimension
ROOM_SPACING = 40
ROOM_SIZE = 36


class RoomView:
    def __init__(self, scene: Scene, room: world.Room) -> None:
        self.floor = scene.layers[FLOOR_LAYER].add_rect(
            width=ROOM_SIZE, height=ROOM_SIZE, fill=True, color="#555555"
        )
        self.floor.pos = (room.x * ROOM_SPACING, room.y * ROOM_SPACING)

        # Initial update
        self.notify(room, {})
        room.register(self)

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        room = cast(world.Room, obj)
        # Show/Hide
        self.floor.scale = int(room.seen)


class UI:
    def __init__(self) -> None:
        self.scene = Scene()
        self.scene.camera.pos = (0, 0)
        self.game = game.Game()
        self.show_map()

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

    def update(self, keyboard: Any) -> None:
        observer.dispatch_events()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key == keys.RIGHT:
            self.game.move(world.Direction.EAST)
        elif key == keys.UP:
            self.game.move(world.Direction.NORTH)
        elif key == keys.LEFT:
            self.game.move(world.Direction.WEST)
        elif key == keys.DOWN:
            self.game.move(world.Direction.SOUTH)

    def run(self) -> None:
        event(self.update)
        event(self.on_key_up)
        run()
