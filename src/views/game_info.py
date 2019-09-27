from typing import cast

import game
from hudscene import HUDScene
import observer
from views.dimensions import SCREEN_HEIGHT

MINUTES_PER_TURN = 5


def convert_time(t: int) -> str:
    t *= MINUTES_PER_TURN
    mm = t % 60
    t //= 60
    hh = t % 24
    dd = t // 24
    return f"Day {dd+1}, {hh:02}:{mm:02}"


class GameInfoView:
    def __init__(self, scene: HUDScene, game: game.Game) -> None:
        self.scene = scene
        scene.hudlayers[0].add_sprite("sidebar", pos=(100, 350))
        self.time_label = scene.hudlayers[1].add_label(
            "<Time>", pos=(30, SCREEN_HEIGHT - 50)
        )
        game.register(self)
        self.notify(game, {})

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        g = cast(game.Game, obj)
        level = g.world.level_number(g.hero.room.level) + 1
        nlevels = len(g.world.levels)
        self.time_label.text = f"Level {level}/{nlevels}\n{convert_time(g.time)}"
