import pygame as pg
import data.config as config
from data import colors
from data.components import building
from data.components.soldier import *


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
        self.paths = {
            0: None,
            1: None,
            2: None,
            3: None
        }
        self.image = pg.Surface((config.TILE_SPRITE_SIZE, config.TILE_SPRITE_SIZE))
        self.image.fill(colors.LIGHT_GRAY)
        self.ownership = {}
        self.rect = self.image.get_rect(topleft=pos)
        self.building_path = False

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def build(self, building_name):
        """gets the building object from a dict? from config? from building.py?"""
        self.building = building.BUILDINGS[building_name](self)

        self.increase_ownership(self.owner)
        self.update_owner()

        for n in self.neighbours.values():
            if n is not None:
                n.increase_ownership(self.owner)
                n.update_owner()
        return self.building

    def demolish(self):
        self.board.building_group.remove(self.building)
        self.building = None
        for n in self.neighbours.values():
            if n is not None:
                n.decrease_ownership(self.owner)
                n.update_owner()

    # to jeszcze do poprawy zeby budowac naraz jedna sciezke
    def build_path(self, building_name, source, target):
        self.building = building.Path(source, target)

    def can_build_path_here(self, player): # returns (can_build, is_potentially_end)
        if self.paths[player.id] is None:  # for now none of player's path can cross
            if self.owner == player.id:
                if self.building is not None: # TODO dunno if ok owner == id
                    return False, False
                else:
                    return True, False
            else:
                if self.building is not None:
                    return True, True
                else:
                    return True, False
        else:
            return False, False



    def get_soldier(self):
        if self.building is not None and isinstance(self.building, (building.Barracks, building.Path)):
            return self.building.soldier
        else:
            return None

    def increase_ownership(self, player):
        self.ownership[player] = self.ownership.get(player, 0) + 1

    def decrease_ownership(self, player):
        self.ownership[player] -= 1
        # if self.ownership[player] == 0:
        #     del self.ownership[player]

    def update_owner(self):
        if self.building is None:
            ranking = sorted(list(self.ownership.items()), key=lambda x: -x[1])
            # if no one has ownership the tile belongs to noone
            if ranking[0][1] == 0:
                self.owner = None
            else:
                self.owner = ranking[0][0]
        self.image.fill(colors.LIGHT_GRAY if self.owner is None else self.owner.color)

    def update(self):  # is called by the map
        pass
