import math
import pygame as pg
from data import config
from data.tools import dist_sq, get_health_surface, pos_to_relative, pos_to_absolute
from data.components.building_stats import SOLDIER_STATS, SOLDIER_ANIM_FPS
from data.tools import Animation
from data.networking import Packable


class Soldier(pg.sprite.Sprite, Packable):
    def pack(self):
        return {
            'name': self.name,
            'pos': pos_to_relative(self.rect.center),
            'curr_path_index': self.path_tile_index,
            'path_id': self.path.path_id,
            'move_vector': self.move_vector,
            'flipped': self.flipped
        }

    def unpack(self, data):
        self.path_tile_index = data['curr_path_index']
        self.rect.center = pos_to_absolute(data['pos'])
        self.move_vector = data['move_vector']
        self.flipped = data['flipped']

    def __init__(self, unit_name):
        pg.sprite.Sprite.__init__(self)
        stats = SOLDIER_STATS[unit_name]
        self.name = unit_name
        self.max_health = stats['health']
        self.health = self.max_health
        self.damage = stats['attack']
        self.owner = None
        self.tile = None
        self.path = None
        self.move_vector = None
        self.image = None

        self.flipped = False
        self.sprites = []
        self.sprites.append(config.gfx['units'][self.name + '_soldier'])
        self.sprites.append(config.gfx['units'][self.name + '_soldier_2'])
        for i in range(len(self.sprites)):
            self.sprites[i] = pg.transform.scale(self.sprites[i], (config.UNIT_SIZE,) * 2)
        self.speed = 1
        self.path_tile_index = 1
        self.damage_timer = 0
        self.damage_image = config.gfx['utils']['boom']
        self.damage_image = pg.transform.scale(self.damage_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_rect = None
        self.is_dead = False
        self.dying_timer = 10
        self.anim = Animation(self.sprites, SOLDIER_ANIM_FPS)

    def release(self, path):
        self.path = path
        self.tile = self.path.tiles[0]
        self.owner = self.tile.owner
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=path.tiles[0].rect.center)
        self.move_vector = self.get_move_vector()

    def get_move_vector(self):
        try:
            src, to = self.rect.center, self.path.tiles[self.path_tile_index].rect.center
        except IndexError:  # the path has changed, unit has to die [*]
            self.is_dead = True
            return None
        hypot = math.sqrt(dist_sq(src, to))
        scale = self.speed
        dx, dy = (to[0] - src[0]) / hypot * scale, (to[1] - src[1]) / hypot * scale
        return dx, dy

    def try_to_attack(self):
        if self.tile.building is not None and self.tile.owner != self.owner:
            self.attack(self.tile.building)

    def update(self, now):
        if self.is_dead:
            self.die()
            return

        self.image = self.anim.get_next_frame(now)
        if self.move_vector[0] < 0:
            self.flipped = True
        if self.move_vector[0] > 0:
            self.flipped = False
        if self.flipped:
            self.image = pg.transform.flip(self.image, True, False)

        if self.path.destroyed:  # tha path under the soldier has disappeared
            self.kill()
        if dist_sq(self.rect.center, self.path.tiles[self.path_tile_index].rect.center) >= 0.001:
            # print(self.move_vector, self.rect.center)
            self.rect.move_ip(*self.move_vector)
        else:  # soldier has arrived at the target tile
            self.try_to_attack()

            # try to go to the next tile
            if self.path_tile_index == len(self.path.tiles)-1:  # soldier disappears upon reaching the end of the path
                self.kill()
            else:
                self.path_tile_index += 1
                self.tile = self.path.tiles[self.path_tile_index]
                self.move_vector = self.get_move_vector()

    def get_attacked(self, damage):
        self.health -= damage
        self.damage_timer = 10
        if self.health <= 0:
            self.is_dead = True

    def attack(self, building):
        building.get_attacked(self.damage)
        self.kill()  # :c

    def die(self):
        if self.dying_timer > 0:
            self.damage_timer = self.dying_timer
            self.dying_timer -= 1
        else:
            self.kill()

    def draw_health(self, surface):
        if self.damage_timer > 0:
            surface.blit(self.damage_image, self.damage_image.get_rect(center=self.rect.center))
            self.damage_timer -= 1
        health_ratio = max(0, self.health / self.max_health)
        health_img = get_health_surface(health_ratio, config.TILE_SPRITE_SIZE*0.6, config.TILE_SPRITE_SIZE * 0.10)
        health_rect = health_img.get_rect(centerx=self.rect.centerx, top=self.rect.top - 4)
        surface.blit(health_img, health_rect)
