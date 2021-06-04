from data.components.soldier import Soldier, pos_to_relative
from data.components.bullet import *
from data.components.building_stats import *
from data import config


class Building(pg.sprite.Sprite):
    def __init__(self, tile, building_name):
        super().__init__()
        self.name = building_name
        self.max_health = 0
        self.health = 0
        self.cost = 0
        self.can_be_attacked = True
        self.is_built = False
        self.owner = tile.owner
        # self.building_timer = 10
        self.last_action_time = 0
        self.delay = 1
        self.tile = tile
        self.max_health = BUILDING_DATA[self.name]['health']

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
        self.current_building_sprite = 0
        # TODO this same as self.image???
        self.building_image = config.gfx['buildings'][building_name]
        self.building_image = pg.transform.scale(self.building_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.images = {}  # TODO this is not used anywhere?

    def update(self, now):
        if not self.is_built:
            if self.health < self.max_health:
                self.image = self.building_sprites[self.current_building_sprite]
                # TODO should not scale in update
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

    def get_upgrade_types(self):
        if not self.is_built:
            return []
        return UPGRADE_TYPES.get(self.name, [])

    def passive(self):
        # It is called every self.delay seconds
        pass

    def active(self):
        # It is called whenever action button is pressed on this field
        pass

    def upgrade(self, upgrade_name):
        """ Changes building to one of its upgrades. Returns true if the upgrade_name was valid """
        if not self.is_built:
            return False
        if upgrade_name in self.get_upgrade_types():
            self.get_destroyed()
            new_building = BUILDINGS[upgrade_name](self.tile)
            new_building.health = self.health
            new_building.tile = self.tile
            new_building.is_built = False
            self.pass_to_upgraded_building(new_building)
            self.tile.board.replace_tile_building(self.tile, new_building)
            return True

    def pass_to_upgraded_building(self, new_building):
        pass

    def get_destroyed(self):
        self.tile.building = None
        self.kill()

    def get_attacked(self, damage):
        if not self.is_built:
            return
        self.health -= damage
        self.damage_timer = 10
        if self.health <= 0:
            self.get_destroyed()

    def draw_health(self, surface):
        if self.damage_timer > 0:
            surface.blit(self.damage_image, self.damage_rect)
            self.damage_timer -= 1
        health_ratio = self.health / self.max_health
        health_img = pg.Surface((int(health_ratio*config.TILE_SPRITE_SIZE), int(config.TILE_SPRITE_SIZE*0.12)))
        col = [250 * (1 - health_ratio), health_ratio * 250, 0]
        health_img.fill(col)
        health_rect = health_img.get_rect(centerx=self.tile.rect.centerx, top=self.tile.rect.top+5)
        surface.blit(health_img, health_rect)


class Castle(Building):
    def __init__(self, tile):
        super().__init__(tile, 'castle')
        self.is_built = True

    def passive(self):
        self.owner.add_gold(BUILDING_DATA['castle']['income'])

    def get_destroyed(self):
        self.owner.lose()


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
            if dist_sq(pos_to_relative(soldier.rect.center), pos_to_relative(self.rect.center)) < self.range:
                self.tile.board.add_bullet(Bullet(self.bullet_image, self.rect.center, soldier, self.damage))
                self.delay = 1/self.fire_rate
                print('Paf paf i shoot')
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
        self.tile = tile
        self.path_sprite = None
        self.can_release = False
        self.soldier_queue = []
        self.delay = 2
        self.soldier_name = self.name.split('_')[0]

    def try_to_train_soldiers(self):
        if len(self.soldier_queue) < 3:
            soldier = Soldier(self.soldier_name)
            self.soldier_queue.append(soldier)

    def try_to_release_soldier(self):
        if self.can_release and len(self.soldier_queue) > 0:
            soldier = self.soldier_queue.pop(0)
            soldier.release(self.tile.paths[self.owner.id])
            self.tile.board.add_unit(soldier)
            print(f"Releasing a players {soldier.tile.owner.id} soldier")

    def passive(self):
        self.try_to_train_soldiers()
        self.try_to_release_soldier()

    def get_attacked(self, damage):
        if not self.is_built:
            return
        self.health -= damage
        print("Get attacked DMG: ", damage)
        if self.health <= 0:
            self.get_destroyed()

    def get_destroyed(self):
        super().get_destroyed()
        if self.health <= 0:  # don't destroy the path if the barracks are getting upgraded
            path = self.tile.paths[self.owner.id]
            if path:
                path.destroy()

    def pass_to_upgraded_building(self, new_building):
        new_building.path_sprite = self.path_sprite
        new_building.can_release = self.can_release


class SwordBarracks(Barracks):
    def __init__(self, tile):
        super().__init__(tile, 'swords_barracks')


class ShieldBarracks(Barracks):
    def __init__(self, tile):
        super().__init__(tile, 'shields_barracks')


class Market(Building):
    def __init__(self, tile, building_name='market'):
        super().__init__(tile, building_name)
        self.income = BUILDING_DATA[self.name].get('income', 0)
        self.frequency = BUILDING_DATA[self.name].get('frequency', 1)
        self.owner.change_income(self.income / self.frequency)

    def get_destroyed(self):
        super().get_destroyed()
        self.owner.change_income(-self.income / self.frequency)

    def get_attacked(self, damage):
        super().get_attacked(damage)
        # update owner's income on being destroyed
        if self.health < 0:
            self.owner.change_income(-self.income/self.frequency)


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
