from wasabi2d import keys, Scene
from wasabi2d.constants import keymods

from ui import UI


class MessageController:
    def __init__(self, text: str):
        self.text = text

    def activate(self, scene: Scene) -> None:
        layer = scene.layers[100]
        cx, cy = scene.camera.pos
        layer.add_rect(width=500, height=100, color="#0000a0a0", pos=(cx, cy))
        layer.add_label(self.text, align="center", pos=(cx, cy + 10))

    def deactivate(self, scene: Scene) -> None:
        scene.layers[100].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key == keys.ESCAPE:
            UI.pop()
