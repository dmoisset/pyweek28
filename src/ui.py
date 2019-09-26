import os
from typing import Any, List
from typing_extensions import Protocol

from wasabi2d import run, event, keys, keymods
from wasabi2d import game

import observer
from hudscene import HUDScene
from views.dimensions import SCREEN_WIDTH, SCREEN_HEIGHT


class Controller(Protocol):
    def activate(self, scene: HUDScene) -> None:
        ...

    def deactivate(self, scene: HUDScene) -> None:
        ...

    def on_key_up(self, key: keys, mod: keymods) -> None:
        ...


class EventManager:

    stack: List[Controller]

    def __init__(self) -> None:
        self.scene = HUDScene(
            rootdir=os.environ["RUNNER_DIRECTORY"],
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )
        self.stack = []

    def push(self, c: Controller) -> None:
        c.activate(self.scene)
        self.stack.append(c)

    def pop(self) -> None:
        deactivated = self.stack.pop(-1)
        deactivated.deactivate(self.scene)
        if not self.stack:
            game.exit()

    def replace(self, old: Controller, new: Controller) -> None:
        try:
            i = self.stack.index(old)
        except ValueError:
            # Nothing to replace
            return
        self.stack[i].deactivate(self.scene)
        new.activate(self.scene)
        self.stack[i] = new

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
