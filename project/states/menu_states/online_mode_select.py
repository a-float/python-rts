from typing import Tuple, Any
import socket

import names
import pygame as pg
from project import menu_utils, config, colors
from project.menu_utils import BasicMenu


class OnlineModeSelect(BasicMenu):
    def __init__(self):
        super().__init__(4)
        center_x, center_y = config.SCREEN_RECT.center
        host, ip = self.get_ip()
        self.notification: Any[Tuple[pg.Surface, pg.Rect]] = None

        self.head_surface = config.FONT_SMALL.render(f'Your ip is: {ip}', True, pg.Color('black'))
        self.head_rect = self.head_surface.get_rect(center=(center_x, center_y * 0.45))

        y_spacing = config.FONT_MED.get_ascent()
        self.options = menu_utils.make_options(config.FONT_MED, ['HOST', 'JOIN'], center_y * 0.8, y_spacing+10,
                                               True, center_x)

        args = [config.FONT_SMALL, colors.WHITE, colors.BLACK, (200, 45), (center_x, center_y * 1.4)]
        self.address_field = menu_utils.TextField(*args)
        self.address_field.content = '127.0.0.1'

        args = [config.FONT_SMALL, colors.WHITE, colors.BLACK, (200, 45), (center_x, center_y * 1.7)]
        self.name_field = menu_utils.TextField(*args)
        self.name_field.content = names.get_first_name()

    def _set_notification(self, notify_text):
        """
        Set the notification attribute. If its not None, it's drawn on the screen
        :param notify_text: The text to draw. If None, set notification to None to not draw it
        """
        if notify_text is None:
            self.notification = None
        else:
            text = config.FONT_SMALL.render(notify_text, 1, pg.Color('red'))
            rect = text.get_rect(centerx=config.WIDTH * 0.5, top=config.HEIGHT * 0.02)
            self.notification = (text, rect)

    def startup(self, now, persistent):
        notify_text = persistent.get('notification', None)
        self._set_notification(notify_text)
        super().startup(now, persistent)

    def cleanup(self):
        self.notification = None
        return super().cleanup()

    def get_event(self, event):
        super().get_event(event)

        def handle_text_field(index, text_field, event):
            if self.index == index:  # the text_field
                text_field.active = True
                text_field.bg_color = colors.BLUE
            else:
                if text_field.active:
                    text_field.active = False
                    text_field.bg_color = colors.WHITE
            text_field.handle_event(event)
            text_field.update_image()

        handle_text_field(2, self.address_field, event)
        handle_text_field(3, self.name_field, event)
        self.dirty = True

    @staticmethod
    def get_ip():
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return hostname, ip_address

    def _draw(self, screen, interpolate):
        screen.fill(config.BACKGROUND_COLOR)

        # if exists, draw the notification
        if self.notification:
            screen.blit(*self.notification)

        # draw the hostname and ip address info
        screen.blit(self.head_surface, self.head_rect)

        # draw the options
        for i, _ in enumerate(self.options):
            which = "active" if i == self.index else "inactive"
            text, rect = self.options[which][i]
            screen.blit(text, rect)

        # draw the text fields
        self.address_field.draw(screen)
        self.name_field.draw(screen)

    def pressed_enter(self):
        if self.index in [0, 1]:
            if self.index == 0:
                self.persist = {'is_host': True}
            elif self.index == 1:
                self.persist = {'is_host': False, 'ip': self.address_field.content}
            self.persist.update({'player_name': self.name_field.content})
            self.next = 'ONLINE_LOBBY'
            self.done = True

    def pressed_exit(self):
        self.next = 'MAIN'
        self.done = True
