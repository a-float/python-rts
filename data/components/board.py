import pygame as pg
from data import colors, config
from data.components.tile import Tile
from data.components.player import Player


class Board:
    """Manages all the tiles"""

    def __init__(self):
        self.tile_group = pg.sprite.Group()
        self.building_group = pg.sprite.Group()
        self.tiles = {}
        self.board_size = None
        self.players = {}

    def _find_neighbours(self, tile_pos):
        results = {}
        for name, vec in config.DIRECTIONS.items():
            n_pos = (vec[0] + tile_pos[0], vec[1] + tile_pos[1])
            if n_pos in self.tiles.keys():
                results[name] = self.tiles[n_pos]
            else:
                results[name] = None
        return results

    def initialize(self, board_string):
        """ reads the shape of the map from the file for example """
        self.board_size = (board_string.find('\n'), board_string.count('\n'))
        print("The board size is:", self.board_size)
        # figure out where to draw the tiles to center them in the window
        offset_x = config.WIDTH/2 - self.board_size[0]*config.TILE_SIZE//2
        offset_y = config.HEIGHT / 2 - self.board_size[1] * config.TILE_SIZE // 2

        castle_tiles = []
        rows = board_string.split('\n')[:-1]  # remove the last empty row
        for y, row in enumerate(rows):
            if len(row) != self.board_size[0]:
                raise ValueError(f'Invalid board string. Faulty row: {y}. "{row}"')
            for x, char in enumerate(row):
                if char != '.':
                    new_tile = Tile((offset_x+x * config.TILE_SIZE, offset_y+y*config.TILE_SIZE))
                    if char in ['1', '2', '3', '4']: # TODO check if each of the numbers appears once
                        new_tile.owner = self.create_player(int(char), new_tile)
                        castle_tiles.append(new_tile) # castles are bulid after the neighbours are set
                    self.tiles[(x, y)] = new_tile

        for pos, tile in self.tiles.items():
            tile.set_neighbours(self._find_neighbours(pos))
        self.tile_group.add(*self.tiles.values())

        for tile in castle_tiles:
            self.build_on_tile(tile, 'castle')

    def get_tile(self, tile_pos):
        return self.tiles.get(tile_pos, None)

    def create_player(self, player_no, start_tile):
        """ Creates and returns the newly created player """
        if player_no in self.players.keys():
            # TODO should it be a RuntimeError?
            raise RuntimeError(f"Can't create player no {player_no} as it already exists.")
        self.players[player_no] = Player(player_no, start_tile, self)
        return self.players[player_no]

    def get_player(self, player_no):
        return self.players.get(player_no, None)

    def build_on_tile(self, tile, builiding_name):
        new_building = tile.build(builiding_name)
        if new_building is not None:
            self.building_group.add(new_building)

    def handle_event(self, event):
        for p in self.players.values():
            p.handle_event(event)

    def update(self):
        self.tile_group.update()

    def draw(self, surface, interpolate):
        surface.fill(colors.WHITE)
        for p in self.players.values():
            p.draw(surface)
        self.tile_group.draw(surface)
        self.building_group.draw(surface)
