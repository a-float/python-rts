import os
import pygame as pg
import threading
from project import state_machine, config

TIME_PER_UPDATE = 16.0  # ~= 1000ms/60f = 62.5fps


class Control(object):
    """
    Control class for entire project. Contains the game loop, and
    the event_loop which passes events to States as needed.
    """

    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.caption = caption
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.fps_visible = True
        self.now = 0.0
        self.keys = pg.key.get_pressed()
        self.state_machine = state_machine.StateMachine()

    def update(self):
        """Updates the currently active state."""
        self.now = pg.time.get_ticks()
        self.state_machine.update(self.keys, self.now)

    def draw(self, interpolate):
        if not self.state_machine.state.done:
            self.state_machine.draw(self.screen, interpolate)
            pg.display.update()
            self.show_fps()

    def event_loop(self):
        """
        Process all events and pass them down to the state_machine.
        The f5 key globally turns on/off the display of FPS in the caption
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.state_machine.state.cleanup()
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            self.state_machine.get_event(event)

    def toggle_show_fps(self, key):
        """Press f5 to turn on/off displaying the framerate in the caption."""
        if key == pg.K_F5:
            self.fps_visible = not self.fps_visible
            if not self.fps_visible:
                pg.display.set_caption(self.caption)

    def show_fps(self):
        """ Display the current FPS in the window handle if fps_visible is True."""
        if self.fps_visible:
            fps = self.clock.get_fps()
            with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
            pg.display.set_caption(with_fps)

    def main(self):
        """Main loop for entire program. Uses a constant timestamp."""
        lag = 0.0
        while not self.done:
            lag += self.clock.tick(self.fps)
            self.event_loop()
            while lag >= TIME_PER_UPDATE:
                self.update()
                lag -= TIME_PER_UPDATE
            self.draw(lag / TIME_PER_UPDATE)


# Resource loading functions.
def load_all_gfx(directory, colorkey, accept=(".png", ".jpg", ".bmp")):
    """
    Load all graphics with extensions in the accept argument.  If alpha
    transparency is found in the image the image will be converted using
    convert_alpha().  If no alpha transparency is detected image will be
    converted using convert() and colorkey will be set to colorkey.
    """
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def dist_sq(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def pos_to_relative(pos):
    """
    eg (200px, 300px) -> (0.2, 0.4) (20% of the width from the left, 40% of the height from the top)
    :param pos: absolute valued position
    :return: position relative to the window size
    """
    return pos[0] / config.SCREEN_SIZE[0], pos[1] / config.SCREEN_SIZE[1]


def pos_to_absolute(pos):
    """
    :param pos: position relative to the window size
    :return: absolute valued position
    """
    return pos[0]*config.WIDTH, pos[1]*config.HEIGHT


def get_health_surface(health_ratio, width, height):
    health_ratio = max(0, health_ratio)
    health_img = pg.Surface((int(health_ratio*width), int(height)))
    col = [250 * (1 - health_ratio), health_ratio * 250, 0]
    health_img.fill(col)
    return health_img


class Animation:
    """Simplifies animation handling"""
    def __init__(self, frames, fps):
        self.frames = frames
        self.fps = fps
        self.frame = 0
        self.timer = None

    def get_next_frame(self, now):
        if not self.timer:
            self.timer = now
        if now - self.timer > 1000.0 / self.fps:
            self.frame = (self.frame + 1) % len(self.frames)
            self.timer = now
        return self.frames[self.frame]
