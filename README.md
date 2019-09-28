# Spire of Chaos

Entry in PyWeek #28  <http://www.pyweek.org/28/>

**Team:** Chaotic Elven Wizard

**Members:** Darni

## DEPENDENCIES

The game was built on python 3.7, should work on python 3.6

You will need to pip install some of these before running the game:

 - wasabi2d: The latest release as of today has some bugs fixed in master.
   please install it with `pip install git+https://github.com/lordmauve/wasabi2d.git@669e0072`.
   Requires also having git in your system
 - `pip install typing_extensions` 
 - `pip install dataclasses` (only if you use python 3.6)

I have tried this on Linux and on Windows

Unfortunately, it won't run on OS X; wasabi2d requires OpenGL 4.3 and Apple
only supports OpenGL 4.1

## RUNNING THE GAME

Open a terminal / command line and "cd" to the game directory and run:

```
  python run_game.py
```

## THE ADVENTURE BEGINS....

No one could stop the dragon, and now he is ruling your beloved city. A
seasoned adventurer like you knows that he will get bored and devour everyone
in a few days. But a seasoned adventurer like you knows there is nothing
that can harm the monster except for an enchanted dragon-slaying arrow.

Nobody has seen one of those in ages. It is said that the wizard kept one in
his tower nearby... but he died a century ago. Others have tried to get into
the building just to escape with reports of deadly traps and monsters. But
there is no choice now but face the dangers within if you are to slay the
evil dragon. The time is running out and the path will certainly be filled
with peril, it's not an accident that this place is called...

THE SPIRE OF CHAOS

You have a week, adventurer.

## HOW TO PLAY

The game is played with the keyboard. You can use:

 - Arrow keys to move;
 - CTRL+Q to quit
 - Space bar or ESC to close pop-ups
 - In-game actions are shortcuts shown in the sidebar:
    - S: Search for hidden traps and doors around
    - R: Rest (heals and recovers spells)
    - I: Show inventory (where you can also choose to use items)
 - When a menu is shown, key shortcuts will be labeled with brackets

## ABOUT THE GAME

This is a game heavily inspired in the roguelike/nethack genre, but trying to
replace the complex interface into a more "choose your own adventure" multiple
choice type of experience. The mechanics internally also draw shamelessly
from D&D (there's a dragon! and a dungeon!). I also added a time limit as
compared to those.

There's of course a ton of extra content that I would have liked to add but
there was no time. Hopefully you still find it fun!

## LICENSE:

See LICENSE file

## LICENSE FOR OTHER RESOURCES

**Image credits:**

 - Most graphical assets (unless specified otherwise) were all created
   by https://www.patreon.com/forgottenadventures/ . They are great, you should sponsor them!
   They are licensed under Creative Commons — Attribution-NonCommercial-ShareAlike 4.0 International — CC BY-NC-SA 4.0
 - sidebar.png is assembled also with assets from Forgotten adventures
 - trap.png: Downloaded from https://pixabay.com/vectors/warning-sign-30915/ (license info available there)
 - scroll.png: https://www.deviantart.com/saimgraphics/art/Scroll-PNG-371989314
   Creative Commons Attribution 3.0 License
 - the intro background pictures are:
     - dragon from https://commons.wikimedia.org/wiki/File:Durian_-_Sintel-wallpaper-dragon.jpg under
       https://creativecommons.org/licenses/by/3.0/deed.en
     - tower image is a 1832 Thomas Cole painting, under public domain:
       https://commons.wikimedia.org/wiki/File:Cole_Thomas_Romantic_Landscape_with_Ruined_Tower_1832-36.jpg

**Music credits:**

 - All music tracks are by Kevin MacLeod, https://incompetech.com , distributed
   under CC-BY (http://creativecommons.org/licenses/by/4.0/)

Music from https://filmmusic.io:

 - "Serpentine Trek" by Kevin MacLeod (https://incompetech.com)
 - "Anguish" by Kevin MacLeod (https://incompetech.com)
 - "Oppressive Gloom" by Kevin MacLeod (https://incompetech.com)
 - "Crossing the Chasm" by Kevin MacLeod (https://incompetech.com)
 - "Volatile Reaction" by Kevin MacLeod (https://incompetech.com)
 - "Five Armies" by Kevin MacLeod (https://incompetech.com)
