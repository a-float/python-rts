import pygame as pg
from typing import Dict, List, Any
from data.components.tile import Tile
from data import config
from data.components.path import PathBuilder
from data.components import building
from data.components.building_stats import BUILDING_DATA
from data.components.building import Barracks, Tower, Market


class Player:
    """Class that allows the player to interact with the Board"""

    def __init__(self, player_no, tile, board):
        self.lost: bool = False
        self.gold: float = 20
        self.income: int = 0  # just for the display. Actual income is generated by the buildings
        self.tile: Tile = tile  # the tile player is currently pointing at
        self.id: int = player_no
        self.color: (int, int, int) = config.PLAYER_COLORS[player_no]
        self.marker: PlayerMarker = PlayerMarker(self.color, tile.rect.center)
        self.board = board
        self.controls: Dict[str, str] = config.CONTROLS[player_no]
        self.in_upgrade_mode: bool = False
        self.in_build_mode: bool = False
        self.path_builder: PathBuilder = PathBuilder(self)
        self.is_online: bool = False  # if True, the player can't be controlled via the keyboard
        self.current_menu_images = None
        self.menu_images = self.create_menu_images()
        self.menu_image: Any[List[pg.Surface, pg.Rect]] = None

    @staticmethod
    def create_menu_images():
        res = {}
        for menu_name in ['build_menu', 'tower_upgrade_menu', 'barracks_upgrade_menu', 'market_upgrade_menu']:
            image = config.gfx['utils'][menu_name]
            image = pg.transform.smoothscale(image, (config.TILE_SPRITE_SIZE * 4,) * 2)
            res[menu_name] = image
        return res

    def set_menu_image(self, menu_name):
        image = self.menu_images[menu_name]
        rect = image.get_rect(center=self.tile.rect.center)
        self.menu_image = [image, rect]

    def set_is_online(self, is_online):
        self.is_online = is_online

    def get_command_from_event(self, event):
        if event.type == pg.KEYDOWN:
            if self.controls is None or self.is_online:
                # TODO controls for player no 3 and 4
                return None
            if event.key in self.controls.keys():
                command = self.controls[event.key]
                return command

    def execute_command(self, command):
        if self.lost:
            return
        if self.in_upgrade_mode:
            self.upgrade_building(command)
        elif self.path_builder.is_active:
            self.path_builder.handle_command(command)
        elif self.in_build_mode:
            self.parse_build_command(command)
        else:
            if command == 'action':
                if self.tile.owner == self and self.tile.building is None:
                    self.in_build_mode = True
                    self.set_menu_image('build_menu')
                elif self.tile.owner == self and self.tile.building is not None and self.tile.building.is_built:
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

    def parse_build_command(self, command):
        if command == 'up':
            building_name = 'barracks'
        elif command == 'left':
            building_name = 'market'
        elif command == 'right':
            building_name = 'tower'
        elif command == 'down':
            self.in_build_mode = False
            return
        else:
            raise ValueError('Invalid build command: ', command)

        if self.build(building_name):
            self.in_build_mode = False

    def add_gold(self, amount):
        self.gold += amount

    def change_income(self, income_diff):
        self.income += income_diff

    def build(self, building_name):
        """ Checks building conditions. If fulfilled builds the requested building and returns True"""
        build_cost = BUILDING_DATA[building_name]['cost']
        if self.gold >= build_cost:
            if self.tile.owner == self and self.tile.building is None:
                self.add_gold(-build_cost)
                self.board.build_on_tile(self.tile, building_name)
                print(f'Player {self.id} has build {building_name}')
                return True
            else:
                print(f"Player {self.id} can't place buildings on this tile!")
        print(f"Player {self.id} can't afford to build {building_name} on this tile!")
        return False

    def move(self, direction):
        if self.tile.neighbours[direction] is not None:
            self.tile = self.tile.neighbours[direction]
            self.marker.set_position(self.tile.rect.center)

    def lose(self):
        print(f'Players {self.id} lost')
        self.lost = True

    def init_upgrade(self):
        if self.tile.owner == self and self.tile.building is not None:
            upgrade_types = self.tile.building.get_upgrade_types()
            if len(upgrade_types) > 0:  # it is upgradable
                self.in_upgrade_mode = True
                if isinstance(self.tile.building, Market):
                    self.set_menu_image('market_upgrade_menu')
                elif isinstance(self.tile.building, Tower):
                    self.set_menu_image('tower_upgrade_menu')
                elif isinstance(self.tile.building, Barracks):
                    self.set_menu_image('barracks_upgrade_menu')
            else:
                print("Can't upgrade building")
        else:
            print(f"Player {self.id} doesn't have building on this tile!")

    def upgrade_building(self, command):
        upgrade_types = self.tile.building.get_upgrade_types()
        if command == 'left':
            upgrade_name = upgrade_types[0]
        elif command == 'right':
            upgrade_name = upgrade_types[1]
        elif command == 'down':
            self.in_upgrade_mode = False
            return
        else:
            raise ValueError('Invalid upgrade command: ', command)

        upgrade_cost = BUILDING_DATA[upgrade_name]['cost']
        if self.gold >= upgrade_cost:
            self.add_gold(-upgrade_cost)
            self.tile.building.upgrade(upgrade_name)
            self.in_upgrade_mode = False

    def draw_marker(self, surface):
        surface.blit(self.marker.image, self.marker.rect)

    def draw_menu(self, surface):
        """Draws a choice menu if in build or upgrade mode"""
        if self.in_build_mode or self.in_upgrade_mode:
            surface.blit(*self.menu_image)


class PlayerMarker(pg.sprite.Sprite):
    # maybe it could be stored inside of the Player
    def __init__(self, color, tile_center):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE+2, config.TILE_SIZE+2))
        self.image.fill(color)
        self.image.set_alpha(150)  # applies soma alpha
        self.rect = self.image.get_rect(center=tile_center)

    def set_position(self, new_center):
        self.rect.center = new_center
