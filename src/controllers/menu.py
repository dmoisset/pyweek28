from wasabi2d import keys, keymods

from hudscene import HUDScene
from menu import Menu
from ui import UI
from views.layer_ids import DIALOG_LAYER
from views.dimensions import SCREEN_WIDTH

MENU_WIDTH = 500
ENTRY_HEIGHT = 40

BOX_COLOR = "#0000aaff"
BORDER_COLOR = "#7777aaff"


class MenuController:
    def __init__(self, menu: Menu, offset: int = 0):
        self.menu = menu
        self.action_map = {keys[e.key]: e.action for e in menu.entries}  # type: ignore
        self.action_map[keys.ESCAPE] = menu.cancel  # type: ignore
        self.layer = DIALOG_LAYER + offset

    def activate(self, scene: HUDScene) -> None:
        layer = scene.hudlayers[self.layer]
        height = 100 + ENTRY_HEIGHT * len(self.menu.entries)
        cx, cy = SCREEN_WIDTH / 2, 50 + height / 2
        layer.add_rect(width=MENU_WIDTH, height=height, color=BOX_COLOR, pos=(cx, cy))
        layer.add_rect(
            width=MENU_WIDTH,
            height=height,
            color=BORDER_COLOR,
            pos=(cx, cy),
            fill=False,
        )
        top = cy - height / 2
        left = cx - MENU_WIDTH / 2
        layer.add_label(self.menu.title, align="center", pos=(cx, top + 40))
        layer.add_label(
            self.menu.subtitle,
            fontsize=14,
            align="center",
            pos=(cx, top + 60),
            color="#aaaaaa",
        )
        for i, e in enumerate(self.menu.entries):
            layer.add_label(
                e.label,
                fontsize=18,
                pos=(left + 20, top + 100 + i * ENTRY_HEIGHT),
                color=e.color,
            )
            if e.subtitle:
                layer.add_label(
                    e.subtitle,
                    fontsize=14,
                    pos=(left + 60, top + 100 + i * ENTRY_HEIGHT + 16),
                    color="#aaaaaa",
                )

    def deactivate(self, scene: HUDScene) -> None:
        scene.hudlayers[self.layer].clear()

    def on_key_down(self, key: keys, mod: keymods) -> None:
        if key in self.action_map:
            self.action_map[key]()
            UI.pop()
