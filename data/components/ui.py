import pygame as pg
from typing import Dict, Any
import data.config as config
from data.components import Player
from data.building_stats import BUILDING_DATA as DATA


class UI(pg.sprite.Sprite):
    def __init__(self, players: Dict[int, Player]):
        super().__init__()
        self.rect = config.SCREEN_RECT
        self.players: Dict[int: Player] = players
        self.player_gold: Dict[int: int] = {k: self.players[k].gold for k in self.players}
        self.player_incomes: Dict[int: int] = {k: self.players[k].income for k in self.players}
        self.info: Dict[int: Any[pg.Surface, pg.Rect]] = {k: None for k in self.players}
        self.info_positions = {
            1: 'topleft',
            2: 'topright',
            3: 'bottomleft',
            4: 'bottomright',
        }
        for k in self.players:
            self.draw_dynamic_info(k)
        text = f'Costs: tower={DATA["tower"]["cost"]}g, market={DATA["market"]["cost"]}g, barracks={DATA["barracks"]["cost"]}g, upgrades=10g'
        self.bottom_info = config.FONT_TINY.render(text, 1, pg.Color('black'))
        self.bottom_info_rect = self.bottom_info.get_rect(centerx=config.SCREEN_RECT.centerx, bottom=config.SCREEN_RECT.bottom-5)

    def draw_dynamic_info(self, player_no: int):
        # big enough but not too big
        player_color = self.players[player_no].color
        gold_font = config.FONT_SMED
        income_font = config.FONT_SMALL

        info_height = income_font.get_height() + gold_font.get_height()
        info = pg.Surface((int(config.WIDTH*0.14), info_height+10))
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

    @staticmethod
    def show_winner(surface, winner: Player):
        help_message = 'Press ESC to quit'
        subtext = config.FONT_TINY.render(help_message, 1, pg.Color('black'))

        winner_text = (f'Player {winner.id} has won!' if winner else 'There is no winner')
        text_color = winner.color if winner else pg.Color('black')
        text = config.FONT_MED.render(winner_text, 1, text_color)

        pad = 20
        text_bg = pg.Surface((config.WIDTH, 20+text.get_height()+subtext.get_height()))
        text_bg_rect = text_bg.get_rect()
        text_bg.fill(pg.Color('white'))
        # setting the relative positions of texts on the background
        text_bg.blit(text, text.get_rect(top=text_bg_rect.top, centerx=text_bg_rect.centerx))
        text_bg.blit(subtext, subtext.get_rect(centery=text_bg_rect.centery+pad+10, centerx=text_bg_rect.centerx))
        surface.blit(text_bg, text_bg.get_rect(center=config.SCREEN_RECT.center))

    def update(self):
        for k in self.players:
            # re render text only if necessary
            if self.player_gold[k] != self.players[k].gold or self.player_incomes[k] != self.players[k].income:
                self.player_gold[k] = self.players[k].gold
                self.player_incomes[k] = self.players[k].income
                self.draw_dynamic_info(k)

    def draw(self, surface):
        for k in self.players:
            surface.blit(self.info[k]['image'], self.info[k]['rect'])
        surface.blit(self.bottom_info, self.bottom_info_rect)
