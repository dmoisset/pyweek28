from wasabi2d import keys, keymods, music

from controllers.map import MapController
from hudscene import HUDScene
from ui import UI

intro_text = [
    """
No one could stop the dragon, and now
he is ruling your beloved city. A
seasoned adventurer like you knows
that he will get bored and devour
everyone in a few days. But a seasoned
adventurer like you knows there is
nothing that can harm the monster
except for an enchanted dragon-slaying
arrow.""",
    """
Nobody has seen one of those in ages.
It is said that the wizard kept one
in his tower nearby... but he died a
century ago. Others have tried to get
into the building just to escape with
reports of deadly traps and monsters.""",
    """But there is no choice now but face
the dangers within if you are to slay the
evil dragon. The time is running out and
the path will certainly be filled with
peril. It's not an accident that this
place is called...

THE SPIRE OF CHAOS""",
    "You have a week, adventurer.",
]

intro_images = ["intro_bg", "intro_bg_2", "intro_bg_2", None]
intro_pos_x = [900, 300, 300, 600]
intro_pos_y = [200, 240, 240, 350]


class IntroController:
    def __init__(self, stage: int = 0) -> None:
        self.stage = stage
        if stage == 0:
            music.play_once("intro")

    def activate(self, scene: HUDScene) -> None:
        size = 20
        text = intro_text[self.stage]
        x = intro_pos_x[self.stage]
        y = intro_pos_y[self.stage]

        if intro_images[self.stage]:
            scene.layers[0].add_sprite(intro_images[self.stage], pos=scene.camera.pos)
            scroll = scene.layers[0].add_sprite("scroll", pos=(x, 330))
            scroll.scale = 0.9
            color = "black"
        else:
            color = "white"
        scene.layers[0].add_label(
            text, align="center", pos=(x, y), color=color, fontsize=size
        )
        scene.layers[0].add_label(
            "(press SPACE to continue)",
            align="center",
            pos=(x, 500),
            color="black",
            fontsize=14,
        )

    def deactivate(self, scene: HUDScene) -> None:
        scene.layers[0].clear()

    def on_key_down(self, key: keys, mod: keymods) -> None:
        if key in (keys.ESCAPE, keys.SPACE):
            next_stage = self.stage + 1
            if next_stage == len(intro_text):
                UI.replace(self, MapController())
            else:
                UI.replace(self, IntroController(next_stage))
