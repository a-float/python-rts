import pygame as pg
from data.components.soldier import *
from data.components.bullet import *
from data.components.building_stats import *
from data import config, colors


class Building(pg.sprite.Sprite):
    def __init__(self, tile, img_name):
        super().__init__()
        self.max_health = 0
        self.health = 0
        self.cost = 0
        self.can_be_attacked = True
        self.buildable = True
        self.is_destroyed = False
        self.is_built = False
        # self.building_timer = 10
        self.last_action_time = 0
        self.delay = 1
        self.tile = tile
        self.owner = tile.owner
        self.image = config.gfx['buildings'][img_name]
        self.image = pg.transform.scale(self.image, (config.TILE_SPRITE_SIZE,) * 2)
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.health_rect = self.rect
        self.health_image = config.gfx['utils']['full_hp']
        self.health_image = pg.transform.scale(self.health_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_timer = 0
        self.damage_image = config.gfx['utils']['boom']
        self.damage_image = pg.transform.scale(self.damage_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_rect = self.rect
        self.building_sprites = []
        self.building_sprites.append(config.gfx['utils']['building_anim'])
        self.building_sprites.append(config.gfx['utils']['building_anim_2'])
        self.current_building_sprite = 0
        self.building_image = config.gfx['buildings'][img_name]
        self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,) * 2)

    def update(self, now):
        if not self.is_built:
            if self.health < self.max_health:
                self.image = self.building_sprites[self.current_building_sprite]
                self.image = pg.transform.scale(self.image, (config.TILE_SPRITE_SIZE,) * 2)
                self.health += BUILDING_SPEED
                if self.health % 10 == 0:
                    self.current_building_sprite += 1
                if self.current_building_sprite >= len(self.building_sprites):
                    self.current_building_sprite = 0
            else:
                self.health = self.max_health
                self.image = self.building_image
                self.is_built = True

        elif self.last_action_time <= now - self.delay * 1000:
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
        if not self.is_built:
            return
        print("Building got ", damage, " damage")
        self.health -= damage
        self.damage_timer = 10
        if self.health <= 0:
            self.tile.building = None
            self.kill()

    @staticmethod
    def to_dict():
        return BUILDINGS

    def draw_health(self, surface):
        if self.damage_timer > 0:
            surface.blit(self.damage_image, self.damage_rect)
            self.damage_timer -= 1
        health_ratio = self.health / self.max_health
        if health_ratio >= 0.8:
            self.health_image = config.gfx['utils']['full_hp']

        elif health_ratio >= 0.6:
            self.health_image = config.gfx['utils']['almost_full']
        elif health_ratio >= 0.4:
            self.health_image = config.gfx['utils']['medium_hp']
        elif health_ratio >= 0.2:
            self.health_image = config.gfx['utils']['low_hp']
        else:
            self.health_image = config.gfx['utils']['critical_hp']

        self.health_image = pg.transform.scale(self.health_image, (config.TILE_SPRITE_SIZE,) * 2)

        surface.blit(self.health_image, self.health_rect)


class Castle(Building):
    def __init__(self, tile):
        super().__init__(tile, 'castle')
        self.health = self.max_health = BUILDING_DATA['castle']['health']
        self.tile = tile
        self.basic_income = BUILDING_DATA['castle']['income']  # TODO make income a static class variable
        self.tile = tile
        self.buildable = False

    def passive(self):
        self.owner.add_gold(self.basic_income)


class Tower(Building):
    def __init__(self, tile):
        super().__init__(tile, 'tower')
        self.tile = tile
        self.neighbours = tile.neighbours
        self.type = 0
        self.max_health = BUILDING_DATA['tower']['health']
        self.health = 0
        self.timer = 0
        self.damage = TOWER_DAMAGE
        self.bullet_image = config.gfx['utils']['default_bullet']

    def passive(self):
        for neigh in self.neighbours:
            # attacks first soldier found
            neigh = self.neighbours[neigh]
            soldier = None
            if neigh is not None:
                soldier = neigh.get_soldier(self.owner)
            if soldier is not None:
                self.tile.board.add_bullet(Bullet(self.bullet_image, self, soldier, self.damage))
                self.timer = TOWER_RELOAD_TIME[self.type]
                print('Paf paf i shoot')
                break

    def get_upgrade_types(self):
        if not self.is_built:
            return []
        return list(UPGRADE_TYPES['tower'].keys()) if self.type == 0 else []

    def upgrade(self, upgrade_type):
        if not self.is_built:
            return
        if UPGRADE_TYPES['tower'][upgrade_type] == 1:
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
            self.building_image = config.gfx['buildings']['sniper_tower']
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.bullet_image = config.gfx['utils']['arrow']
            self.bullet_image = pg.transform.scale(self.bullet_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0

        if UPGRADE_TYPES['tower'][upgrade_type] == 2:
            self.type = 2
            self.building_image = config.gfx['buildings']['magic_tower']
            self.bullet_image = config.gfx['utils']['magic_sphere']
            self.bullet_image = pg.transform.scale(self.bullet_image, (config.TILE_SPRITE_SIZE,)*2)
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0


class Barracks(Building):
    def __init__(self, tile):
        super().__init__(tile, 'barracks')
        self.tile = tile
        self.path_sprite = None
        self.can_release = False
        self.soldier_queue = []
        self.type = 0
        self.soldier_cost = 20
        self.max_health = BUILDING_DATA['barracks']['health']
        self.health = 0
        self.delay = 0.5

    def try_to_train_soldiers(self):
        if self.owner.gold >= self.soldier_cost and len(self.soldier_queue) < 3:
            self.owner.gold -= self.soldier_cost
            dmg = SOLDIER_STATS['damage'][self.type]
            hp = SOLDIER_STATS['health'][self.type]
            self.soldier_queue.append(Soldier(hp, dmg, self.type))
        else:
            pass
            # print(f"Player {self.owner.id} can't train new soldier!")

    def try_to_release_soldier(self):
        if self.can_release and len(self.soldier_queue) > 0:
            soldier = self.soldier_queue.pop(0)
            soldier.release(self.tile.paths[self.owner.id])
            self.tile.board.add_unit(soldier)
            print(f"Releasing a players {soldier.owner.id} soldier")

    def passive(self):
        self.try_to_train_soldiers()
        self.try_to_release_soldier()

    def get_upgrade_types(self):
        if not self.is_built:
            return []
        return list(UPGRADE_TYPES['barracks'].keys()) if self.type == 0 else []

    def get_attacked(self, damage):
        if not self.is_built:
            return
        self.health -= damage
        print("Get attacked DMG: ", damage)
        if self.health <= 0:
            path = self.tile.paths[self.owner.id]
            if path:
                path.destroy()
            self.tile.building = None
            self.kill()

    def upgrade(self, upgrade_type):
        if not self.is_built:
            return
        self.type = UPGRADE_TYPES['barracks'][upgrade_type]
        if self.type == UPGRADE_TYPES['barracks']['shields']:
            self.building_image = config.gfx['buildings']['shield_barracks']
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0
        else:
            self.building_image = config.gfx['buildings']['sword_barracks']
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0


class Market(Building):
    def __init__(self, tile):
        super().__init__(tile, 'market')
        self.type = 0
        self.max_health = BUILDING_DATA['market']['health']
        self.health = 0
        self.owner.change_income(MARKET_STATS['income'][self.type] / MARKET_STATS['frequency'][self.type])
        self.delay = MARKET_STATS['frequency'][self.type]

    def passive(self):
        self.owner.add_gold(MARKET_STATS['income'][self.type])

    def get_upgrade_types(self):
        if not self.is_built:
            return []
        return list(UPGRADE_TYPES['market'].keys()) if self.type == 0 else []

    def upgrade(self, upgrade_type):
        if not self.is_built:
            return
        self.type = UPGRADE_TYPES['market'][upgrade_type]
        if self.type == UPGRADE_TYPES['market']['bank']:
            self.building_image = config.gfx['buildings']['bank']
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0
        else:
            self.building_image = config.gfx['buildings']['mine']
            self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,)*2)
            self.is_built = False
            self.health = 0
        self.owner.change_income(MARKET_STATS['income'][self.type]/MARKET_STATS['frequency'][self.type] -
                                 MARKET_STATS['income'][0]/MARKET_STATS['frequency'][0])

    def get_attacked(self, damage):
        super().get_attacked(damage)
        # update owner income on being destroyed
        if self.health < 0:
            self.owner.change_income(-MARKET_STATS['income'][self.type]/MARKET_STATS['frequency'][self.type])


BUILDINGS = {
    'castle': Castle,
    'tower': Tower,
    'barracks': Barracks,
    'market': Market,
}