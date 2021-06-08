from project.components.building import Barracks
import pygame as pg
from project import config
from project.networking import Packable


class Path(pg.sprite.Sprite, Packable):
    def __init__(self, start_tile, player):
        self.image = pg.Surface(config.SCREEN_SIZE)
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        self.rect = self.image.get_rect()
        super().__init__(start_tile.board.path_group)
        self.tiles = []
        self.path_id = start_tile.index  # no two paths can start at the same tile. Used to unpack units online
        self.owner = player
        self.is_destroyed = False
        self.color = tuple([int(0.8 * x) for x in self.owner.color])
        self.add_tile(start_tile)

    def add_tile(self, tile):
        self.tiles.append(tile)
        tile.paths[self.owner.id] = self
        self.update_image()

    def pop_tile(self):
        tile = self.tiles.pop()
        tile.paths[self.owner.id] = None
        self.update_image()

    def destroy(self):
        self.is_destroyed = True
        for tile in self.tiles:
            tile.paths[self.owner.id] = None
            if self.tiles[0].building:
                self.tiles[0].building.set_path(None)
        self.kill()

    def update_image(self):
        self.image.fill(config.COLORKEY)
        for i in range(len(self.tiles)-1):
            src = self.tiles[i]
            to = self.tiles[i+1]
            pg.draw.line(self.image, self.color, src.rect.center, to.rect.center, width=5)

    def pack(self):
        return {
            'tile_indices': [tile.index for tile in self.tiles],
            'owner_id': self.owner.id,
            'path_id': self.path_id
        }

    def unpack(self, data):
        self.path_id = data['path_id']


class PathBuilder:
    def __init__(self, player):
        self.prev_directions = []
        self.owner = player
        self.is_active = False
        self.path = None

    def can_build_path_on_tile(self, tile):
        if tile is None:
            return False
        if config.CAN_PATHS_CROSS:
            return True
        else:  # paths can't cross
            if tile.paths[self.owner.id] is None:
                return True
        return False

    def init_path(self):
        tile = self.owner.tile
        if tile.owner == self.owner and isinstance(tile.building, Barracks):
            if tile.building.path is not None:
                tile.building.path.destroy()
                tile.building.set_path(None)
            print("Started Building a Path")
            self.path = Path(tile, self.owner)  # has to be a new one
            tile.paths[self.owner.id] = self.path
            self.prev_directions = []
            self.is_active = True
        else:
            print(f"Player {self.owner.id} can't start building path on this tile!")

    def undo_path(self):
        self.path.pop_tile()
        self.prev_directions.pop()
        # print(f"Backtracking building of the path")

    def handle_command(self, command):
        if self.path.tiles[0].building is None:  # the barracks were destroyed while building the path
            self.cancel_path()
        if command in {'up', 'right', 'left', 'down'}:
            target_tile = self.owner.tile.neighbours[command]
            if len(self.prev_directions) > 0 and \
                    config.OPPOSITE_DIRECTIONS[command] == self.prev_directions[-1]:  # trying to move backwards
                self.undo_path()
                self.owner.move(command)
            elif self.can_build_path_on_tile(target_tile):
                self.path.add_tile(target_tile)
                self.prev_directions.append(command)
                self.owner.move(command)
        elif command == 'action':
            self.finish_path()
        elif command == 'upgrade':  # upgrade command is default command for canceling building path
            self.cancel_path()

    def cancel_path(self):
        self.is_active = False
        self.path.destroy()
        print("Path Building Cancelled")

    def finish_path(self):
        if len(self.path.tiles) == 1:  # path start at the barracks but doesnt go anywhere
            self.cancel_path()
        else:
            self.is_active = False
            self.path.tiles[0].building.set_path(self.path)
        print("Path Building Finished")
