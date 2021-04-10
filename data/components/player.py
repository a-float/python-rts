from data.colors import *
import data.config as config


class Player:
    """Class that allows the player to interact with the Board"""

    def __init__(self, player_no):
        self.base_color = RED
        self.is_dead = False
        self.active_tile = None
        self.controls = config.DEFAULT_CONTROLS_1
        self.gold = 0
        self.income = 5
        self.color = config.PLAYER_COLORS[player_no]
