import os, math
import pygame as pg
from . import colors, tools

pg.init()  # its here to start loading everything up asap

WIDTH, HEIGHT = (int(1280 / 1.4), int(720 / 1.4))
SCREEN_SIZE = (WIDTH, HEIGHT)
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)
_screen = pg.display.set_mode(SCREEN_SIZE)
BACKGROUND_COLOR = colors.LIGHT_GRAY
COLORKEY = (255, 0, 255)  # treated as alpha - bright purple

# Display until loading finishes.
FONT_LARGE = pg.font.SysFont("comicsansms", 110)
FONT_BIG = pg.font.SysFont("comicsansms", 55)
FONT_MED = pg.font.SysFont("comicsansms", 42)
FONT_SMED = pg.font.SysFont("comicsansms", 29)
FONT_SMALL = pg.font.SysFont("comicsansms", 25)
FONT_TINY = pg.font.SysFont("comicsansms", 20)

TILE_SIZE = math.floor((min(WIDTH, HEIGHT) / 8.36))
BULLET_SIZE = int(TILE_SIZE * 0.8)

UNIT_SIZE = int(TILE_SIZE / 1.8)
TILE_SPRITE_SIZE = TILE_SIZE - 10  # this offset needs to be even for the player marker to display symmetrically
# not used rn

# loading screen
_screen.fill(colors.BLUE)
_render = FONT_BIG.render("LOADING...", True, pg.Color("white"))
_screen.blit(_render, _render.get_rect(center=SCREEN_RECT.center))
pg.display.update()

pg.joystick.init()
joysticks = [pg.joystick.Joystick(i) for i in range(pg.joystick.get_count())]
# work if controller is connected via BT (otherwise 2 controllers are visible) dunno why :<, but it can be drivers issue

MAX_PLAYERS = 4
CAN_PATHS_CROSS = True
MAX_GOLD = 9999

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_3 = 3
PLAYER_4 = 4

DEFAULT_CONTROLS_1 = {pg.K_DOWN: "down",
                      pg.K_UP: "up",
                      pg.K_LEFT: "left",
                      pg.K_RIGHT: "right",
                      pg.K_RETURN: "action",
                      pg.K_p: "upgrade"
                      }

DEFAULT_CONTROLS_2 = {pg.K_s: "down",
                      pg.K_w: "up",
                      pg.K_a: "left",
                      pg.K_d: "right",
                      pg.K_SPACE: "action",
                      pg.K_q: "upgrade"
                      }

DEFAULT_CONTROLS_CONTROLLER = {12: "down",  # d-pad down
                               11: "up",  # d-pad up
                               13: "left",  # d-pad left
                               14: "right",  # d-pad right
                               0: "action",  # cross/a
                               2: "upgrade"  # square/x
                               }

CONTROLS = {
    PLAYER_1: DEFAULT_CONTROLS_1,
    PLAYER_2: DEFAULT_CONTROLS_2,
    PLAYER_3: DEFAULT_CONTROLS_CONTROLLER,
    PLAYER_4: DEFAULT_CONTROLS_CONTROLLER
}

PLAYER_CONTROLLERS = {
    PLAYER_1: None,
    PLAYER_2: None,
    PLAYER_3: 0,
    PLAYER_4: 1
}

INCOME = {
    'castle': 5,
    'market': 5
}

DIRECTIONS = {"up": (0, -1),
              "down": (0, 1),
              "left": (-1, 0),
              "right": (1, 0),
              "up-left": (-1, -1),
              "up-right": (1, -1),
              "down-right": (1, 1),
              "down-left": (-1, 1)
              }
OPPOSITE_DIRECTIONS = {"up": "down",
                       "down": "up",
                       "left": "right",
                       "right": "left",
                       "up-left": "down-right",
                       "up-right": "down-left",
                       "down-right": "up-left",
                       "down-left": "up-right"
                       }

MAPS = {
    "The Rumble": "\
oo..1o..oo\n\
4ooooooooo\n\
oooooooooo\n\
ooooooo...\n\
ooooooo3oo\n\
o2..oo..oo\n\
"
    , 'Canions': "\
1oooo.oooo2\n\
ooooo.ooooo\n\
...ooooo...\n\
ooooooooooo\n\
3oooo.oooo4\n\
"
    , 'Big Rumble': "\
oo..ooo.ooo\n\
4ooo..oooo1\n\
ooooooooooo\n\
o..ooooo...\n\
2ooo.oooooo\n\
oo..oooo.o3\n\
"
    , 'The Donut': "\
.ooooooooo.\n\
o1o..o..o3o\n\
oo...o...oo\n\
oo...o...oo\n\
o4o..o..o2o\n\
.ooooooooo.\n\
"
, 'Final Duel': "\
....ooo....\n\
ooooooooooo\n\
1ooo...ooo2\n\
ooooooooooo\n\
....ooo....\n\
"
}

PLAYER_COLORS = {
    PLAYER_1: colors.RED,
    PLAYER_2: colors.BLUE,
    PLAYER_3: colors.GREEN,
    PLAYER_4: colors.YELLOW,
}


def load_gfx_from_dirs(dirs):
    """
    Calls the tools.load_all_graphics() function for all directories passed.
    """
    base_path = os.path.join("project", "resources", "graphics")
    GFX = {}
    for directory in dirs:
        path = os.path.join(base_path, directory)
        GFX[directory] = tools.load_all_gfx(path, COLORKEY)
    return GFX


gfx = load_gfx_from_dirs(['buildings', 'units', 'utils'])
