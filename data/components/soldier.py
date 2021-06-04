import math
import pygame as pg
from data import config
from data.components.building_stats import SOLDIER_STATS


class Soldier(pg.sprite.Sprite):
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
        self.current_sprite = 0
        self.movement_iter = 0
        self.speed = 1
        self.tile_index = 1
        self.damage_timer = 0
        self.damage_image = config.gfx['utils']['boom']
        self.damage_image = pg.transform.scale(self.damage_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_rect = None
        self.is_dead = False
        self.dying_timer = 10

    def release(self, path):
        self.path = path
        self.tile = self.path.tiles[0]
        self.owner = self.tile.owner
        self.sprites.append(config.gfx['units'][self.name+'_soldier'])
        self.sprites.append(config.gfx['units'][self.name+'_soldier_2'])
        for i in range(len(self.sprites)):
            self.sprites[i] = pg.transform.scale(self.sprites[i], (config.UNIT_SIZE,) * 2)
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(center=path.tiles[0].rect.center)
        self.move_vector = self.get_move_vector()

    def get_move_vector(self):
        src, to = self.rect.center, self.path.tiles[self.tile_index].rect.center
        hypot = math.sqrt(dist_sq(src, to))
        scale = self.speed
        dx, dy = (to[0] - src[0]) / hypot * scale, (to[1] - src[1]) / hypot * scale
        return dx, dy

    def try_to_attack(self):
        if self.tile.building is not None and self.tile.owner != self.owner:
            self.attack(self.tile.building)

    def update(self):
        if self.is_dead:
            self.die()
            return

        self.movement_iter += 1
        if self.movement_iter % 10 == 0:
            self.movement_iter = 0
            self.current_sprite += 1
            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 0
            self.image = self.sprites[self.current_sprite]
            self.image = pg.transform.scale(self.image, (config.UNIT_SIZE,) * 2)
            if self.move_vector[0] < 0:
                self.flipped = True
            if self.move_vector[0] > 0:
                self.flipped = False
            if self.flipped:
                # TODO image is flipped every frame. Should be checked only when the move vector changes
                self.image = pg.transform.flip(self.image, True, False)

        if self.tile.paths[self.owner.id] is None:  # tha path under the soldier has disappeared
            self.kill()
        if dist_sq(self.rect.center, self.path.tiles[self.tile_index].rect.center) >= 0.001:
            # print(self.move_vector, self.rect.center)
            self.rect.move_ip(*self.move_vector)
        else:  # soldier has arrived at the target tile
            self.try_to_attack()

            # try to go to the next tile
            if self.tile_index == len(self.path.tiles)-1:  # soldier disappears upon reaching the end of the path
                self.kill()
            else:
                self.tile_index += 1
                self.tile = self.path.tiles[self.tile_index]
                self.move_vector = self.get_move_vector()

    def get_attacked(self, damage):
        self.health -= damage
        print("AUCH!!!  HP:  ", self.health)
        self.damage_timer = 10
        if self.health <= 0:
            print("IM DEAD!")
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
        health_img = pg.Surface((int(health_ratio * config.TILE_SPRITE_SIZE*0.6), int(config.TILE_SPRITE_SIZE * 0.12)))
        if health_ratio >= 0.8:
            col = (0, 255, 0)
        elif health_ratio >= 0.6:
            col = (50, 200, 0)
        elif health_ratio >= 0.4:
            col = (100, 150, 0)
        elif health_ratio >= 0.2:
            col = (200, 50, 0)
        else:
            col = (255, 0, 0)
        health_img.fill(col)
        health_rect = health_img.get_rect(centerx=self.rect.centerx, top=self.rect.top - 4)
        surface.blit(health_img, health_rect)


def dist_sq(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

def pos_to_relative(pos):
    return pos[0] / config.SCREEN_SIZE[0], pos[1] / config.SCREEN_SIZE[1]
