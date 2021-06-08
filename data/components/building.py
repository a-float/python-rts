import pygame as pg
from data.components.soldier import Soldier, dist_sq
from data.tools import pos_to_relative, get_health_surface
from data.networking import Packable
from data.components import Bullet
from data.building_stats import *
from data import config
from data.tools import Animation


class Building(pg.sprite.Sprite, Packable):
    def __init__(self, tile, building_name):
        super().__init__()
        self.name = building_name
        self.max_health = BUILDING_DATA[self.name]['health']
        self.health = 0  # health starts as 0 and increases to a hundred while building
        self.cost = 0
        self.is_built = False
        self.owner = tile.owner
        if not self.owner:
            raise ValueError('Building with no owner created: ', self.name)
        self.last_passive_time = 0  # when was the last time the passive was executed
        self.delay = 1  # time between adjacent passive() calls in seconds
        self.tile = tile

        self.image = config.gfx['buildings'][building_name]
        self.image = pg.transform.scale(self.image, (config.TILE_SPRITE_SIZE,) * 2)
        self.rect = self.image.get_rect(center=tile.rect.center)
        self.damage_timer = 0
        self.damage_image = config.gfx['utils']['boom']
        self.damage_image = pg.transform.scale(self.damage_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_rect = self.rect
        self.building_sprites = []
        self.building_sprites.append(config.gfx['utils']['building_anim'])
        self.building_sprites.append(config.gfx['utils']['building_anim_2'])
        for i in range(len(self.building_sprites)):
            self.building_sprites[i] = pg.transform.scale(self.building_sprites[i], (config.TILE_SPRITE_SIZE,) * 2)
        self.anim = Animation(self.building_sprites, fps=7)
        self.building_image = config.gfx['buildings'][building_name]
        self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,) * 2)

    def update(self, now):
        """ Called every frame. Handles the building animation"""
        if not self.is_built:
            if self.health < self.max_health:
                self.image = self.anim.get_next_frame(now)
                self.health += BUILDING_SPEED

            else:
                self.health = self.max_health
                self.image = self.building_image
                self.is_built = True
        # passive is not executed while the building is being built
        elif self.last_passive_time <= now - self.delay * 1000:
            self.last_passive_time = now
            self.passive()

    def get_upgrade_types(self):
        """ Returns the list of names of the buildings the current one can be upgraded to """
        if not self.is_built:
            return []
        return UPGRADE_TYPES.get(self.name, [])

    def passive(self):
        # Called every self.delay seconds
        pass

    def active(self):
        # Called whenever the action button is pressed on this field
        pass

    def upgrade(self, upgrade_name):
        """
        Replaces the tile's building to the new building of the specified name.
        Doesn't destroy nor actually build the new building
        Tile ownership is not affected
        """
        self.kill()
        new_building = BUILDINGS[upgrade_name](self.tile)
        new_building.health = 0
        new_building.tile = self.tile
        new_building.is_built = False
        self.pass_to_upgraded_building(new_building)
        self.tile.board.replace_tile_building(self.tile, new_building)

    def pass_to_upgraded_building(self, new_building):
        """ Called on the upgraded version of the building before it is placed on the tile """
        pass

    def destroy(self):
        """ Called when the building is destroyed"""
        self.tile.demolish()

    def get_attacked(self, damage):
        """ Called when a soldier attacks the building"""
        self.health -= damage
        self.damage_timer = 10
        if self.health <= 0:
            self.destroy()

    def draw_health(self, surface):
        if self.damage_timer > 0:
            surface.blit(self.damage_image, self.damage_rect)
            self.damage_timer -= 1
        health_ratio = self.health / self.max_health
        health_img = get_health_surface(health_ratio, config.TILE_SPRITE_SIZE, config.TILE_SPRITE_SIZE*0.12)
        health_rect = health_img.get_rect(centerx=self.tile.rect.centerx, top=self.tile.rect.top+5)
        surface.blit(health_img, health_rect)

    def pack(self):
        return {
            'name': self.name,
            'health': self.health,
            'is_built': self.is_built,
        }

    def unpack(self, data):
        self.health = data['health']
        self.is_built = data['is_built']


class Castle(Building):
    def __init__(self, tile):
        super().__init__(tile, 'castle')
        self.income = BUILDING_DATA[self.name]['income']
        self.owner.change_income(self.income)

    def passive(self):
        self.owner.add_gold(self.income)

    def destroy(self):
        self.owner.lose()
        super().destroy()
        # no need to decrease the income as player is out anyway


class Tower(Building):
    def __init__(self, tile, building_name='tower'):
        super().__init__(tile, building_name)
        self.tile = tile
        self.neighbours = tile.neighbours
        self.fire_rate = BUILDING_DATA[self.name]['fire_rate']
        self.damage = BUILDING_DATA[self.name]['damage']
        self.range = BUILDING_DATA[self.name]['range']
        self.bullet_image = config.gfx['utils'][self.name.split('_')[0]+'_bullet']

    def passive(self):
        for soldier in self.tile.board.unit_group.sprites():
            if soldier.owner != self.owner and dist_sq(pos_to_relative(soldier.rect.center), pos_to_relative(self.rect.center)) < self.range:
                self.tile.board.add_bullet(Bullet(self.bullet_image, self.rect.center, soldier, self.damage))
                self.delay = 1/self.fire_rate
                break


class SniperTower(Tower):
    def __init__(self, tile):
        super().__init__(tile, 'sniper_tower')


class MagicTower(Tower):
    def __init__(self, tile):
        super().__init__(tile, 'magic_tower')


class Barracks(Building):
    def __init__(self, tile, building_name='barracks'):
        super().__init__(tile, building_name)
        self.path = None
        self.tile = tile
        self.soldier_queue = []
        self.delay = 2
        self.soldier_name = self.name.split('_')[0]

    def set_path(self, path):
        self.path = path

    def try_to_train_soldiers(self):
        if len(self.soldier_queue) < 3:
            soldier = Soldier(self.soldier_name)
            self.soldier_queue.append(soldier)

    def try_to_release_soldier(self):
        if self.path and not self.path.is_destroyed and len(self.soldier_queue) > 0:
            soldier = self.soldier_queue.pop(0)
            soldier.release(self.path)
            self.tile.board.add_unit(soldier)
            # print(f"Releasing a players {soldier.tile.owner.id} soldier")

    def passive(self):
        self.try_to_train_soldiers()
        self.try_to_release_soldier()

    def get_attacked(self, damage):
        if not self.is_built:
            return
        self.health -= damage
        print("Get attacked DMG: ", damage)
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        super().destroy()
        if self.health <= 0:  # don't destroy the path if the barracks are getting upgraded
            path = self.tile.paths[self.owner.id]
            if path:
                path.destroy()

    def pass_to_upgraded_building(self, new_building):
        new_building.path = self.path

    def pack(self):
        building_pack = super().pack()
        building_pack.update({'path_id': self.path.path_id if self.path else None})
        return building_pack

    def unpack(self, data):
        super().unpack(data)
        if data['path_id']:
            self.path = self.tile.board.get_path_by_id(data['path_id'])


class SwordBarracks(Barracks):
    def __init__(self, tile):
        super().__init__(tile, 'swords_barracks')


class ShieldBarracks(Barracks):
    def __init__(self, tile):
        super().__init__(tile, 'shields_barracks')


class Market(Building):
    def __init__(self, tile, building_name='market'):
        super().__init__(tile, building_name)
        self.income = BUILDING_DATA[self.name]['income']
        self.frequency = BUILDING_DATA[self.name]['frequency']
        self.owner.change_income(self.income / self.frequency)
        self.delay = self.delay * self.frequency

    def passive(self):
        self.owner.add_gold(self.income)

    def destroy(self):
        super().destroy()
        self.owner.change_income(-self.income * self.frequency)

    def get_attacked(self, damage):
        super().get_attacked(damage)
        # update owner's income on being destroyed
        if self.health < 0:
            self.owner.change_income(-self.income * self.frequency)


class Mine(Market):
    def __init__(self, tile):
        super().__init__(tile, 'mine')


class Bank(Market):
    def __init__(self, tile):
        super().__init__(tile, 'bank')


BUILDINGS = {
    'castle': Castle,
    'tower': Tower,
    'sniper_tower': SniperTower,
    'magic_tower': MagicTower,
    'barracks': Barracks,
    'swords_barracks': SwordBarracks,
    'shields_barracks': ShieldBarracks,

    'market': Market,
    'bank': Bank,
    'mine': Mine,
}
