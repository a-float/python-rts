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
from data.networking import Client, Server, Receiver, Packable


# TODO add receiver class? to online lobby as well
class Game(state_machine.State, Packable, Receiver):
    """Core state for the actual gameplay."""

    def pack(self):
        return {
            'board': self.board.pack(),
            'players': [player.pack() for player in self.players.values()],
        }

    def unpack(self, data):
        print('Game unpacking data: ', data)
        self.board.unpack(data['board'])
        for player_data in data['players']:
            self.players[player_data['id']].unpack(player_data)

    def __init__(self):
        state_machine.State.__init__(self)
        self.board = board.Board(self)
        self.players: Dict[int, Player] = {}
        self.UI = None
        self.is_over: bool = False
        self.server: Optional[Server] = None  # if is not None, the game is online, and this Game is the host
        self.client: Optional[Client] = None  # if is not None, the game is online, and this Game is a client
        # self.online: bool = False  # if server and client are None, the game is played offline

    def startup(self, now, persistent):
        self.is_over = False
        print('game persistent is ', persistent)
        if 'game_data' not in persistent or type(persistent['game_data']) != GameData:
            raise IndexError('GAME startup: game_data key not present in the persistent dictionary.')
        settings = persistent['game_data']
        self.client, self.server = settings.client, settings.server
        if self.server:
            self.server.set_state_source(self, 0.3)
        if self.client:
            self.client.receiver = self
            for p in self.players.values():
                print('MY ID is ', p.id)
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
        if event.type == pg.KEYDOWN or event.type == pg.JOYBUTTONDOWN:  # TODO tmp escape to the menu
            if not event.type == pg.JOYBUTTONDOWN and event.key == pg.K_ESCAPE:
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
        elif message[0] == 'state' and self.server is None:  # the state owner doesnt care about the state message
            self.unpack(message[1])

    def update(self, keys, now):
        """Update phase for the primary game state."""
        if not self.is_over:
            self.is_over = self._is_over()
            self.UI.update()
            self.board.update(now)

    def get_winner(self):
        """
        Finds the player who has not lost and returns him. If no one has survived returns None
        Raises assertion error if called while the game is not over
        """
        assert self.is_over, 'To get the winner, the game must be over'
        for player in self.players.values():
            if not player.lost:
                return player
        return None

    def _is_over(self):
        """Returns True if at least two players haven't lost yet"""
        still_playing = 0
        for player in self.players.values():
            if not player.lost:
                still_playing += 1
        return still_playing <= 1

    def draw(self, surface, interpolate):
        """Draw level and sidebar; if player is dead draw death sequence."""
        surface.fill(colors.WHITE)
        self.UI.draw(surface)
        for p in self.players.values():
            p.draw_marker(surface)
        self.board.draw(surface, interpolate)
        for p in self.players.values():
            if not p.is_online:
                p.draw_menu(surface)
        if self.is_over:
            print('Game is over')
            self.UI.show_winner(surface, self.get_winner())
