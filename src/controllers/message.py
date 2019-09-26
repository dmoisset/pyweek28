from wasabi2d import keys
from wasabi2d import keymods

from hudscene import HUDScene
from ui import UI
from views.layer_ids import DIALOG_LAYER
from views.dimensions import SCREEN_WIDTH

MESSAGE_WIDTH = 600
BOX_COLOR = "#0000aaff"
BORDER_COLOR = "#7777aaff"


class MessageController:
    def __init__(self, text: str, offset: int = 0):
        self.text = text
        self.layer = DIALOG_LAYER + offset

    def activate(self, scene: HUDScene) -> None:
        layer = scene.hudlayers[self.layer]
        cx, cy = SCREEN_WIDTH / 2, 100
        layer.add_rect(width=MESSAGE_WIDTH, height=100, color=BOX_COLOR, pos=(cx, cy))
        layer.add_rect(
            width=MESSAGE_WIDTH,
            height=100,
            color=BORDER_COLOR,
            pos=(cx, cy),
            fill=False,
        )
        layer.add_label(self.text, align="center", pos=(cx, cy + 10))

    def deactivate(self, scene: HUDScene) -> None:
        scene.hudlayers[self.layer].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key in (keys.ESCAPE, keys.SPACE):
            UI.pop()
