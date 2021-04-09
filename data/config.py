import pygame as pg

WIDTH, HEIGHT = (1200, 700)

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_3 = 3
PLAYER_4 = 4

DEFAULT_CONTROLS_1 = {pg.K_DOWN: "down",
                      pg.K_UP: "up",
                      pg.K_LEFT: "left",
                      pg.K_RIGHT: "right",
                      pg.K_SPACE: "action"}

DEFAULT_CONTROLS_2 = {pg.K_s: "down",
                      pg.K_w: "up",
                      pg.K_l: "left",
                      pg.K_r: "right",
                      pg.K_RETURN: "action"}

DIRECT_DICT = {"up": (0, 1),
               "down": (0, -1),
               "left": (-1, 0),
               "right": (1, 0)}
