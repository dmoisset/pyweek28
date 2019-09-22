from typing import Any

from wasabi2d import Scene, run, event

import game

# Layers
FLOOR_LAYER = 0

# Dimension
ROOM_SPACING = 40
ROOM_SIZE = 36


class UI:
    def __init__(self) -> None:
        self.scene = Scene()
        self.scene.camera.pos = (0, 0)
        self.game = game.Game()
        self.show_map()

    def show_map(self) -> None:
        floor = self.scene.layers[FLOOR_LAYER]

        shown_rooms = set()
        level = self.game.hero.room.level
        pending_rooms = [(level.entrance, 0, 0)]
        while pending_rooms:
            room, x, y = pending_rooms.pop(-1)
            shown_rooms.add(room)

            r = floor.add_rect(
                width=ROOM_SIZE, height=ROOM_SIZE, fill=True, color="#555555"
            )
            r.pos = (x * ROOM_SPACING, y * ROOM_SPACING)
            for d, n in room.neighbors.items():
                dx, dy = d.value
                if n not in shown_rooms:
                    pending_rooms.append((n, x + dx, y + dy))

    def update(self, keyboard: Any) -> None:
        pass

    def run(self) -> None:
        event(self.update)
        run()
