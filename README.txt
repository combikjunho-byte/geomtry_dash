GEOMETRY DASH - Python Edition
==============================

HOW TO PLAY
-----------
- The cube runs forward on its own.
- Press SPACE (or the UP arrow, or left-click) to JUMP.
- You can HOLD the jump key to keep hopping.
- Avoid the red spikes. Land on top of the blue platforms.
- Reach the green finish flag to win.
- Press R any time to restart from the beginning.
- Press ESC to quit.

HOW TO RUN IT (pick one)
------------------------
EASIEST:  Double-click  run.bat

OR, in a terminal:
    cd C:\Users\human\geometry-dash
    python main.py

IF IT SAYS "pygame not found":
    python -m pip install pygame

WANT TO CHANGE THE GAME?
------------------------
Open main.py in any text editor (even Notepad). Near the top you'll
find a section called SETTINGS with plain-English comments. Try:
  - SPEED        -> lower = easier, higher = harder
  - JUMP_VELOCITY-> more negative = jump higher
  - GRAVITY      -> bigger = the cube falls faster

The level layout lives in the build_level() function further down --
each spikes(...) and platform(...) line adds an obstacle.

Enjoy, and ask Claude to add new features whenever you like!
