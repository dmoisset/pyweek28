import math
from typing import cast, Optional

from wasabi2d import animate
from wasabi2d.primitives import polygons

import hero
from hudscene import HUDScene
import observer
from views.layer_ids import HERO_LAYER
from views.dimensions import ROOM_SPACING, SCREEN_WIDTH, SCREEN_HEIGHT

HURT_LAYER = 10


class HeroView:
    """View for the hero token on the map"""

    def __init__(self, scene: HUDScene, hero: hero.Hero) -> None:
        self.scene = scene
        self.sprite = scene.layers[HERO_LAYER].add_sprite("hero")
        self.sprite.scale = 0.18
        self.hurt = scene.hudlayers[HURT_LAYER].add_particle_group(
            texture="hurt", max_age=1
        )
        for i in range(11):
            self.hurt.add_color_stop(i * 0.1, (1, 1, 1, i % 2))

        self.prev_damage = hero.damage
        self.notify(hero, {})
        hero.register(self)

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        pc = cast(hero.Hero, obj)
        target = (pc.x * ROOM_SPACING, pc.y * ROOM_SPACING)
        animate(self.sprite, pos=target)
        animate(self.scene.camera, duration=0.2, pos=target)
        if pc.damage > self.prev_damage:
            self.hurt.emit(
                1,
                pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                vel_spread=5,
                size=30,
                angle=math.pi,
            )
        self.prev_damage = pc.damage


HP_METER_WIDTH = 110
HP_METER_HEIGHT = 20
HP_METER_POS = (100, 115)

HP_METER_LAYER = 0

STAT_LAYER = 0
STAT_POS = (20, 315)


class HitPointView:
    def __init__(self, scene: HUDScene, hero: hero.Hero) -> None:
        self.below = scene.hudlayers[HP_METER_LAYER]

        above = scene.hudlayers[HP_METER_LAYER + 2]
        above.add_rect(
            width=HP_METER_WIDTH, height=HP_METER_HEIGHT, pos=HP_METER_POS, fill=False
        )
        self.counter = above.add_label(
            "0/0",
            align="center",
            fontsize=HP_METER_HEIGHT * 0.7,
            pos=HP_METER_POS,
            color="#ffffff",
        )
        self.counter.y += HP_METER_HEIGHT * 0.3
        self.meter: Optional[polygons.Rect] = None

        hero.register(self)
        self.notify(hero, {})

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        pc = cast(hero.Hero, obj)
        self.counter.text = f"{pc.hit_points}/{pc.max_hit_points}"
        if self.meter:
            self.meter.delete()
        ratio = pc.hit_points / pc.max_hit_points
        width = HP_METER_WIDTH * ratio
        if ratio <= 0.25:
            color = (0.75, 0.0, 0.0)
        elif ratio <= 0.75:
            color = (0.75, 1.5 * (ratio - 0.25), 0)
        else:
            color = ((1 - ratio) * 3, 0.75, 0)
        self.meter = self.below.add_rect(
            width=width,
            height=HP_METER_HEIGHT,
            pos=(HP_METER_POS[0] - (HP_METER_WIDTH - width) / 2, HP_METER_POS[1]),
            color=color,
        )


class StatsView:
    def __init__(self, scene: HUDScene, hero: hero.Hero) -> None:
        layer = scene.hudlayers[HP_METER_LAYER]

        self.label = layer.add_label("", pos=STAT_POS, fontsize=16, color="#cccccc")

        hero.register(self)
        self.notify(hero, {})

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        pc: hero.Hero = cast(hero.Hero, obj)
        t = [
            f"Character Level: {pc.level}",
            f"Strength: +{pc.strength.bonus}",
            f"Agility: +{pc.agility.bonus}",
            f"Health: +{pc.health.bonus}",
            f"Awareness: +{pc.awareness.bonus}",
        ]
        self.label.text = "\n".join(t)
