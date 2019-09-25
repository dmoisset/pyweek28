from wasabi2d import keys, Scene
from wasabi2d.constants import keymods

import game
import world
from views.room import RoomView
from views.hero import HeroView


class MapController:
    def __init__(self) -> None:
        self.game = game.Game()

    def activate(self, scene: Scene) -> None:
        self.scene = scene
        scene.camera.pos = (0, 0)
        self.show_map()
        self.show_hero()

    def deactivate(self, scene: Scene) -> None:
        pass

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
        elif key == keys.S:
            self.game.search()
