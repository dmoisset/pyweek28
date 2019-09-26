import math

from wasabi2d import Scene

import observer
from views.layer_ids import FLOOR_LAYER
from views.dimensions import ROOM_SPACING, ROOM_SIZE, DOORWAY_SIZE
import world


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
        # Door
        self.door = floor.add_sprite("door", pos=self.floor.pos)
        self.door.scale = ROOM_SIZE / 200
        if (
            world.Direction.EAST in room.neighbors
            or world.Direction.WEST in room.neighbors
        ):
            self.door.angle = math.pi / 2

        # Trap
        self.trap = floor.add_sprite("trap", pos=self.floor.pos)
        self.trap.scale = 0.5

        # Monster
        self.monster = floor.add_sprite("monster", pos=self.floor.pos)
        self.monster.scale = 0.15

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
            east_room = room.neighbors[world.Direction.EAST]
            if east_room.visible and room.visible:
                visible = int(room.seen) + int(east_room.seen)
            else:
                visible = 0
            self.east_doorway.color = self.FLOOR_COLOR[visible]
        if self.south_doorway:
            south_room = room.neighbors[world.Direction.SOUTH]
            if south_room.visible and room.visible:
                visible = int(room.seen) + int(south_room.seen)
            else:
                visible = 0
            self.south_doorway.color = self.FLOOR_COLOR[visible]
        # Show door if present
        self.door.color = (1, 1, 1, int(room.seen and room.door is not None))
        # Show trap if present and detected
        self.trap.color = (
            1,
            1,
            1,
            int(room.seen and room.trap is not None and room.trap.hide_dc == 0),
        )
        # Show monster if present
        self.monster.color = (1, 1, 1, int(room.seen and room.monster is not None))
