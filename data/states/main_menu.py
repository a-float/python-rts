import sys
from typing import Any

import pygame as pg
from data import menu_utils, state_machine, config, colors
from data.components.board import Board
from data.states.online_lobby import OnlineLobby, OnlineModeSelect
from data.dataclasses import GameData, MapConfig


class Menu(state_machine.State):
    def __init__(self):
        super().__init__()
        self.next = "GAME"
        self.state_machine: Any[state_machine.StateMachine] = None

    def startup(self, now, persistent):
        self.state_machine = state_machine.StateMachine()
        state_dict = {
            "MAIN": MainMenu(),
            "GAME_SETUP": GameSetup(),
            'ONLINE_MODE_SELECT': OnlineModeSelect(),
            'ONLINE_LOBBY': OnlineLobby()
        }
        self.state_machine.setup_states(state_dict, "MAIN")
        super().startup(now, {})

    def cleanup(self):
        self.state_machine.state.cleanup()
        return super().cleanup()

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.start_time = pg.time.get_ticks()
        self.state_machine.get_event(event)

    def update(self, keys, now):
        self.state_machine.update(keys, now)
        if self.state_machine.done:
            self.done = True
            # taking the persist out of this state machine so it can be passed to the GAME state
            self.persist = self.state_machine.state.persist
            # print('new MENU persist ', self.persist)

    def draw(self, surface, interpolate):
        self.state_machine.draw(surface, interpolate)


class MainMenu(menu_utils.BasicMenu):
    def __init__(self):
        self.ITEMS = ['OFFLINE', 'ONLINE', 'EXIT']
        super().__init__(len(self.ITEMS))
        self.next = 'GAME_SETUP'
        start_y = config.SCREEN_RECT.height * 0.5
        self.title = config.FONT_BIG.render('Castillio', 1, colors.RED)
        self.title_rect = self.title.get_rect(midtop=(config.SCREEN_RECT.centerx, config.SCREEN_RECT.top + 20))
        self.items = menu_utils.make_options(config.FONT_MED, self.ITEMS, start_y, 65)

    def startup(self, now, persistent):
        pass

    def draw(self, surface, interpolate):
        surface.fill(config.BACKGROUND_COLOR)
        surface.blit(self.title, self.title_rect)
        for i, _ in enumerate(self.ITEMS):
            which = "active" if i == self.index else "inactive"
            text, rect = self.items[which][i]
            surface.blit(text, rect)

    def pressed_enter(self):
        selected_item = self.ITEMS[self.index]
        if selected_item == 'OFFLINE':
            self.next = 'GAME_SETUP'
            self.done = True
        elif selected_item == 'ONLINE':
            self.next = 'ONLINE_MODE_SELECT'
            self.done = True
        elif selected_item == 'EXIT':
            pg.quit()
            sys.exit()


class GameSetup(menu_utils.BidirectionalMenu):
    def __init__(self):
        super().__init__([5, 4])
        self.image = pg.Surface(config.SCREEN_SIZE).convert()
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        self.selected = {'bots': 0, 'players': 2}
        preview_size = (int(config.WIDTH*0.5), int(config.HEIGHT*0.5))
        self.board_preview = menu_utils.BoardPreview(self.selected['bots'], self.selected['players'], size=preview_size)
        self.NUMBERS = range(5)
        self.rendered = {}
        self.board_preview.change_map(0)
        self.render()

    def render(self):
        center_x, center_y = config.SCREEN_RECT.center
        left_start = center_x + 100
        args = [config.FONT_MED, list(map(lambda x: str(x), self.NUMBERS)), left_start, 35, False, center_y - 90]
        self.rendered['players_list'] = menu_utils.make_options(*args)

        players_text = config.FONT_SMALL.render('Players no:', 1, colors.BLACK)
        players_text_rect = players_text.get_rect(midleft=(left_start - 20, center_y - 90 - 45))
        self.rendered['players_text'] = (players_text, players_text_rect)

        args = [config.FONT_MED, list(map(lambda x: str(x), self.NUMBERS)), left_start, 35, False, center_y + 10]
        self.rendered['bots_list'] = menu_utils.make_options(*args)

        bots_text = config.FONT_SMALL.render('Bots no:', 1, colors.BLACK)
        bots_text_rect = bots_text.get_rect(midleft=(left_start - 20, center_y + 10 - 45))
        self.rendered['bots_text'] = (bots_text, bots_text_rect)

        args = [config.FONT_MED, ['START', 'BACK'], center_y * 1.5, 50, True, center_x * 1.55]
        self.rendered['buttons'] = menu_utils.make_options(*args)

        h_width, h_height, h_thick = 36, 52, 10
        surface = pg.Surface((h_width, h_height))
        surface.fill(config.BACKGROUND_COLOR)
        pg.draw.rect(surface, colors.BLUE, pg.Rect(0, 0, h_width, h_height), 3, border_radius=3)
        self.rendered['number_highlight'] = surface

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
        self.image.blit(*self.rendered['bots_text'])
        self.board_preview.draw(self.image)

        highlight = self.rendered['number_highlight']
        # draw the players and bots numbers
        for option_index, option in enumerate(['players', 'bots']):
            for i, val in enumerate(self.NUMBERS):
                state = 'active' if self.index == [val, option_index] else 'inactive'
                numbers = self.rendered[f'{option}_list']
                text, rect = numbers[state][i]
                if val == self.selected[option]:
                    self.image.blit(highlight, highlight.get_rect(center=(rect.center[0], rect.center[1]+2)))
                self.image.blit(text, rect)
        # draw the back and start buttons
        for i, val in enumerate([0, 1]):  # change it
            state = 'active' if self.index[1] == 2 + i else 'inactive'
            players = self.rendered['buttons']
            text, rect = players[state][i]
            self.image.blit(text, rect)
        screen.blit(self.image, self.image.get_rect())

    def pressed_enter(self):
        if self.index[1] == 0:  # change player no
            self.selected['players'] = self.index[0]
            self.board_preview.set_player_counts(self.selected)
            self.board_preview.change_map(0)  # update player count
        elif self.index[1] == 1:  # change bot no
            self.selected['bots'] = self.index[0]
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
