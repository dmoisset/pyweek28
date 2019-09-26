from typing import cast

from wasabi2d import Scene

import game
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
    def __init__(self, scene: Scene, game: game.Game) -> None:
        self.scene = scene
        self.time_label = scene.hudlayers[1].add_label(
            "<Time>", pos=(30, SCREEN_HEIGHT - 30)
        )
        game.register(self)
        self.notify(game, {})

    def notify(self, obj: observer.Observable, message: observer.Message) -> None:
        g = cast(game.Game, obj)
        self.time_label.text = convert_time(g.time)
