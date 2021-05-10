from typing import Optional, Dict, List
import names
import socket

import pygame as pg
from data import menu_utils, config, colors
from data.menu_utils import BasicMenu, BoardPreview
from data.networking.server import Server, ClientData
from data.networking.client import Client


class OnlineModeSelect(BasicMenu):
    def __init__(self):
        super().__init__(3)
        center_x, center_y = config.SCREEN_RECT.center
        host, ip = self.get_ip()
        self.head_surface = config.FONT_SMALL.render(f'Your ip is: {ip}', True, pg.Color('black'))
        self.head_rect = self.head_surface.get_rect(center=(center_x, center_y * 0.55))

        self.options = menu_utils.make_options(config.FONT_MED, ['HOST', 'JOIN'], center_y * 0.9, 70, True, center_x)

        args = [config.FONT_SMALL, colors.WHITE, colors.BLACK, (200, 50), (center_x, center_y * 1.7)]
        self.text_field = menu_utils.TextField(*args)

    def get_event(self, event):
        super().get_event(event)
        if self.index == 2:  # the text_field
            self.text_field.active = True
            self.text_field.bg_color = colors.BLUE
        else:
            if self.text_field.active:
                self.text_field.active = False
                self.text_field.bg_color = colors.WHITE
        self.text_field.handle_event(event)
        self.text_field.update_image()
        self.dirty = True

    def get_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return hostname, ip_address

    def _draw(self, screen, interpolate):
        screen.fill(config.BACKGROUND_COLOR)

        # draw the hostname and ip address info
        screen.blit(self.head_surface, self.head_rect)

        # draw the options
        for i, _ in enumerate(self.options):
            which = "active" if i == self.index else "inactive"
            text, rect = self.options[which][i]
            screen.blit(text, rect)

        # draw the text field
        self.text_field.draw(screen)

    def pressed_enter(self):
        if self.index == 0:
            self.next = 'ONLINE_LOBBY'
            self.done = True

    def pressed_exit(self):
        self.next = 'MAIN'
        self.done = True


class OnlineLobby(BasicMenu):
    def __init__(self):
        super().__init__(2)
        self.image = pg.Surface(config.SCREEN_SIZE).convert()
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        preview_size = (int(config.WIDTH * 0.4), int(config.HEIGHT * 0.4))
        # start with 0 bots and one player - host
        self.board_preview: BoardPreview = BoardPreview(0, 1, size=preview_size)
        self.rendered: Dict[str, (pg.Surface, pg.Rect)] = {}
        self.board_preview.change_map(0)
        self.server: Optional[Server] = None
        self.handle = None
        self.client: Optional[Client] = None
        self.render()

    def startup(self, now, persistent):
        self.server = Server(self)
        self.handle = self.server.run()
        self.client = Client(names.get_first_name())

    def cleanup(self):
        self.client.close()
        self.server.close()  # need to close the server and the client before closing the program
        # state cleanup
        self.done = False
        return self.persist

    def render_players(self, clients: List[Optional[ClientData]]):
        center_x, center_y = config.SCREEN_RECT.center

        strings = [f'{c.id}. {c.name} - {c.address}' for c in clients if c]
        cols = [config.PLAYER_COLORS[c.id] for c in clients if c]
        args = [config.FONT_TINY, strings, cols, center_y * 0.38, 35, True, center_x * 1.48]
        self.rendered['players'] = menu_utils.make_text_list(*args)
        print(self.rendered['players'])
        self.dirty = True

    def render(self):
        center_x, center_y = config.SCREEN_RECT.center

        head = config.FONT_SMALL.render('Players in the lobby:', True, colors.BLACK)
        self.rendered['players_header'] = head, head.get_rect(center=(center_x * 1.48, center_y * 0.21))

        player_list_bg = pg.Surface((config.WIDTH * 0.37, config.HEIGHT * 0.57))
        player_list_bg.fill(colors.WHITE)
        rect = player_list_bg.get_rect(midtop=(center_x * 1.48, center_y * 0.13))
        self.rendered['player_list_bg'] = (player_list_bg, rect)

        args = [config.FONT_MED, ['START', 'BACK'], center_y * 1.5, 50, True, center_x * 1.48]
        self.rendered['buttons'] = menu_utils.make_options(*args)
        self.rendered['players'] = []

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

    def _draw(self, screen, interpolate):
        self.image.fill(config.BACKGROUND_COLOR)
        self.board_preview.draw(self.image)

        # draw the player list background
        self.image.blit(*self.rendered['player_list_bg'])
        # draw the players header
        self.image.blit(*self.rendered['players_header'])

        # draw the connected players
        for text, rect in self.rendered['players']:
            self.image.blit(text, rect)

        # draw the back and start buttons
        for i, val in enumerate([0, 1]):  # change it
            state = 'active' if self.index == i else 'inactive'
            buttons = self.rendered['buttons']
            text, rect = buttons[state][i]
            self.image.blit(text, rect)
        screen.blit(self.image, self.image.get_rect())

    def pressed_enter(self):
        if self.index == 0:  # start button
            # self.persist = self.get_map_settings()
            # self.board_preview.clear()
            # self.quit = True
            self.client.send('blah blah KZ be cute af blah')
            # self.server.running = False
        elif self.index == 1:  # back button
            self.next = 'ONLINE_MODE_SELECT'
            self.done = True

    def get_map_settings(self):
        return self.board_preview.get_settings()
