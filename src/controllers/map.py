from wasabi2d import keys, keymods

from controllers.message import MessageController
from controllers.menu import MenuController
import game
from hudscene import HUDScene
from observer import Observable, Message
from ui import UI, Controller
import world
from views.room import RoomView
from views.game_info import GameInfoView
from views.hero import HeroView, HitPointView


class MapController:
    def __init__(self) -> None:
        self.game = game.Game()
        self.game.register(self)

    def activate(self, scene: HUDScene) -> None:
        self.scene = scene
        scene.camera.pos = (0, 0)
        self.show_map()
        self.show_hero()
        self.show_hud()

    def deactivate(self, scene: HUDScene) -> None:
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

    def show_hud(self) -> None:
        GameInfoView(self.scene, self.game)
        HitPointView(self.scene, self.game.hero)

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
        elif key == keys.R:
            self.game.rest()

    def notify(self, obj: Observable, msg: Message) -> None:
        if "events" in msg:
            # Handle game events
            events = reversed(self.game.pop_events())
            # events are reversed, so most recent ones end up the top of the stack
            # and are processed first by the user
            for i, menu in enumerate(events):
                c: Controller
                if not menu.entries:
                    c = MessageController(f"{menu.title}\n{menu.subtitle}", offset=i)
                else:
                    c = MenuController(menu, offset=i)
                UI.push(c)
        if "win" in msg:
            if self.game.win is not None:
                UI.replace(
                    self,
                    MessageController(
                        "You " + ("win!" if self.game.win else "lose!"), offset=-5
                    ),
                )
