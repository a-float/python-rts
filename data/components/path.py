from queue import LifoQueue
from typing import Tuple

from data.components.building import Barracks
import pygame as pg
from data import config, colors


class Path(pg.sprite.Sprite):  # todo its not being a sprite rn, just drawing a line
    # todo if second path of same player is built, first disappears
    """
    Creates a double linked list. The first one has None source and the last one None target
    Each points to the tile it lies on.
    Used to display the paths and guide the soldiers
    """

    def __init__(self, start_tile, player):
        super().__init__(start_tile.board.path_group)
        self.tiles = []
        self.owner = player
        self.color = tuple([int(0.8 * x) for x in self.owner.color])
        self.image = pg.Surface(config.SCREEN_SIZE)
        self.image.set_colorkey(config.COLORKEY)
        self.image.fill(config.COLORKEY)
        self.rect = self.image.get_rect()
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
        for tile in self.tiles:
            tile.paths[self.owner.id] = None
        self.kill()

    def update_image(self):
        self.image.fill(config.COLORKEY)
        for i in range(len(self.tiles)-1):
            src = self.tiles[i]
            to = self.tiles[i+1]
            pg.draw.line(self.image, self.color, src.rect.center, to.rect.center, width=5)


class PathBuilder:
    def __init__(self, player):
        self.prev_directions = []
        self.owner = player
        self.is_active = False
        self.path = None

    def can_build_here(self, tile):
        if tile is None:
            return False
        if tile.owner == self.owner.id and tile.building is not None and not isinstance(tile.building, Barracks):
            return False
        if tile.paths[self.owner.id] is not None:  # paths cant cross (for now), it doesnt allow path cycles
            return False
        return True

    def init_path(self):
        tile = self.owner.tile
        print(type(tile.building))
        if tile.owner == self.owner and isinstance(tile.building, Barracks):
            if tile.paths[self.owner.id] is not None:
                tile.paths[self.owner.id].destroy()
                tile.building.can_release = False
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
        print(f"Backtracking building of the path")

    def handle_command(self, command):
        if self.path.tiles[0].building is None:  # the barracks were destroyed while building the path
            self.cancel_path()
        if command in {'up', 'right', 'left', 'down'}:
            target_tile = self.owner.tile.neighbours[command]
            if len(self.prev_directions) > 0 and \
                    config.OPPOSITE_DIRECTIONS[command] == self.prev_directions[-1]:  # trying to move backwards
                self.undo_path()
                self.owner.move(command)
            elif self.can_build_here(target_tile):
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
            self.path.tiles[0].building.can_release = True
        print("Path Building Finished")
