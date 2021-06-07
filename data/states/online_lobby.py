import pickle
from typing import Optional, Dict, List
import time

import pygame as pg
from data import menu_utils, config, colors
from data.dataclasses import GameData
from data.menu_utils import BasicMenu, BoardPreview
from data.networking import Server, ClientData, Client, Receiver, Packable


class OnlineLobby(BasicMenu, Packable, Receiver):
    """Players connect and wait choose the settings before the game begins"""
    def __init__(self):
        super().__init__(2)
        self.image = pg.Surface(config.SCREEN_SIZE).convert()
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        preview_size = (int(config.WIDTH * 0.4), int(config.HEIGHT * 0.4))
        # start with 0 bots and one player - host
        self.board_preview: BoardPreview = BoardPreview(players_no=1, size=preview_size)
        self.rendered: Dict[str, (pg.Surface, pg.Rect)] = {}
        self.board_preview.change_map(0)
        self.server: Optional[Server] = None
        self.client: Optional[Client] = None
        self.is_host: bool = False
        self.preserve_network = False  # should the server and client be preserved when changing the state
        self.render()

    def startup(self, now, persistent):
        """
        Starts up the clients and/or server threads
        :param now: current time
        :param persistent: dict with keys:
            'is_host' -> should the server be created
            'ip' -> ignored is 'is_host'  the server is not created and the client connects to the specified ip
            'player_name' -> client's name
        """
        print(persistent)
        if persistent['is_host']:
            self.client = Client(self, 'scout', is_scout=True)
            if self.client.player_id is not None:
                # the client has connected to the server => the server is already up, go back to mode select
                self.next = 'ONLINE_MODE_SELECT'
                self.persist.update({'notification': 'The server is already hosted'})
                self.done = True
                time.sleep(0.1)  # give server a moment to parse the set_name command
                self.client.close()

            self.is_host = True
            self.server = Server(self)
            self.server.set_state_source(self, update_delay=0.5)
            self.server.run()
            self.client = Client(self, persistent['player_name'])
        else:
            self.client = Client(self, persistent['player_name'], persistent['ip'])
            if not self.client.running:
                self.next = 'ONLINE_MODE_SELECT'
                self.persist.update({'notification': 'Could not connect to the server {}'.format(persistent['ip'])})
                self.done = True

    def cleanup(self):
        if not self.preserve_network:
            print('cleaning up the network')
            if self.client and self.client.running:
                print('closing the client')
                self.client.close()
            if self.server:
                self.server.close()  # need to close the server and the client before closing the program
        return super().cleanup()

    def render_players(self, clients: List[Optional[ClientData]]):
        center_x, center_y = config.SCREEN_RECT.center
        strings = [f'{c.id}. {c.name[:10]} - {c.address[0]}' for c in clients if c]
        cols = [config.PLAYER_COLORS[c.id] for c in clients if c]
        args = [config.FONT_SMALL, strings, cols, center_y * 0.38, 35, True, center_x * 1.48]
        self.rendered['players'] = menu_utils.make_text_list(*args)

        self.board_preview.set_player_counts({'players': len(strings), 'bots': 0})
        self.board_preview.change_map(0)  # update player count

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

    def handle_message(self, message):
        if message[0] == 'init':  # ['init', map:MapConfig]
            self.start_game(message[1])
        elif message[0] == 'state':
            self.unpack(message[1])  # ['state', state_data: Dict]

    def get_event(self, event):
        super().get_event(event)
        if self.server and event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                self.board_preview.change_map(-1)
                self.server.send_state()
            elif event.key == pg.K_d:
                self.board_preview.change_map(1)
                self.server.send_state()

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
            if not self.is_host and i == 0:
                continue
            state = 'active' if self.index == i else 'inactive'
            buttons = self.rendered['buttons']
            text, rect = buttons[state][i]
            self.image.blit(text, rect)
        screen.blit(self.image, self.image.get_rect())

    def pressed_enter(self):
        if self.index == 0:  # start button
            if self.server is not None:
                map_config = self.board_preview.get_map_config()
                self.persist.update({
                    'game_data': GameData(server=self.server, client=self.client,
                                          map=map_config)
                })
                # self.server.send_to_all(pickle.dumps({'stats': building_stats.get_stats_dict()}))
                self.server.send_to_clients(pickle.dumps(['init', map_config]))
                self.preserve_network = True
                self.quit = True  # leave the menu state manager and start the game
        elif self.index == 1:  # back button
            self.next = 'ONLINE_MODE_SELECT'
            self.done = True

    def start_game(self, map_config):
        self.persist.update({
            'game_data': GameData(server=self.server, client=self.client, map=map_config)
        })
        self.preserve_network = True
        self.quit = True  # leave the menu state manager and start the game

    def pack(self):
        if not self.server:
            return {}
        return {
            'map_index': self.board_preview.map_index,
            'clients': self.server.clients
        }

    def unpack(self, data):
        if self.board_preview.map_index != data['map_index']:
            self.board_preview.set_map(data['map_index'])
        self.render_players(data['clients'])