from typing import Any

from wasabi2d import keys, Scene
from wasabi2d.constants import keymods

from menu import Menu
from ui import UI
from views.layer_ids import DIALOG_LAYER

MENU_WIDTH = 500
ENTRY_HEIGHT = 40


class MenuController:
    def __init__(self, menu: Menu, offset: int = 0):
        self.menu = menu
        self.action_map = {keys[e.key]: e.action for e in menu.entries}  # type: ignore
        self.action_map[keys.ESCAPE] = menu.cancel  # type: ignore
        self.layer = DIALOG_LAYER + offset
        self.layerhack = [float(self.layer)]

    def add_label(self, scene: Scene, text: str, **kwargs: Any) -> Any:
        new_layer = self.layerhack[-1] + 1 / 128
        self.layerhack.append(new_layer)
        scene.hudlayers[new_layer].add_label(text, **kwargs)

    def activate(self, scene: Scene) -> None:
        layer = scene.hudlayers[self.layer]
        height = 100 + ENTRY_HEIGHT * len(self.menu.entries)
        cx, cy = 600, 50 + height / 2
        layer.add_rect(width=MENU_WIDTH, height=height, color="#0000aaff", pos=(cx, cy))
        top = cy - height / 2
        left = cx - MENU_WIDTH / 2
        self.add_label(scene, self.menu.title, align="center", pos=(cx, top + 40))
        self.add_label(
            scene,
            self.menu.subtitle,
            fontsize=14,
            align="center",
            pos=(cx, top + 60),
            color="#aaaaaa",
        )
        for i, e in enumerate(self.menu.entries):
            self.add_label(
                scene,
                e.label,
                pos=(left + 20, top + 100 + i * ENTRY_HEIGHT),
                color=e.color,
            )
            if e.subtitle:
                self.add_label(
                    scene,
                    e.subtitle,
                    fontsize=14,
                    pos=(left + 60, top + 100 + i * ENTRY_HEIGHT + 16),
                    color="#aaaaaa",
                )

    def deactivate(self, scene: Scene) -> None:
        # scene.hudlayers[self.layer].clear()
        for l in self.layerhack:
            scene.hudlayers[l].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key in self.action_map:
            self.action_map[key]()
            UI.pop()
