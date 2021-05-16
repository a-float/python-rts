"""
Contains functionality for uni and bidirectional menus as well as for the board preview and text field element.
"""

import pygame as pg
import typing
from . import config, state_machine, colors
from data.components.board import Board


class BasicMenu(state_machine.State):
    """Base class for basic uni-directional menus."""

    def __init__(self, option_length):
        super().__init__()
        self.option_length = option_length
        self.index = 0
        self.dirty = True

    def get_event(self, event):
        """
        Generic event getter for scrolling through menus.
        """
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_DOWN, pg.K_RIGHT):
                # config.SFX["dj-chronos__menu-nav-2"].play()
                self.index = (self.index + 1) % self.option_length
                self._on_move()
            elif event.key in (pg.K_UP, pg.K_LEFT):
                # config.SFX["dj-chronos__menu-nav-2"].play()
                self.index = (self.index - 1) % self.option_length
                self._on_move()
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.pressed_enter()
            elif event.key in (pg.K_x, pg.K_ESCAPE):
                self.pressed_exit()

    def _on_move(self):
        self.dirty = True

    def draw(self, screen, interpolate):
        if self.dirty:
            self.dirty = False
            self._draw(screen, interpolate)

    def _draw(self, screen, interpolate):
        pass

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


def render_font(font, msg, color, center) -> [pg.Surface, pg.Rect]:
    """Return the rendered font surface and its rect centered on center."""
    msg = font.render(msg, 1, color)
    rect = msg.get_rect(center=center)
    return msg, rect


def make_text_list(font, strings, colors, start, space, vertical=True, perp_center=None):
    """
    Takes a list of strings and returns a list of
    (rendered_surface, rect) tuples. The rects are centered on the screen
    and their y coordinates begin at starty, with y_space pixels between  #TODO update the description
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
        color = colors[i] if type(colors) == list else colors  # TODO what if color is passed as a list [int, int, int]
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


class BoardPreview:
    def __init__(self, bots_no, players_no, size=(300, 200)):
        self.board = Board()
        self.preview_size = size
        self.maps = list(config.MAPS.items())
        self.map_index = 0
        self.current_map = self.maps[0]
        self.players_no = players_no
        self.bots_no = bots_no
        self.rendered = {}

    def draw(self, surface):
        surface.blit(*self.rendered['map_name'])
        surface.blit(*self.rendered['preview'])
        surface.blit(*self.rendered['map_help'])

    def change_map(self, diff):
        self.map_index = (self.map_index + diff) % len(self.maps)
        self.current_map = self.maps[self.map_index]
        self.board.clear()
        self.board.initialize(self.get_settings())

        center_x, center_y = config.SCREEN_RECT.center

        surface = pg.Surface(config.SCREEN_SIZE)
        surface.fill(colors.WHITE)
        self.board.draw(surface, 0)
        preview = pg.transform.scale(surface, self.preview_size)
        preview_x = max(35 + self.preview_size[0] * 0.5, center_x - self.preview_size[0] * 0.5 - 50)
        preview_rect = preview.get_rect(center=(preview_x, center_y))
        self.rendered['preview'] = (preview, preview_rect)

        map_name = config.FONT_SMALL.render(self.current_map[0], 1, colors.BLACK)
        map_name_rect = map_name.get_rect(center=(preview_x, center_y - self.preview_size[1] * 0.5 - 30))
        self.rendered['map_name'] = (map_name, map_name_rect)

        map_help_name = config.FONT_TINY.render('Press a or d to change the selected map', 1, colors.BLACK)
        map_help_rect = map_help_name.get_rect(center=(preview_x, center_y + self.preview_size[1] * 0.5 + 15))
        self.rendered['map_help'] = (map_help_name, map_help_rect)  # TODO this should be in render but whatever

    def clear(self):
        self.board.clear()

    def get_settings(self):
        return {
            'players_no': self.players_no,
            'bots_no': self.bots_no,
            'map': self.current_map
        }

    def set_player_counts(self, new_counts: typing.Dict[str, int]):
        self.players_no = new_counts['players']
        self.bots_no = new_counts['bots']


class TextField(pg.sprite.Sprite):
    def __init__(self, font: pg.font, bg_color: pg.Color, color: pg.Color, size: (int, int), center: (int, int)):
        super().__init__()
        self.image: pg.Surface = pg.Surface(size)
        self.bg_color = bg_color
        self.color = color
        self.rect = self.image.get_rect(center=center)
        self.content: str = ''
        self.active: bool = False
        self.font: pg.font = font
        self.update_image()

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self.on_pressed_enter()
            elif event.key == pg.K_ESCAPE:
                self.on_pressed_exit()
            elif event.key == pg.K_BACKSPACE:
                self.content = self.content[:-1]
            else:
                self.content += event.unicode
            self.update_image()

    def update_image(self):
        self.image.fill(self.bg_color)
        text = self.font.render(self.content, True, self.color)
        # midleft = self.image.get_rect().midleft
        # left_padding = 5
        self.image.blit(text, text.get_rect(center=self.image.get_rect().center))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def on_pressed_enter(self):
        pass

    def on_pressed_exit(self):
        self.active = False

