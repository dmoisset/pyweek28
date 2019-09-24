import os
from typing import Any, List
from typing_extensions import Protocol

from wasabi2d import Scene, run, event, keys
from wasabi2d.constants import keymods

import observer


class Controller(Protocol):
    def activate(self, scene: Scene) -> None:
        ...

    def on_key_up(self, key: keys, mod: keymods) -> None:
        ...


class EventManager:

    stack: List[Controller]

    def __init__(self) -> None:
        self.scene = Scene(rootdir=os.environ["RUNNER_DIRECTORY"])
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
