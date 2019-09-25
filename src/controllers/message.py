from wasabi2d import keys, Scene
from wasabi2d.constants import keymods

from ui import UI
from views.layer_ids import DIALOG_LAYER


class MessageController:
    def __init__(self, text: str, offset: int = 0):
        self.text = text
        self.layer = DIALOG_LAYER + offset

    def activate(self, scene: Scene) -> None:
        layer = scene.hudlayers[self.layer]
        cx, cy = 600, 100
        layer.add_rect(width=500, height=100, color="#0000aaff", pos=(cx, cy))
        layer.add_label(self.text, align="center", pos=(cx, cy + 10))

    def deactivate(self, scene: Scene) -> None:
        scene.hudlayers[self.layer].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key in (keys.ESCAPE, keys.SPACE):
            UI.pop()
