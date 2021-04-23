from queue import LifoQueue
from data.components.building import Barracks, Path


class PathBuilder:
    def __init__(self, player_id):
        self.tiles_queue = LifoQueue()
        self.player_id = player_id
        self.source = None

    def add_tile(self, tile):
        if self.can_build_here(tile):
            if not self.tiles_queue.empty():
                last_tile = self.tiles_queue.get()
                last_tile.paths[self.player_id].target = tile
                self.tiles_queue.put(last_tile)
            self.tiles_queue.put(tile)
            tile.paths[self.player_id] = Path(self.source, None)
            self.source = tile
            print("Successfully added tile to path_builders queue")
        else:
            raise ValueError("Can't build path here")

    def get_tile(self):
        return self.tiles_queue.get()

    def can_build_here(self, tile):
        if tile is None:
            return False
        if tile.owner == self.player_id and tile.building is not None and not isinstance(tile.building, Barracks):
            return False
        if tile.paths[self.player_id] is not None:  # paths cant cross (for now), it doesnt allow path cycles
            return False
        return True

    def cancel_path(self):
        s = None
        while self.tiles_queue.empty():
            s = self.tiles_queue.get()
            s.paths[self.player_id] = None
        print("Path Building Cancelled")

    def finish_path(self):
        s = None
        while not self.tiles_queue.empty():
            s = self.tiles_queue.get()
        if s is not None:
            s.building.path = s.paths[self.player_id]
        print("Path Has Been Built")
