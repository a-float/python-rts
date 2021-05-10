import pygame as pg
import data.config as config
from data.components.player import Player
from typing import Dict

# TODO maybe it should be in the game state. Very likely ill move it there later

class UI(pg.sprite.Sprite):
    def __init__(self, players: Dict[int, Player]):
        super().__init__()
        self.rect = config.SCREEN_RECT
        self.players = players
        self.player_gold = {k: self.players[k].gold for k in self.players}
        self.player_incomes = {k: self.players[k].income for k in self.players}
        self.info = {k: None for k in self.players}
        self.info_positions = {
            1: 'topleft',
            2: 'topright',
            3: 'bottomleft',
            4: 'bottomright',
        }
        for k in self.players:
            self.draw_dynamic_info(k)

    def draw_dynamic_info(self, player_no: int):
        # big enough but not too big
        player_color = self.players[player_no].color
        gold_font = config.FONT_SMED
        income_font = config.FONT_SMALL

        info_height = income_font.get_height() + gold_font.get_height()
        info = pg.Surface((int(config.WIDTH*0.2), info_height))
        info.fill(pg.Color('white'))
        gold_text = gold_font.render(str(self.player_gold[player_no])+'$', 1, player_color, pg.Color('white'))
        income_text = income_font.render('income: '+str(self.player_incomes[player_no]), 1, player_color, pg.Color('white'))

        kwargs = {self.info_positions[player_no]: getattr(config.SCREEN_RECT, self.info_positions[player_no])}
        info.blit(gold_text, gold_text.get_rect(midtop=info.get_rect().midtop))
        info.blit(income_text, income_text.get_rect(midtop=info.get_rect().center))

        # print(kwargs)
        self.info[player_no] = {
            'image': info,
            'rect': info.get_rect(**kwargs)
        }

    def update(self):
        for k in self.players:
            if self.player_gold[k] != self.players[k].gold or self.player_incomes[k] != self.players[k].income:
                self.player_gold[k] = self.players[k].gold
                self.player_incomes[k] = self.players[k].income
                self.draw_dynamic_info(k)
                # print('updating dynamic info')

    def draw(self, surface):
        for k in self.players:
            surface.blit(self.info[k]['image'], self.info[k]['rect'])
