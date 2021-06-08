import pygame as pg
from project import menu_utils, config, colors
from project.dataclasses import GameData

class GameSetup(menu_utils.BidirectionalMenu):
    def __init__(self):
        self.PLAYER_OPTIONS_COUNT = range(1,5)
        super().__init__([len(self.PLAYER_OPTIONS_COUNT), 4])
        self.image = pg.Surface(config.SCREEN_SIZE).convert()
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        self.selected = {'players': 2}
        preview_size = (int(config.WIDTH*0.5), int(config.HEIGHT*0.5))
        self.board_preview = menu_utils.BoardPreview(self.selected['players'], size=preview_size)
        self.rendered = {}
        self.board_preview.change_map(0)
        self.render()

    def render(self):
        center_x, center_y = config.SCREEN_RECT.center
        header_font = config.FONT_SMED
        options_font = config.FONT_MED
        options_font_width = options_font.size('2')[0]
        header_font_height = header_font.get_linesize()
        y_spacing = header_font_height+5
        top_start = center_y*0.4
        options_center = center_x*1.5-options_font_width*2

        # player no header
        players_text = header_font.render('Players no:', 1, colors.BLACK)
        players_text_rect = players_text.get_rect(midleft=(center_x*1.5-players_text.get_rect().width//2, top_start))
        self.rendered['players_text'] = (players_text, players_text_rect)

        # player no list
        args = [options_font, list(map(lambda x: str(x), self.PLAYER_OPTIONS_COUNT)),
                options_center, (options_font_width+5), False, top_start+y_spacing]
        self.rendered['players_list'] = menu_utils.make_options(*args)

        # path crossing header
        path_cross_text = header_font.render('Can paths cross:', 1, colors.BLACK)
        path_cross_text_rect = path_cross_text.get_rect(midleft=(center_x*1.5-path_cross_text.get_rect().width//2,
                                                                 top_start+y_spacing*3))
        self.rendered['path_cross_text'] = (path_cross_text, path_cross_text_rect)

        # path crossing check
        args = [options_font, ['No', 'Yes'], options_center, options_font_width * 3, False, top_start+y_spacing*4]
        self.rendered['cross_options_list'] = menu_utils.make_options(*args)

        # START and BACK buttons
        args = [config.FONT_MED, ['START', 'BACK'], top_start+y_spacing*6, y_spacing+10, True, center_x * 1.5]
        self.rendered['buttons'] = menu_utils.make_options(*args)

        # the number highlight rectangle
        h_width, h_height, h_thick = options_font_width+5, options_font.get_ascent(), 10
        surface = pg.Surface((h_width, h_height))
        surface.fill(config.BACKGROUND_COLOR)
        pg.draw.rect(surface, colors.BLUE, pg.Rect(0, 0, h_width, h_height), 3, border_radius=3)
        self.rendered['number_highlight'] = surface

        # the number highlight rectangle
        h_width, h_height, h_thick = options_font_width*3, options_font.get_ascent(), 10
        surface = pg.Surface((h_width, h_height))
        surface.fill(config.BACKGROUND_COLOR)
        pg.draw.rect(surface, colors.BLUE, pg.Rect(0, 0, h_width, h_height), 3, border_radius=3)
        self.rendered['bool_highlight'] = surface

    def get_event(self, event):
        super().get_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                self.board_preview.change_map(1)
            elif event.key == pg.K_d:
                self.board_preview.change_map(-1)

    def pressed_exit(self):
        self.next = 'MAIN'
        self.done = True

    def draw(self, screen, interpolate):  # TODO it doesnt have to redraw every frame
        self.image.fill(config.BACKGROUND_COLOR)
        self.image.blit(*self.rendered['players_text'])
        self.image.blit(*self.rendered['path_cross_text'])
        self.board_preview.draw(self.image)

        no_highlight = self.rendered['number_highlight']
        bool_highlight = self.rendered['bool_highlight']

        # draw the players numbers
        for option_index, option in enumerate(['players']):
            for i, val in enumerate(self.PLAYER_OPTIONS_COUNT):
                state = 'active' if self.index == [val-1, option_index] else 'inactive'
                numbers = self.rendered[f'{option}_list']
                text, rect = numbers[state][i]
                if val == self.selected[option]:
                    self.image.blit(no_highlight, no_highlight.get_rect(center=(rect.center[0], rect.center[1]+2)))
                self.image.blit(text, rect)

        for i in range(2):
            state = 'active' if self.index[1] == 1 and (self.index[0]+i+1) % 2 else 'inactive'
            options = self.rendered['cross_options_list']
            text, rect = options[state][i]
            if config.CAN_PATHS_CROSS == i:
                self.image.blit(bool_highlight, bool_highlight.get_rect(center=(rect.center[0], rect.center[1] + 2)))
            self.image.blit(text, rect)

        # draw the back and start buttons
        for i in range(2):
            state = 'active' if self.index[1] == 2 + i else 'inactive'
            players = self.rendered['buttons']
            text, rect = players[state][i]
            self.image.blit(text, rect)
        screen.blit(self.image, self.image.get_rect())

    def pressed_enter(self):
        if self.index[1] == 0:  # change player no
            self.selected['players'] = self.index[0]+1
            self.board_preview.set_player_counts(self.selected)
            self.board_preview.change_map(0)  # update player count
        elif self.index[1] == 1:  # change path crossing
            config.CAN_PATHS_CROSS = self.index[0] % 2
        elif self.index[1] == 2:  # start button
            self.persist = {
                'game_data': GameData(server=None, client=None,
                                      map=self.board_preview.get_map_config())
            }
            self.board_preview.clear()
            self.quit = True
        elif self.index[1] == 3:  # back button
            self.next = 'MAIN'
            self.done = True
