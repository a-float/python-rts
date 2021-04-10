import pygame as pg
from data import colors, config
from data.components.tile import Tile
from data.components.player import Player

class Map:
    """Manages all the tiles"""

    def __init__(self):
        self.tile_group = pg.sprite.Group()
        self.tiles = {}
        self.board_size = None
        self.players = {}

    def initialize(self, board_string):
        """ reads the shape of the map from the file for example
        ...3...
        ..ooo..
        .1ooo2.
        would result in a pyramid shaped map with players starting at the edges
        """
        def _find_neighbours(t_pos):
            results = {}
            for name, vec in config.DIRECTIONS.items():
                n_pos = (vec[0] + t_pos[0], vec[1] + t_pos[1])
                if n_pos in self.tiles.keys():
                    results[name] = n_pos
                else:
                    results[name] = None
            return results

        self.board_size = (board_string.find('\n'), board_string.count('\n'))
        print("The board size is:", self.board_size)

        rows = board_string.split('\n')[:-1]  # remove the last empty row
        for y, row in enumerate(rows):
            if len(row) != self.board_size[0]:
                raise ValueError(f'Invalid board string. Faulty row: {y}. "{row}"')
            for x, char in enumerate(row):
                if char != '.':
                    new_tile = Tile()
                    if char in ['1', '2', '3', '4']:
                        new_tile.set_owner(self.get_player(int(char)))
                    self.tiles[(x, y)] = new_tile

        for pos, tile in self.tiles.items():
            tile.setup((pos[0] * config.TILE_SIZE, pos[1] * config.TILE_SIZE), _find_neighbours(pos))
        self.tile_group.add(*self.tiles.values())

    def update(self):
        self.tile_group.update()

    def draw(self, surface, interpolate):
        surface.fill(colors.WHITE)
        self.tile_group.draw(surface)

    def get_player(self, player_no):
        if player_no not in self.players.keys():
            self.players[player_no] = Player(player_no)
        return self.players[player_no]

