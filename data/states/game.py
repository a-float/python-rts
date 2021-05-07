"""
This module contains the primary gameplay state.
"""

import sys
import math
import pygame as pg

from data import state_machine, config, colors
from data.components import board, UI


class Game(state_machine.State):
    """Core state for the actual gameplay."""

    def __init__(self):
        state_machine.State.__init__(self)
        self.board = board.Board()
        self.players = {}
        self.UI = None

    def startup(self, now, persistent):
        self.players = self.board.initialize(persistent)
        self.UI = UI.UI(self.players)

    def cleanup(self):
        self.done = False
        return self.persist

    def get_event(self, event):
        if event.type == pg.KEYDOWN:  # TODO tmp escape to the menu
            if event.key == pg.K_ESCAPE:
                self.board.clear()
                self.next = 'MENU'
                self.done = True
        self.board.handle_event(event)
        for p in self.players.values():
            p.handle_event(event)

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