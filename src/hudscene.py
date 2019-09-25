from typing import Any

from wasabi2d import Scene
from wasabi2d.scene import Camera, LayerGroup


class HUDScene(Scene):  # type: ignore
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.hudcamera = Camera(self.ctx, self.width, self.height)
        self.hudlayers = LayerGroup(self.ctx, self.hudcamera)

    def draw(self, t: float, dt: float) -> None:
        # Copied code instead of calling super() to avoid performance drop
        assert len(self.background) == 3, "Scene.background must be a 3-element tuple."
        if self._recording:
            self._vid_frame()
        self.ctx.clear(*self.background)
        self.layers.render(self.camera.proj, t, dt)
        self.hudlayers.render(self.hudcamera.proj, t, dt)
