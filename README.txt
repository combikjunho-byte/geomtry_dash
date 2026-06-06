GEOMETRY DASH - Python Edition
==============================

HOW TO PLAY
-----------
- When the game starts you pick a difficulty:
  Easy, Medium, Hard, Very Hard, or Boss.
  Use UP/DOWN (or press 1-5), then ENTER / click to start.
  Every difficulty is beatable -- the harder ones just scroll
  faster and pack the obstacles tighter.
- The cube then runs forward on its own.
- Press SPACE (or the UP arrow, or left-click) to JUMP.
- You can HOLD the jump key to keep hopping.
- Avoid the red spikes. Land on top of the blue platforms.
- Reach the green finish flag to win.
- Background music plays from the menu all the way through.
- Press R to restart the current difficulty from the beginning.
- Press ESC to go back to the difficulty menu (and again to quit).

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
Open geometry_dash/config.py in any text editor (even Notepad). You'll
find plain-English comments. Try:
  - JUMP_VELOCITY -> more negative = jump higher
  - GRAVITY       -> bigger = the cube falls faster
  - DIFFICULTIES  -> the per-tier speed, length, and obstacle density.
                     A longer 'length_cells' makes the % climb slower.

The level layout is generated per difficulty in build_level()
(geometry_dash/level.py).

Enjoy, and ask Claude to add new features whenever you like!
