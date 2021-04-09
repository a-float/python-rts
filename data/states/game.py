"""
This module contains the primary gameplay state.
"""

import sys
import math
import pygame as pg

from data import state_machine
from data.components import map


class Game(state_machine._State):
    """Core state for the actual gameplay."""
    def __init__(self):
        state_machine._State.__init__(self)
        self.map = map.Map()

    def startup(self, now, persistent):
        """
        Call the parent class' startup method.
        If reset_map has been set (after player death etc.) recreate the world
        map and reset relevant variables.
        """
        self.map.initialize()

    def cleanup(self):
        """Store background color and sidebar for use in camp menu."""
        self.done = False
        return self.persist

    def get_event(self, event):
        """
        Process game state events. Add and pop directions from the player's
        direction stack as necessary.
        """
        if self.player.action_state != "dead":
            if event.type == pg.KEYDOWN:
                self.player.add_direction(event.key)
                if not self.world.scrolling:
                    if event.key == pg.K_SPACE:
                        self.player.attack()
                    elif event.key == pg.K_s:
                        self.change_to_camp()
                    elif event.key == pg.K_LSHIFT:
                        self.player.interact(self.world.level.interactables)
            elif event.type == pg.KEYUP:
                self.player.pop_direction(event.key)


    def update(self, keys, now):
        """Update phase for the primary game state."""


    def draw(self, surface, interpolate):
        """Draw level and sidebar; if player is dead draw death sequence."""

