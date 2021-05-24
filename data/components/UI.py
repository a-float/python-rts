import pygame as pg
import data.config as config
from data.components.player import Player
from data.components.building_stats import BUILDING_DATA as data
from typing import Dict


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
        text = f'Costs: tower: {data["tower"]["cost"]}g market: {data["market"]["cost"]}g barracks: {data["barracks"]["cost"]}g'
        self.bottom_info = config.FONT_SMALL.render(text, 1, pg.Color('black'))
        self.bottom_info_rect = self.bottom_info.get_rect(centerx=config.SCREEN_RECT.centerx, bottom=config.SCREEN_RECT.bottom-20)

    def draw_dynamic_info(self, player_no: int):
        # big enough but not too big
        player_color = self.players[player_no].color
        gold_font = config.FONT_SMED
        income_font = config.FONT_SMALL

        info_height = income_font.get_height() + gold_font.get_height()
        info = pg.Surface((int(config.WIDTH*0.14), info_height))
        info.fill(pg.Color('white'))
        gold_text = gold_font.render(str(self.player_gold[player_no])+'$', 1, player_color, pg.Color('white'))
        income_text = income_font.render(f'+{int(self.player_incomes[player_no])}$/s', 1, player_color, pg.Color('white'))

        kwargs = {self.info_positions[player_no]: getattr(config.SCREEN_RECT, self.info_positions[player_no])}
        info.blit(gold_text, gold_text.get_rect(midtop=info.get_rect().midtop))
        info.blit(income_text, income_text.get_rect(midtop=info.get_rect().center))

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

    def draw(self, surface):
        for k in self.players:
            surface.blit(self.info[k]['image'], self.info[k]['rect'])
        surface.blit(self.bottom_info, self.bottom_info_rect)
