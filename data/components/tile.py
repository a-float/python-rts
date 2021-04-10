import pygame as pg
import data.config as config
from data import colors


class Tile(pg.sprite.Sprite):
    """
    Class representing a single in game tile.
    It knows about it's neighbours, and the building it holds
    """

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.neighbours = {}  # a dict passed by the map
        self.owner = None
        self.building = None
        self.image = pg.Surface((config.TILE_SPRITE_SIZE, config.TILE_SPRITE_SIZE))
        self.image.fill(colors.LIGHT_GRAY)
        self.rect = self.image.get_rect(topleft=pos)

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def build(self, building_name):
        """gets the building object from a dict? from config? from building.py?"""
        pass

    def set_owner(self, player):
        self.owner = player
        self.image.fill(colors.LIGHT_GRAY if self.owner is None else self.owner.color)

    def update_borders(self):
        """called when building is created or destroyed
        influences the neighbours"""
        pass

    def update(self):  # is called by the map
        pass

    def draw(self, surface):  # is not called. Don't know why?
        """called by the map"""
        print("tile drawn")
        surface.blit(self.image, self.rect)