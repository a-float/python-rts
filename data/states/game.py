"""
This module contains the primary gameplay state.
"""
import pickle
import sys
import math
from dataclasses import dataclass
from typing import Any, Optional, Dict

import pygame as pg
from data import state_machine, config, colors
from data.components import board, UI
from data.components.player import Player
from data.dataclasses import GameData
from data.networking.client import Client
from data.networking.server import Server


class Game(state_machine.State):
    """Core state for the actual gameplay."""

    def __init__(self):
        state_machine.State.__init__(self)
        self.board = board.Board()
        self.players: Dict[int, Player] = {}
        self.UI = None
        self.server: Optional[Server] = None  # if is not None, the game is online, and this Game is the host
        self.client: Optional[Client] = None  # if is None, the game is played offline

    def startup(self, now, persistent):
        print('game persistent is ', persistent)
        if 'game_data' not in persistent or type(persistent['game_data']) != GameData:
            raise IndexError('GAME startup: game_data key not present in the persistent dictionary.')
        settings = persistent['game_data']
        self.client, self.server = settings.client, settings.server
        if self.client:
            self.client.receiver = self
            for p in self.players.values():
                if p.id != self.client.player_id:
                    p.is_online = True

        self.players = self.board.initialize(settings.map)
        self.UI = UI.UI(self.players)
        # set the client. If None, the game is played offline

    def cleanup(self):
        if self.client and self.client.running:
            print('closing the client')
            self.client.close()
        if self.server:
            print('closing the server')
            self.server.close()  # need to close the server and the client before closing the program
        return super().cleanup()

    def get_event(self, event):
        if event.type == pg.KEYDOWN:  # TODO tmp escape to the menu
            if event.key == pg.K_ESCAPE:
                self.board.clear()
                self.next = 'MENU'
                self.done = True
            for p in self.players.values():
                comm = p.get_command_from_event(event)
                # send what you want to do to the server, and execute it when the servers responds
                if self.client and comm is not None:
                    self.client.send(f'action:{comm}')
                else:  # playing offline, just execute the command
                    p.execute_command(comm)

    def handle_message(self, message):
        print('Game received message: ', message)
        if message[0] == 'action':  # someone has pressed a key ('kdown', player id, command to execute)
            self.players[message[1]].execute_command(message[2])

    def update(self, keys, now):
        """Update phase for the primary game state."""
        self.UI.update()
        self.board.update(now)

    def draw(self, surface, interpolate):
        """Draw level and sidebar; if player is dead draw death sequence."""
        surface.fill(colors.WHITE)
        self.UI.draw(surface)
        for p in self.players.values():
            p.draw_marker(surface)
        self.board.draw(surface, interpolate)
        for p in self.players.values():
            if not p.is_online:
                p.draw_menus(surface)
