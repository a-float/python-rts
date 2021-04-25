from queue import LifoQueue
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

    def __init__(self, source, target, tile, color):
        super().__init__()
        self.source = source
        self.target = target
        self.tile = tile
        self.color = tuple([int(0.8 * x) for x in color])
        # self.image = None
        # self.rect = None

    def draw(self, surface):
        if self.target is not None:  # we have n tile to stretch the path over, but just n-1 gaps between the tiles
            # noinspection PyTypeChecker
            pg.draw.line(surface, self.color, self.tile.rect.center, self.target.tile.rect.center, width=5)


class PathBuilder:
    def __init__(self, player):
        self.paths_queue = LifoQueue()  # i don't know if it belongs here. I think its mainly for multithreading
        self.prev_directions = []
        self.owner = player
        self.is_active = False
        self.image = pg.Surface(config.SCREEN_SIZE)
        self.image.convert()
        self.colorkey = (255, 0, 255)
        self.image.set_colorkey(self.colorkey)
        self.source_tile = None

    def connect_tile(self, tile):
        if self.can_build_here(tile):
            if not self.paths_queue.empty():
                last_path = self.paths_queue.get()
                new_path = Path(last_path, None, tile, self.owner.color)  # creates the new path
                tile.paths[self.owner.id] = new_path  # updates the previous one's target
                last_path.target = new_path
                self.paths_queue.put(last_path)  # put everything back into the queue
            else:
                new_path = Path(None, None, tile, self.owner.color)  # the first path
                tile.paths[self.owner.id] = new_path
            self.paths_queue.put(new_path)
            print("Successfully added path to the path_builders queue")
        else:
            raise ValueError("Can't build path here")

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
            print("Started Building a Path")
            try:
                self.paths_queue = LifoQueue()  # clears the queue
                self.connect_tile(tile)  # can fail
                self.prev_directions = []
                self.is_active = True
                self.source_tile = tile
            except ValueError:
                print("Can't build path here")
        else:
            print(f"Player {self.owner.id} can't start building path on this tile!")

    def undo_path(self):
        if self.paths_queue.empty():
            raise IndexError('Cannot remove path from an empty queue')
        last_path = self.paths_queue.get()  # remove the last path
        last_path.tile.paths[self.owner.id] = None
        if not self.paths_queue.empty():
            prev_path = self.paths_queue.get()  # update the second to last path's target
            prev_path.target = None
            self.paths_queue.put(prev_path)
        self.prev_directions.pop()
        print(f"Backtracking building of the path")

    def handle_command(self, command):
        if command in {'up', 'right', 'left', 'down'}:
            if len(self.prev_directions) > 0 and \
                    config.OPPOSITE_DIRECTIONS[command] == self.prev_directions[-1]:  # trying to move backwards
                self.undo_path()
                self.owner.move(command)
                self.update_path_surface()
            else:  # moving in another direction
                try:
                    self.connect_tile(self.owner.tile.neighbours[command])
                    self.prev_directions.append(command)
                    self.owner.move(command)
                    self.update_path_surface()
                except ValueError:
                    print("Can't build path here")
        elif command == 'action':
            self.finish_path()
        elif command == 'upgrade':  # upgrade command is default command for canceling building path
            self.cancel_path()

    def cancel_path(self):
        self.is_active = False
        while not self.paths_queue.empty():
            path = self.paths_queue.get()
            path.tile.paths[self.owner.id] = None
        del self.owner.path_surfaces[self.source_tile]
        print("Path Building Cancelled")

    def finish_path(self):
        self.is_active = False
        self.update_path_surface()
        self.source_tile.building.can_release = True

    def update_path_surface(self):
        self.image.fill(self.colorkey)
        path = self.paths_queue.get()
        self.paths_queue.put(path)
        while path is not None:
            path.draw(self.image)
            path = path.source
        self.owner.tile.board.path_surfaces[self.source_tile] = self.image
