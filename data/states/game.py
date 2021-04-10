"""
This module contains the primary gameplay state.
"""

import sys
import math
import pygame as pg

from data import state_machine, config
from data.components import board


class Game(state_machine.State):
    """Core state for the actual gameplay."""

    def __init__(self):
        state_machine.State.__init__(self)
        self.board = board.Board()
        self.board.initialize(config.MAP1)

    def startup(self, now, persistent):
        """
        Call the parent class' startup method.
        If reset_map has been set (after player death etc.) recreate the world
        map and reset relevant variables.
        """

    def cleanup(self):
        """Store background color and sidebar for use in camp menu."""
        self.done = False
        return self.persist

    def get_event(self, event):
        """
        Process game state events. Add and pop directions from the player's
        direction stack as necessary.
        """
        # if self.player.action_state != "dead":
        #     if event.type == pg.KEYDOWN:
        #         self.player.add_direction(event.key)
        #         if not self.world.scrolling:
        #             if event.key == pg.K_SPACE:
        #                 self.player.attack()
        #             elif event.key == pg.K_s:
        #                 self.change_to_camp()
        #             elif event.key == pg.K_LSHIFT:
        #                 self.player.interact(self.world.level.interactables)
        #     elif event.type == pg.KEYUP:
        #         self.player.pop_direction(event.key)
        self.board.handle_event(event)


    def update(self, keys, now):
        """Update phase for the primary game state."""
        self.board.update()

    def draw(self, surface, interpolate):
        """Draw level and sidebar; if player is dead draw death sequence."""
        self.board.draw(surface, interpolate)
