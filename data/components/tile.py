import pygame as pg
import data.config as config
from data.colors import *


class Tile(pg.sprite.Sprite):
    """
    Class representing a single in game tile.
    It knows about it's neighbours, and the building it holds
    """

    def __init__(self, neighbours):
        pg.sprite.Sprite.__init__(self)
        self.neighbours = neighbours  # a dict passed by the map
        self.owner = None
        self.building = None

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pg.Surface([config.WIDTH // 10, config.HEIGHT // 10])
        self.image.fill(WHITE)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

    def build(self, building_name):
        """gets the building object from a dict? and assigns it to itself"""
        pass

    def draw(self, screen):
        """called by the map"""
        pass

    def update_borders(self):
        """called when building is created or destroyed
        influences the neighbours"""
        pass
