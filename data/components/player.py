import pygame as pg
from data.colors import *
import data.config as config
from data.components.building import Barracks


class Player:
    """Class that allows the player to interact with the Board"""

    def __init__(self, player_no, tile, board):
        self.base_color = RED
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

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.controls is None:
                # TODO controls for player no 3 and 4
                return
            if event.key in self.controls.keys():
                command = self.controls[event.key]

                if self.tile.building_path:
                    self.build_path(command)

                elif command == 'action':
                    # print("Player has performed an action")
                    if self.tile.owner == self and self.tile.building is None:
                        print("Performs action")
                    else:
                        print(f"Player {self.id} doesn't have building on this tile!")
                elif command == 'upgrade':
                    if self.tile.owner == self and self.tile.building is not None:
                        print(self.tile.building.get_upgrade_types())
                    else:
                        print(f"Player {self.id} doesn't have building on this tile!")
                elif command == 'build_path':
                    if self.tile.owner == self and self.tile.building is not None \
                            and isinstance(self.tile.building, Barracks):
                        self.tile.building.build_path()
                    else:
                        print(f"Player {self.id} can't start building path on this tile!")
                elif command == 'tower':
                    if self.tile.owner == self and self.tile.building is None:
                        self.board.build_on_tile(self.tile, 'tower')
                    else:
                        print(f"Player {self.id} can't place buildings on this tile!")
                elif command == 'barracks':
                    if self.tile.owner == self and self.tile.building is None:
                        self.board.build_on_tile(self.tile, 'barracks')
                    else:
                        print(f"Player {self.id} can't place buildings on this tile!")
                elif command == 'market':
                    if self.tile.owner == self and self.tile.building is None:
                        self.board.build_on_tile(self.tile, 'market')
                    else:
                        print(f"Player {self.id} can't place buildings on this tile!")
                else:  # it is a movement command
                    if self.tile.neighbours[command] is not None:
                        self.tile = self.tile.neighbours[command]
                        self.marker.set_position(self.tile.rect.center)

    def build_path(self, command):
        if command in {'up', 'right', 'left', 'down'}:
            self.tile.building.add_to_queue(command)
        elif command == 'action':
            self.tile.building.finish_building(self)
        elif command == 'upgrade': # upgrade command is default command for canceling building path
            self.tile.building.finish_building(self, cancel=True)

    
    def draw(self, surface):
        surface.blit(self.marker.image, self.marker.rect)


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
