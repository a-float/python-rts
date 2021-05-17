import pygame as pg
from typing import Dict
from data.components.tile import Tile
from data import colors
from data import config
from data.components.path import PathBuilder
from data.components.building import Barracks, Tower, Market


class Player:
    """Class that allows the player to interact with the Board"""

    def __init__(self, player_no, tile, board):
        self.is_dead: bool = False
        self.gold: int = 0
        self.income: int = 5
        self.tile: Tile = tile
        self.id: int = player_no
        self.color: (int, int, int) = config.PLAYER_COLORS[player_no]
        self.marker = PlayerMarker(self.color, tile.rect.center)
        self.board = board
        self.controls: Dict[str, str] = config.CONTROLS[player_no]
        self.path_builder = PathBuilder(self)
        self.upgrade_mode: bool = False
        self.build_mode = False
        self.menu_image = None
        self.menu_rect = None

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.controls is None:
                # TODO controls for player no 3 and 4
                return
            if event.key in self.controls.keys():
                command = self.controls[event.key]

                if self.upgrade_mode:
                    self.upgrade_building(command)
                elif self.path_builder.is_active:
                    self.path_builder.handle_command(command)
                elif self.build_mode:
                    self.parse_build_command(command)
                else:
                    if command == 'action':
                        # print("Player has performed an action")
                        if self.tile.owner == self and self.tile.building is None:
                            self.building_action()
                        elif self.tile.owner == self and self.tile.building is not None:
                            if isinstance(self.tile.building, Barracks):
                                self.path_builder.init_path()
                            else:
                                self.tile.building.active()
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

    def building_action(self):
        self.build_mode = True
        self.menu_image = config.gfx['utils']['build_menu']
        self.menu_image = pg.transform.scale(self.menu_image, (config.TILE_SPRITE_SIZE * 5,) * 2)
                                                                            # todo change menu place
        self.menu_rect = self.tile.rect

    def parse_build_command(self, command):
        if command == 'up':
            self.build('barracks')
            self.build_mode = False
        elif command == 'left':
            self.build('market')
            self.build_mode = False
        elif command == 'right':
            self.build('tower')
            self.build_mode = False
        elif command == 'down':
            self.build_mode = False

    def add_gold(self, amount):
        self.gold += amount
        # if self.id == 1:
        #     print(f"Players {self.id} gold = {self.gold}")

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
                self.upgrade_mode = True
                if isinstance(self.tile.building, Market):
                    self.menu_image = config.gfx['utils']['market_upgrade_menu']
                    self.menu_image = pg.transform.scale(self.menu_image, (config.TILE_SPRITE_SIZE * 5,) * 2)
                                                                            # todo change menu place
                    self.menu_rect = self.tile.rect
                elif isinstance(self.tile.building, Tower):
                    self.menu_image = config.gfx['utils']['tower_upgrade_menu']
                    self.menu_image = pg.transform.scale(self.menu_image, (config.TILE_SPRITE_SIZE * 5,) * 2)
                                                                            # todo change menu place
                    self.menu_rect = self.tile.rect
                elif isinstance(self.tile.building, Barracks):
                    self.menu_image = config.gfx['utils']['barracks_upgrade_menu']
                    self.menu_image = pg.transform.scale(self.menu_image, (config.TILE_SPRITE_SIZE * 5,) * 2)
                                                                            # todo change menu place
                    self.menu_rect = self.tile.rect

            else:
                print("Can't upgrade building")
        else:
            print(f"Player {self.id} doesn't have building on this tile!")

    def upgrade_building(self, command):
        upgrade_types = self.tile.building.get_upgrade_types()
        if command == 'left':
            self.tile.building.upgrade(upgrade_types[0])
            self.upgrade_mode = False
        elif command == 'right':
            self.tile.building.upgrade(upgrade_types[1])
            self.upgrade_mode = False
        elif command == 'down':
            self.upgrade_mode = False
        else:
            print("Wrong upgrade command")

    def draw_marker(self, surface):
        surface.blit(self.marker.image, self.marker.rect)

    def draw_menus(self, surface):
        if self.build_mode or self.upgrade_mode:
            surface.blit(self.menu_image, self.menu_rect)


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
