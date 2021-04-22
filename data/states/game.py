"""
This module contains the primary gameplay state.
"""

import sys
import math
import pygame as pg

from data import state_machine, config, colors
from data.components import board


class Game(state_machine.State):
    """Core state for the actual gameplay."""

    def __init__(self):
        state_machine.State.__init__(self)
        self.board = board.Board()

    def startup(self, now, persistent):
        """
        Call the parent class' startup method.
        If reset_map has been set (after player death etc.) recreate the world
        map and reset relevant variables.
        """
        self.board.initialize(persistent['map'][1])

    def cleanup(self):
        """Store background color and sidebar for use in camp menu."""
        self.done = False
        return self.persist

    def get_event(self, event):
        """
        Process game state events. Add and pop directions from the player's
        direction stack as necessary.
        """
        if event.type == pg.KEYDOWN:  # TODO tmp escape to the menu
            if event.key == pg.K_ESCAPE:
                self.board.clear()
                self.next = 'MENU'
                self.done = True
        self.board.handle_event(event)

    def update(self, keys, now):
        """Update phase for the primary game state."""
        self.board.update()

    def draw(self, surface, interpolate):
        """Draw level and sidebar; if player is dead draw death sequence."""
        surface.fill(colors.WHITE)
        self.board.draw(surface, interpolate)
