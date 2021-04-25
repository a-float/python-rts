import os
import pygame as pg
from . import colors, tools

pg.init()  # its here to start loading everything up asap

WIDTH, HEIGHT = (600, 400)
SCREEN_SIZE = (WIDTH, HEIGHT)
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)
_screen = pg.display.set_mode(SCREEN_SIZE)
BACKGROUND_COLOR = colors.LIGHT_GRAY
COLORKEY = (255, 0, 255)  # treated as alpha - bright purple

# Display until loading finishes.
FONT_BIG = pg.font.SysFont("comicsansms", 100)
FONT_MED = pg.font.SysFont("comicsansms", 50)
FONT_SMALL = pg.font.SysFont("comicsansms", 20)
FONT_TINY = pg.font.SysFont("comicsansms", 15)

_screen.fill(colors.BLUE)
_render = FONT_BIG.render("LOADING...", True, pg.Color("white"))
_screen.blit(_render, _render.get_rect(center=SCREEN_RECT.center))
pg.display.update()

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_3 = 3
PLAYER_4 = 4

DEFAULT_CONTROLS_1 = {pg.K_DOWN: "down",
                      pg.K_UP: "up",
                      pg.K_LEFT: "left",
                      pg.K_RIGHT: "right",
                      pg.K_RETURN: "action",
                      pg.K_i: "barracks",
                      pg.K_o: "market",
                      pg.K_p: "tower",
                      pg.K_l: "upgrade",
                      pg.K_k: "start_path"
                      }

DEFAULT_CONTROLS_2 = {pg.K_s: "down",
                      pg.K_w: "up",
                      pg.K_a: "left",
                      pg.K_d: "right",
                      pg.K_SPACE: "action",
                      pg.K_q: "barracks",
                      pg.K_e: "market",
                      pg.K_r: "tower",
                      pg.K_f: "upgrade",
                      pg.K_g: "start_path"
                      }

CONTROLS = {
    1: DEFAULT_CONTROLS_1,
    2: DEFAULT_CONTROLS_2,
    3: None,
    4: None
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

TILE_SIZE = 50
UNIT_SIZE = 40
TILE_SPRITE_SIZE = 45

MAPS = {
    "Big Rumble": "\
oo..1o..oo\n\
4ooooooooo\n\
oooooooooo\n\
ooooooo...\n\
ooooooo3oo\n\
o2..oo..oo\n\
"
    , "Small Rumble": "\
oo..0o..o4\n\
1ooooooooo\n\
ooooooo3oo\n\
oo2oooo...\n\
"
    , 'Canions': "\
1oooo.oooo2\n\
ooooo.ooooo\n\
...ooooo...\n\
ooooooooooo\n\
3oooo.oooo4\n\
"
}

PLAYER_COLORS = {
    1: colors.RED,
    2: colors.BLUE,
    3: colors.GREEN,
    4: colors.YELLOW,
}


def load_gfx_from_dirs(dirs):
    """
    Calls the tools.load_all_graphics() function for all directories passed.
    """
    base_path = os.path.join("data", "resources", "graphics")
    GFX = {}
    for directory in dirs:
        path = os.path.join(base_path, directory)
        GFX[directory] = tools.load_all_gfx(path)
    return GFX


gfx = load_gfx_from_dirs(['buildings', 'units'])