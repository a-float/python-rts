"""
Contains useful functionality for uni- and bi-directional menus.
"""

import pygame as pg

from . import config, state_machine, colors


class BasicMenu(state_machine.State):
    """Base class for basic uni-directional menus."""

    def __init__(self, option_length):
        state_machine.State.__init__(self)
        self.option_length = option_length
        self.index = 0

    def get_event(self, event):
        """
        Generic event getter for scrolling through menus.
        """
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_DOWN, pg.K_RIGHT):
                # config.SFX["dj-chronos__menu-nav-2"].play()
                self.index = (self.index + 1) % self.option_length
            elif event.key in (pg.K_UP, pg.K_LEFT):
                # config.SFX["dj-chronos__menu-nav-2"].play()
                self.index = (self.index - 1) % self.option_length
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.pressed_enter()
            elif event.key in (pg.K_x, pg.K_ESCAPE):
                self.pressed_exit()

    def update(self, keys, now):
        pass

    def pressed_enter(self):
        pass

    def pressed_exit(self):
        pass


class BidirectionalMenu(state_machine.State):
    """Base class for basic bi-directional menus."""

    def __init__(self, option_lengths):
        state_machine.State.__init__(self)
        self.option_lengths = option_lengths
        self.index = [0, 0]

    def get_event(self, event):
        """
        Generic event getter for scrolling through menus.
        """
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.pressed_enter()
            elif event.key in (pg.K_x, pg.K_ESCAPE):
                self.pressed_exit()
            elif event.key in config.DEFAULT_CONTROLS_1:
                # config.SFX["dj-chronos__menu-nav-2"].play()
                self.move_on_grid(event)


    def move_on_grid(self, event):
        """Called when user moves the selection cursor with the arrow keys."""
        direction = config.DEFAULT_CONTROLS_1[event.key]
        vector = config.DIRECTIONS[direction]
        self.index[0] = (self.index[0] + vector[0]) % self.option_lengths[0]
        self.index[1] = (self.index[1] + vector[1]) % self.option_lengths[1]

    def update(self, keys, now):
        pass

    def pressed_enter(self):
        pass

    def pressed_exit(self):
        pass


def render_font(font, msg, color, center):
    """Return the rendered font surface and its rect centered on center."""
    msg = font.render(msg, 1, color)
    rect = msg.get_rect(center=center)
    return msg, rect


def make_text_list(font, strings, color, start, space, vertical=True, perp_center=None):
    """
    Takes a list of strings and returns a list of
    (rendered_surface, rect) tuples. The rects are centered on the screen
    and their y coordinates begin at starty, with y_space pixels between
    each line.
    """
    if vertical:
        perp_center = perp_center if perp_center else config.SCREEN_RECT.centerx
    else:
        perp_center = perp_center if perp_center else config.SCREEN_RECT.centery
    rendered_text = []
    for i, string in enumerate(strings):
        if vertical:
            msg_center = (perp_center, start + i * space)
        else:
            msg_center = (start + i * space, perp_center)
        msg_data = render_font(font, string, color, msg_center)
        rendered_text.append(msg_data)
    return rendered_text


def make_options(font, choices, start, space, vertical=True, perp_center=None):
    """
    Makes prerendered (text,rect) tuples for basic text menus.
    Both selected and non-selected versions are made of each.
    Used by both the Option and Confirm menus.
    """
    options = {}
    args = [font, choices, colors.WHITE, start, space, vertical, perp_center]
    options["inactive"] = make_text_list(*args)
    args = [font, choices, colors.BLUE, start, space, vertical, perp_center]
    options["active"] = make_text_list(*args)
    return options
