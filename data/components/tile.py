import data.config as config
from data.networking.packable import Packable
from data import colors
from data.components import building
from data.components.soldier import *


class Tile(pg.sprite.Sprite, Packable):
    """
    Class representing a single in game tile.
    It knows about it's neighbours, and the building it holds
    """

    def pack(self):
        return {
            'owner': self.owner.id if self.owner else None,
            'building': self.building.pack() if self.building else None
        }

    def unpack(self, data):
        # print('Tile unpacking data: ', data)
        self.owner = self.board.game.players[data['owner']] if data['owner'] else None
        # if there's a building and there should be one, destroy it
        if self.building and not data['building']:
            self.building.destroy()
        # if there's a building of the same type. Update the building data
        elif self.building and self.building.name == data['building']['name']:
            self.building.unpack(data['building'])
        # if there is a building of a different type
        elif data['building']:
            if self.building:
                self.building.destroy()
            building_name = data['building']['name']
            self.board.build_on_tile(self, building_name)
            self.building.unpack(data['building'])

    def __init__(self, pos, index, board, sprite_size):
        pg.sprite.Sprite.__init__(self)
        self.neighbours = {}  # a dict passed by the map
        self.owner = None  # Player object
        self.building = None
        # TODO paths are used only for path crossing prevention is it ok?
        self.paths = {  # paths of each player that lie on this tile. Used when CAN_PATHS_CROSS == False
            1: None,
            2: None,
            3: None,
            4: None
        }
        self.index = index  # index of this tile in the board's tile list
        self.image = pg.Surface((sprite_size, sprite_size))
        self.image.fill(colors.LIGHT_GRAY)
        self.ownership = {}  # Dict[Player: int]
        self.rect = self.image.get_rect(topleft=pos)
        self.building_path = False
        self.board = board

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

    def increase_ownership(self, player):
        self.ownership[player] = self.ownership.get(player, 0) + 1

    def decrease_ownership(self, player):
        self.ownership[player] -= 1

    def update_owner(self):
        if self.building is None:
            ranking = sorted(list(self.ownership.items()), key=lambda x: -x[1])
            # if no one has ownership the tile belongs to no one
            if ranking[0][1] == 0:
                self.owner = None
            else:
                self.owner = ranking[0][0]
        self.image.fill(colors.LIGHT_GRAY if self.owner is None else self.owner.color)
