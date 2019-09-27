from wasabi2d import keys, keymods

from controllers.map import MapController
from hudscene import HUDScene
from views.dimensions import SCREEN_WIDTH
from ui import UI

intro_text = [
    """No one could stop the dragon, and now he is ruling your beloved city. A
seasoned adventurer like you knows that he will get bored and devour everyone
in a few days. But a seasoned adventurer like you knows there is nothing
that can harm the monster except for an enchanted dragon-slaying arrow.

(press SPACE to continue)""",
    """Nobody has seen one of those in ages. It is said that the wizard kept one in
his tower nearby... but he died a century ago. Others have tried to get into
the building just to escape with reports of deadly traps and monsters. But
there is no choice know, and face the dangers within if you are to slay the
evil dragon. The time is running out and the path will certainly be filled
with peril, it's not an accident that this place is called...


THE SPIRE OF CHAOS

(press SPACE to continue)""",
    "You have a week, adventurer.",
]

intro_images = ["intro_bg", "intro_bg_2", None]


class IntroController:
    def __init__(self, stage=0):
        self.stage = stage

    def activate(self, scene: HUDScene) -> None:
        if intro_images[self.stage]:
            scene.layers[0].add_sprite(intro_images[self.stage], pos=scene.camera.pos)
        text = intro_text[self.stage]
        # Cheap font outline effect: write twice in black, once in white
        h = 350 - text.count("\n") * 18
        scene.layers[0].add_label(
            text, align="center", pos=(SCREEN_WIDTH // 2, h), color="black"
        )
        scene.layers[0].add_label(
            text, align="center", pos=(SCREEN_WIDTH // 2, h), color="black"
        )
        scene.layers[0].add_label(
            text, align="center", pos=(SCREEN_WIDTH // 2, h), color="white"
        )

    def deactivate(self, scene: HUDScene) -> None:
        scene.layers[0].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key in (keys.ESCAPE, keys.SPACE):
            next_stage = self.stage + 1
            if next_stage == len(intro_text):
                UI.replace(self, MapController())
            else:
                UI.replace(self, IntroController(next_stage))
