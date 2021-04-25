import pygame as pg
from data.components.soldier import *
from data import config, colors

BUILDING_DATA = {
    'castle': {'health': 1000, 'income': 5},
    'tower': {'health': 200, 'cost': 200},
    'barracks': {'health': 60, 'cost': 250},
    'market': {'health': 150, 'cost': 250},
    'path': {'health': 50, 'cost': 20}
}

UPGRADE_COST = 50


class Building(pg.sprite.Sprite):
    def __init__(self, tile):
        super().__init__()
        self.health = 0
        self.cost = 0
        self.can_be_attacked = True
        self.buildable = True
        self.is_destroyed = False
        self.last_action_time = 0
        self.delay = 1
        self.tile = tile
        self.owner = tile.owner
        self.image = None
        self.rect = None

    def update(self, now):
        if self.last_action_time <= now - self.delay * 1000:
            self.last_action_time = now
            self.passive()

    def passive(self):
        # It is called every self.delay seconds
        pass

    def active(self):
        # It is called whenever action button is pressed on this field
        pass

    def upgrade(self, upgrade_type):
        pass

    def get_upgrade_types(self):
        return None

    def get_attacked(self, damage):
        print("Building got ", damage, " damage")
        self.health -= damage
        if self.health <= 0:
            self.tile.building = None
            self.kill()

    @staticmethod
    def to_dict():
        return {
            'Tower': Tower,
            'Barracks': Barracks,
            'Market': Market,
        }


class Castle(Building):
    def __init__(self, tile):
        super().__init__(tile)
        self.image = config.gfx['buildings']['castle']
        self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.health = BUILDING_DATA['castle']['health']
        self.tile = tile
        self.basic_income = BUILDING_DATA['castle']['income']  # TODO make income a static class variable
        self.tile = tile
        self.buildable = False

    def passive(self):
        self.owner.add_gold(self.basic_income)


"""
Neigbours = {
    'up' = up_neighbour (type_of_tile)
    'right' = right... etc.
    ...
}
"""


class Tower(Building):
    def __init__(self, tile):
        super().__init__(tile)
        self.image = config.gfx['buildings']['tower']
        self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        self.tile = tile
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.neighbours = tile.neighbours
        self.type = 0
        self.health = BUILDING_DATA['tower']['health']
        self.upgrade_types = {
            'sniper': 1,
            'magic': 2
        }
        self.type_reload_time = {
            0: 4,
            1: 4,
            2: 2
        }
        self.timer = 0
        self.damage = 50

    def passive(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            print('Paf paf i shoot')
            for neigh in self.neighbours:
                # attacks first soldier found
                neigh = self.neighbours[neigh]
                soldier = None
                if neigh is not None:
                    soldier = neigh.get_soldier(self.owner)
                if soldier is not None:
                    soldier.get_attacked(self.damage)
                    self.timer = self.type_reload_time[self.type]
                    break

    def get_upgrade_types(self):
        return list(self.upgrade_types.keys()) if self.type == 0 else []

    def upgrade(self, upgrade_type):
        if self.upgrade_types[upgrade_type] == 1:
            self.type = 1
            if self.neighbours['up'] is not None:
                neigh = self.neighbours['up'].neighbours['up']
                if neigh is not None:
                    self.neighbours['up_up'] = neigh
            if self.neighbours['right'] is not None:
                neigh = self.neighbours['right'].neighbours['right']
                if neigh is not None:
                    self.neighbours['right_right'] = neigh
            if self.neighbours['down'] is not None:
                neigh = self.neighbours['down'].neighbours['down']
                if neigh is not None:
                    self.neighbours['down_down'] = neigh
            if self.neighbours['left'] is not None:
                neigh = self.neighbours['left'].neighbours['left']
                if neigh is not None:
                    self.neighbours['left_left'] = neigh
            self.image = config.gfx['buildings']['sniper_tower']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        if self.upgrade_types[upgrade_type] == 2:
            self.type = 2
            self.image = config.gfx['buildings']['magic_tower']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))


class Barracks(Building):
    def __init__(self, tile):
        super().__init__(tile)
        self.image = config.gfx['buildings']['barracks']
        self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.tile = tile
        self.soldier_damage = 20
        self.soldier_health = 50
        self.can_release = False
        self.soldier_queue = []
        self.type = 0
        self.soldier_cost = 50
        self.path_queue = []
        self.health = BUILDING_DATA['barracks']['health']
        self.upgrade_types = {
            'swords': 1,
            'shields': 2
        }
        self.type_soldier_damage = {
            0: 20,
            1: 40,
            2: 20
        }
        self.type_soldier_health = {
            0: 50,
            1: 50,
            2: 100
        }

    def try_to_train_soldiers(self):
        if self.owner.gold >= self.soldier_cost and len(self.soldier_queue) < 5:
            self.owner.gold -= self.soldier_cost
            dmg = self.type_soldier_damage[self.type]
            hp = self.type_soldier_health[self.type]
            self.soldier_queue.append(Soldier(hp, dmg, self.type))
        else:
            print(f"Player {self.owner.id} can't train new soldier!")

    def try_to_release_soldier(self):
        if self.can_release and len(self.soldier_queue) > 0:
            soldier = self.soldier_queue.pop(0)
            soldier.release(self.tile.paths[self.owner.id])
            self.tile.board.add_unit(soldier)
            print(f"Releasing a players {soldier.owner.id} soldier")

    def passive(self):
        self.try_to_train_soldiers()
        self.try_to_release_soldier()

    def active(self):
        pass

    def get_upgrade_types(self):
        return list(self.upgrade_types.keys()) if self.type == 0 else []

    def get_attacked(self, damage):
        self.health -= damage
        print("Get attacked DMG: ", damage)
        if self.health <= 0:
            path = self.tile.paths[self.owner.id]
            while path is not None:
                next_path = path.target
                path.tile.paths[self.owner.id] = None
                path.kill()
                path = next_path
            self.tile.building = None
            del self.owner.path_surfaces[self.tile]
            self.kill()

    def upgrade(self, upgrade_type):
        self.type = self.upgrade_types[upgrade_type]
        if self.type == self.upgrade_types["shields"]:
            self.image = config.gfx['buildings']['shield_barracks']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        else:
            self.image = config.gfx['buildings']['sword_barracks']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))


class Market(Building):
    def __init__(self, tile):
        super().__init__(tile)
        self.image = config.gfx['buildings']['market']
        self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.type = 0
        self.health = BUILDING_DATA['market']['health']
        self.upgrade_types = {
            'mine': 1,
            'bank': 2
        }
        self.type_income = {  # TODO get type_income from BUILIDING_DATA dict
            0: 1,
            1: 2,
            2: 13
        }
        self.type_frequency = {  # TODO maybe this as well
            0: 1,
            1: 1,
            2: 4
        }
        self.delay = self.type_frequency[self.type]

    def passive(self):
        self.owner.add_gold(self.type_income[self.type])

    def get_upgrade_types(self):
        return list(self.upgrade_types.keys()) if self.type == 0 else []

    def upgrade(self, upgrade_type):
        self.type = self.upgrade_types[upgrade_type]
        if self.type == self.upgrade_types["bank"]:
            self.image = config.gfx['buildings']['bank']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
        else:
            self.image = config.gfx['buildings']['mine']
            self.image = pg.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))


BUILDINGS = {
    'castle': Castle,
    'tower': Tower,
    'barracks': Barracks,
    'market': Market
}
