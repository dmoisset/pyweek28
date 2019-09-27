from wasabi2d import keys, keymods

from controllers.map import MapController
from hudscene import HUDScene
from views.dimensions import SCREEN_WIDTH
from ui import UI

intro_text = """No one could stop the dragon, and now he is ruling your beloved city. A
seasoned adventurer like you knows that he will get bored and devour everyone
in a few days. But a seasoned adventurer like you knows there is nothing
that can harm the monster except for an enchanted dragon-slaying arrow.

Nobody has seen one of those in ages. It is said that the wizard kept one in
his tower nearby... but he died a century ago. Others have tried to get into
the building just to escape with reports of deadly traps and monsters. But
there is no choice know, and face the dangers within if you are to slay the
evil dragon. The time is running out and the path will certainly be filled
with peril, it's not an accident that this place is called...

THE SPIRE OF CHAOS

You have a week, adventurer.

(press SPACE to start)"""


class IntroController:
    def activate(self, scene: HUDScene) -> None:
        scene.layers[0].add_sprite("intro_bg", pos=scene.camera.pos)
        scene.layers[0].add_label(
            intro_text, align="center", pos=(SCREEN_WIDTH // 2, 130), color="black"
        )
        scene.layers[0].add_label(
            intro_text, align="center", pos=(SCREEN_WIDTH // 2, 130), color="black"
        )
        scene.layers[0].add_label(
            intro_text, align="center", pos=(SCREEN_WIDTH // 2, 130), color="white"
        )

    def deactivate(self, scene: HUDScene) -> None:
        scene.layers[0].clear()

    def on_key_up(self, key: keys, mod: keymods) -> None:
        if key in (keys.ESCAPE, keys.SPACE):
            UI.replace(self, MapController())
