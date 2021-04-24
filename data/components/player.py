import pygame as pg
from data import colors
from data import config
from data.components.building import Barracks
from data.components.path import PathBuilder


class Player:
    """Class that allows the player to interact with the Board"""

    def __init__(self, player_no, tile, board):
        self.base_color = colors.RED
        self.is_dead = False
        self.controls = config.DEFAULT_CONTROLS_1
        self.gold = 0
        self.income = 5
        self.tile = tile
        self.id = player_no
        self.color = config.PLAYER_COLORS[player_no]
        self.marker = PlayerMarker(self.color, tile.rect.center)
        self.board = board
        self.controls = config.CONTROLS[player_no]
        self.path_builder = PathBuilder(self)
        self.upgrade_mode = False
        self.path_surfaces = {}

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.controls is None:
                # TODO controls for player no 3 and 4
                return
            if event.key in self.controls.keys():
                command = self.controls[event.key]

                if self.upgrade_mode:
                    self.upgrade_building(command)

                if self.path_builder.is_active:
                    self.path_builder.handle_command(command)
                else:
                    if command == 'action':
                        # print("Player has performed an action")
                        if self.tile.owner == self and self.tile.building is None:
                            print("Performs action")
                        else:
                            print(f"Player {self.id} doesn't have building on this tile!")
                    elif command == 'upgrade':
                        self.init_upgrade()
                    elif command == 'start_path':
                        self.path_builder.init_path()
                    elif command in ['tower', 'barracks', 'market']:
                        self.build(command)
                    elif command in config.DIRECTIONS:
                        self.move(command)

    def add_gold(self, amount):
        self.gold += amount
        if self.id == 1:
            print(f"Players {self.id} gold = {self.gold}")

    def build(self, building_name):
        if self.tile.owner == self and self.tile.building is None:
            self.board.build_on_tile(self.tile, building_name)
        else:
            print(f"Player {self.id} can't place buildings on this tile!")

    def move(self, direction):
        if self.tile.neighbours[direction] is not None:
            self.tile = self.tile.neighbours[direction]
            self.marker.set_position(self.tile.rect.center)

    def init_upgrade(self):
        if self.tile.owner == self and self.tile.building is not None:
            upgrade_types = self.tile.building.get_upgrade_types()
            if len(upgrade_types) > 0:
                print(upgrade_types)
                self.upgrade_mode = True
            else:
                print("Can't upgrade building")
        else:
            print(f"Player {self.id} doesn't have building on this tile!")

    def upgrade_building(self, command):
        upgrade_types = self.tile.building.get_upgrade_types()
        if command == 'barracks':
            self.tile.building.upgrade(upgrade_types[0])
            self.upgrade_mode = False
        elif command == 'market':
            self.tile.building.upgrade(upgrade_types[1])
            self.upgrade_mode = False
        elif command == 'action':
            self.upgrade_mode = False
        else:
            print("Wrong upgrade command")

    def draw_marker(self, surface):
        surface.blit(self.marker.image, self.marker.rect)

    def draw_paths(self, surface):  # TODO maybe the paths should be stored in the board? :C
        for img in self.path_surfaces.values():
            surface.blit(img, img.get_rect())


class PlayerMarker(pg.sprite.Sprite):
    # maybe it could be stored inside of the Player
    def __init__(self, color, tile_center):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE, config.TILE_SIZE))
        self.image.fill(color)
        self.image.set_alpha(150)  # applies soma alpha
        self.rect = self.image.get_rect(center=tile_center)

    def set_position(self, new_center):
        self.rect.center = new_center
