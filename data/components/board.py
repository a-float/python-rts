from typing import Optional, Tuple, Dict

import pygame as pg
from data import colors, config
from data.components.tile import Tile
from data.components.player import Player
from data.dataclasses import MapConfig


class Board:
    """Manages the tiles"""

    def __init__(self):
        self.tile_group = pg.sprite.Group()
        self.building_group = pg.sprite.Group()
        self.unit_group = pg.sprite.Group()
        self.path_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.board_size = None
        self.settings: Optional[MapConfig] = None

    def _find_neighbours(self, tile_pos):
        results = {}
        for name, vec in config.DIRECTIONS.items():
            n_pos = (vec[0] + tile_pos[0], vec[1] + tile_pos[1])
            if n_pos in self.tiles.keys():
                results[name] = self.tiles[n_pos]
            else:
                results[name] = None
        return results

    def initialize(self, settings: MapConfig, tile_size=config.TILE_SIZE):
        self.settings = settings
        board_string = self.settings.layout
        # reads the shape of the map from the file
        self.board_size = (board_string.find('\n'), board_string.count('\n'))
        # calculate the offsets to draw the board in the center of the screen
        offset_x = config.WIDTH/2 - self.board_size[0]*tile_size//2
        offset_y = config.HEIGHT / 2 - self.board_size[1] * tile_size//2

        players = {}
        castle_tiles = []
        rows = board_string.split('\n')[:-1]  # remove the last empty row
        for y, row in enumerate(rows):
            if len(row) != self.board_size[0]:
                raise ValueError(f'Invalid board string. Faulty row: {y}. "{row}"')
            for x, char in enumerate(row):
                if char != '.':
                    new_tile = Tile((offset_x+x * tile_size, offset_y+y*tile_size), self, tile_size-4)
                    # TODO check if each of the numbers appears once
                    if char in list([str(config.PLAYER_1 + i) for i in range(self.settings.player_no)]):
                        new_tile.owner = self.create_player(players, int(char), new_tile)
                        castle_tiles.append(new_tile)  # castles are built after the neighbours are set
                    self.tiles[(x, y)] = new_tile

        for pos, tile in self.tiles.items():
            tile.set_neighbours(self._find_neighbours(pos))
        self.tile_group.add(*self.tiles.values())

        for tile in castle_tiles:
            self.build_on_tile(tile, 'castle')

        return players

    def get_tile(self, tile_pos):
        return self.tiles.get(tile_pos, None)

    def create_player(self, players, player_no, start_tile):
        """ Creates and returns the newly created player """
        if player_no in players.keys():
            # TODO should it be a RuntimeError?
            raise RuntimeError(f"Can't create player no {player_no} as it already exists.")
        players[player_no] = Player(player_no, start_tile, self)
        return players[player_no]

    def build_on_tile(self, tile, building_name):
        new_building = tile.build(building_name)
        if new_building is not None:
            self.building_group.add(new_building)

    def add_unit(self, unit):
        self.unit_group.add(unit)

    def add_bullet(self, bullet):
        self.bullet_group.add(bullet)

    def update(self, now):
        self.tile_group.update()
        self.unit_group.update()
        self.bullet_group.update()
        for building in self.building_group.sprites():
            building.update(now)

    def clear(self):
        self.tiles = {}
        self.tile_group.empty()
        self.building_group.empty()
        self.path_group.empty()
        self.unit_group.empty()
        self.bullet_group.empty()

    def draw(self, surface, interpolate, draw_health=True):
        self.tile_group.draw(surface)
        self.path_group.draw(surface)

        self.building_group.draw(surface)
        self.unit_group.draw(surface)
        self.bullet_group.draw(surface)

        if draw_health:
            for unit in self.unit_group.sprites():
                unit.draw_health(surface)
            for building in self.building_group.sprites():
                building.draw_health(surface)
