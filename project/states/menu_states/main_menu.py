import sys
import pygame as pg
from project import menu_utils, config, colors


class MainMenu(menu_utils.BasicMenu):
    def __init__(self):
        self.ITEMS = ['OFFLINE', 'ONLINE', 'HELP', 'EXIT']
        super().__init__(len(self.ITEMS))
        self.next = 'GAME_SETUP'
        start_y = config.SCREEN_RECT.height * 0.45
        self.title = config.FONT_LARGE.render('Castillio', 1, colors.RED)
        self.title_rect = self.title.get_rect(midtop=(config.SCREEN_RECT.centerx, config.SCREEN_RECT.top + 20))
        self.items = menu_utils.make_options(config.FONT_BIG, self.ITEMS, start_y, 65)
        self.help_index = -1  # if equal to -1 show no help
        self.help_images = [
                pg.transform.smoothscale(config.gfx['utils'][image_name], config.SCREEN_RECT.size) for
                image_name in ['main_help1', 'main_help2', 'main_help3']
            ]

    def startup(self, now, persistent):
        pass

    def draw(self, surface, interpolate):
        if self.help_index >= 0:
            surface.fill(pg.Color('white'))
            surface.blit(self.help_images[self.help_index], config.SCREEN_RECT)
            return
        surface.fill(config.BACKGROUND_COLOR)
        surface.blit(self.title, self.title_rect)
        for i, _ in enumerate(self.ITEMS):
            which = "active" if i == self.index else "inactive"
            text, rect = self.items[which][i]
            surface.blit(text, rect)

    def get_event(self, event):
        if event.type == pg.KEYDOWN and self.help_index > -1:
            self.help_index = (self.help_index + 1) % (len(self.help_images) + 1)
            if self.help_index == len(self.help_images):
                self.help_index = -1  # stop showing help
            return
        super().get_event(event)

    def pressed_enter(self):
        selected_item = self.ITEMS[self.index]
        if selected_item == 'OFFLINE':
            self.next = 'GAME_SETUP'
            self.done = True
        elif selected_item == 'ONLINE':
            self.next = 'ONLINE_MODE_SELECT'
            self.done = True
        elif selected_item == 'HELP':
            self.help_index = 0
        elif selected_item == 'EXIT':
            pg.quit()
            sys.exit()
