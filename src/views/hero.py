from typing import cast

from wasabi2d import animate, Scene

import hero
import observer
from views.layer_ids import HERO_LAYER
from views.dimensions import ROOM_SPACING


class HeroView:
    def __init__(self, scene: Scene, hero: hero.Hero) -> None:
        self.scene = scene
        self.sprite = scene.layers[HERO_LAYER].add_sprite("hero")
        self.sprite.scale = 0.18
        self.notify(hero, {})
        hero.register(self)

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        pc = cast(hero.Hero, obj)
        animate(self.sprite, pos=(pc.x * ROOM_SPACING, pc.y * ROOM_SPACING))
        animate(
            self.scene.camera,
            duration=0.2,
            pos=(pc.x * ROOM_SPACING, pc.y * ROOM_SPACING),
        )
