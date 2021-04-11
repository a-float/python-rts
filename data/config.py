import pygame as pg
from . import colors
from data.components import building

pg.init()  # its here to start loading everything up asap

WIDTH, HEIGHT = (600, 400)
SCREEN_SIZE = (WIDTH, HEIGHT)
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)
_screen = pg.display.set_mode(SCREEN_SIZE)

# Display until loading finishes.
FONT = pg.font.SysFont("comicsansms", 100)

_screen.fill(colors.BLUE)
_render = FONT.render("LOADING...", True, pg.Color("white"))
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
                      pg.K_RETURN: "action"}

DEFAULT_CONTROLS_2 = {pg.K_s: "down",
                      pg.K_w: "up",
                      pg.K_a: "left",
                      pg.K_d: "right",
                      pg.K_SPACE: "action"}

CONTROLS = {
    1: DEFAULT_CONTROLS_1,
    2: DEFAULT_CONTROLS_2,
    3: None,
    4: None
}
INCOME = {
  'castle' : 5,
  'market' : 5
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

TILE_SIZE = 50
TILE_SPRITE_SIZE = 45


MAP1 =  "oo..1o..oo\n"
MAP1 += "4ooooooooo\n"
MAP1 += "oooooooooo\n"
MAP1 += "ooooooo...\n"
MAP1 += "ooooooo3oo\n"
MAP1 += "o2..oo..oo\n"


PLAYER_COLORS = {
    1: colors.RED,
    2: colors.BLUE,
    3: colors.GREEN,
    4: colors.YELLOW,
}
