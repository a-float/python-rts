import pygame as pg
from data import colors, config
from data.components.tile import Tile
from itertools import product


class Map:
    """Manages all the tiles"""

    def __init__(self):
        self.tile_group = pg.sprite.Group()
        self.tiles = {}
        self.board_size = None

    def initialize(self, board_shape):
        """ reads the shape of the map from the file for example
        ...3...
        ..ooo..
        .1ooo2.
        would result in a pyramid shaped map with players starting at the edges
        TODO add obstacles etc
        TODO actually add everything lol
        """

        def _find_neighbours(t_pos):
            results = {}
            for name, vec in config.DIRECTIONS.items():
                n_pos = (vec[0] + t_pos[0], vec[1] + t_pos[1])
                for axis, coord in enumerate(n_pos):
                    if coord < 0 or coord > self.board_size[axis]-1:
                        results[name] = None
                        break
                else:
                    results[name] = n_pos
            return results

        self.board_size = (5, 5)
        for x in range(self.board_size[0]):
            for y in range(self.board_size[1]):
                self.tiles[(x, y)] = Tile()

        for pos, tile in self.tiles.items():
            tile.setup((pos[0] * config.TILE_SIZE, pos[1] * config.TILE_SIZE), _find_neighbours(pos))
            print(tile.rect)
        self.tile_group.add(*self.tiles.values())

    def update(self):
        self.tile_group.update()

    def draw(self, surface, interpolate):
        surface.fill(colors.WHITE)
        self.tile_group.draw(surface)
