import pygame as pg
from data.components.soldier import *
from data import config, colors

BUILDINGS_DATA = {
  'castle' : {'health' : 1000, 'income' : 5},
  'tower' : {'health' : 200, 'cost' : 200},
  'market' : {'health' : 150, 'cost' : 250},
  'path' : {'health' : 50, 'cost' : 20}
}

UPGRADE_COST = 50

class Building(pg.sprite.Sprite):
    def __init__(self, neighbour):
        self.health = 0
        self.cost = 0
        self.attackable = True
        self.buildable = True
        self.is_destroyed = False
        self.last_action_time = 0
        self.delay = 1

    def timer(self, now, player):
        if self.last_action_time <= now - self.delay * 1000:
            self.last_action_time = now
            self.passive(player)

    def passive(self, player):
        # It is called every iteration
        pass  
    
    def active(self, player):
        # It is called whenever action button is pressed on this field
        pass

    def upgrade(self, upgrade_type):
        pass

    def get_upgrade_types(self):
        return None

    def get_attacked(demage):
        self.health -= demage 
        if self.health <= 0:
            self.is_destroyed = True   

    @staticmethod
    def to_dict():
        return {
                'Tower' : Tower,
                'Barracks' : Barracks,
                'Market' : Market,
                } 


class Castle(Building):
    def __init__(self, tile):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE//2, config.TILE_SIZE//2))
        self.image.fill(tile.owner.color)
        self.rect = self.image.get_rect()
        self.health = BUILDING_DATA['Castle']
        self.basic_income = BULIDING_DATA['castle']['income'] # TODO make income a static class variable
        self.tile = tile
        self.buildable = False
        
    def passive(self, player):
        player.gold += self.basic_income
         
"""
Neigbours = {
    'up' = up_neighbour (type_of_tile)
    'right' = right... etc.
    ...
}
"""

class Tower(Building):
    def __init__(self, tile):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE//2, config.TILE_SIZE//2))
        self.image.fill(colors.PURPLE)
        self.tile = tile
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.neighbours = tile.neighbours
        self.type = 0
        self.upgrade_types = {
            'sniper' : 1,
            'magic' : 2
        }
        self.type_reload_time = {
            0 : 4,
            1 : 4,
            2 : 2
        }
        self.timer = 0
        self.demage = 50

    def passive(self, player):
        if timer > 0:
            timer -= 1
        else: 
           for neigh in neighbours:
                # attacks first soldier found
                soldier = neighbour.get_soldier()
                if soldier is not None:
                    soldier.get_attacked(self.demage)
                    self.timer = self.type_reload_time[self.type]
                    break     
        
    def get_upgrade_types(self):
        return list(self.upgrade_types.keys()) if self.type == 0 else None

    def upgrade(self, upgrade_type):
        if self.upgrade_types[upgrade_type] == 1:
            self.type = 1
            if self.neighbours['up'] is not None:
                neigh = self.addneighbours['up'].neighbours['up']
                if neigh is not None:
                    self.neighbours['up_up'] = neigh
            if self.neighbours['right'] is not None:
                neigh = self.addneighbours['right'].neighbours['right']
                if neigh is not None:
                    self.neighbours['right_right'] = neigh
            if self.neighbours['down'] is not None:
                neigh = self.addneighbours['down'].neighbours['down']
                if neigh is not None:
                    self.neighbours['down_down'] = neigh
            if self.neighbours['left'] is not None:
                neigh = self.addneighbours['left'].neighbours['left']
                if neigh is not None:
                    self.neighbours['left_left'] = neigh 
        if self.upgrade_types[upgrade_type] == 2:
            self.type = 2                                      

            
class Barracks(Building):
    def __init__(self, neighbours):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE//2, config.TILE_SIZE//2))
        self.image.fill(colors.YELLOW)
        self.rect = self.image.get_rect()

        self.neighbours = neighbours
        self.soldier_demage = 20
        self.soldier_health = 50
        self.soldier = None
        self.path = None
        self.soldier_queue = []
        self.type = 0
        self.soldier_cost = 50
        self.upgrade_types = {
            'swords' : 1,
            'shields' : 2
        }
        self.type_soldier_demage = {
            0 : 20,
            1 : 40,
            2 : 20
        }
        self.type_soldier_health = {
            0 : 50,
            1 : 50,
            2 : 100
        }

    def passive(self, player):
        if self.path is not None:
            self.path.move_soldiers()
        if self.soldier is None and len(self.soldier_queue) > 0:
            self.soldier = self.soldier_queue.pop(0)

    def active(self, player):
        if player.gold >= self.soldier_cost and len(self.soldier_queue) < 5:
            player.gold -= self.soldier_cost
            dmg = self.type_soldier_demage[self.type]
            hp = self.type_soldier_health[self.type]
            self.soldier_queue.append(Soldier(hp, dmg))

    def get_upgrade_types(self):
        return list(self.upgrade_types.keys()) if self.type == 0 else None
    
    def upgrade(self, upgrade_type):
        self.type = self.get_upgrade_types[upgrade_type]

    #TODO dodac funkcje usuwania sciezek przy niszczeniu koszar         

class Market(Building):
    def __init__(self, neighbours):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((config.TILE_SIZE//2, config.TILE_SIZE//2))
        self.image.fill(colors.CYAN)
        self.rect = self.image.get_rect()
        self.type = 0
        self.timer = 0
        self.upgrade_types = {
            'mine' : 1,
            'bank' : 2
        }
        self.type_income = { # TODO get type_income from BUILIDING_DATA dict
            0 : 1,
            1 : 2,
            2 : 13
        }
        self.type_frequency = { # TODO maybe this as well 
            0 : 0,
            1 : 0,
            2 : 4
        }

    def passive(self, player):
        if timer > 0:
            timer -= 1
        else:
            player.gold += self.type_income[self.type]
            timer = self.type_frequency[self.type]

    def get_upgrade_types(self):
        return lsit(self.upgrade_types.keys()) if self.type == 0 else None

    def upgrade(self, upgrade_type):
        self.type = self.upgrade_types[upgrade_type]


class Path(Building):
    def __init__(self, source, target):
        pg.sprite.Sprite.__init__(self)
        self.source = source
        self.target = target
        self.soldier = None
        self.attackable = False
        self.is_active = False

    def activate_to_source(self):
         self.is_active = True
         if isinstance(self.source, Path):
            self.source.activate_to_source()     

    def move_soldiers(self):
        if isinstance(self.target, Path):
                self.target.move_soldiers()
        if self.is_active and self.soldier is None and self.source.soldier is not None:
            self.soldier = self.source.soldier
            self.source.soldier = None

    def passive(self, player):
        if isinstance(self.target, Building) and not isinstance(self.target, Path) and soldier is not None:
            self.soldier.attacks(self.target)


BUILDINGS = {
    'castle' : Castle,
    'tower' : Tower,
    'market' : Market,
    'path' : Path
}