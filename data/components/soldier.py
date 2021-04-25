import math
import pygame as pg
from data import config


class Soldier(pg.sprite.Sprite):
    def __init__(self, health, damage, type):
        pg.sprite.Sprite.__init__(self)
        self.max_health = health
        self.health = health
        self.damage = damage
        self.path = None
        self.owner = None
        self.type = type
        self.move_vector = None
        self.image = config.gfx['units']['soldier']
        self.image = pg.transform.scale(self.image, (config.UNIT_SIZE,)*2)
        self.speed = 1
        self.tile = None
        self.tile_index = 1

    def release(self, path):
        self.path = path
        self.tile = self.path.tiles[0]
        self.tile.soldiers.append(self)
        if self.type == 1:
            self.image = config.gfx['units']['swordsman']
        elif self.type == 2:
            self.image = config.gfx['units']['shieldman']
        self.image = pg.transform.scale(self.image, (config.UNIT_SIZE,) * 2)
        self.rect = self.image.get_rect(center=path.tiles[0].rect.center)
        self.move_vector = self.get_move_vector()
        self.owner = self.tile.owner

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
        if self.tile.paths[self.owner.id] is None:  # tha path under the soldier has disappeared
            self.kill()
        if dist_sq(self.rect.center, self.path.tiles[self.tile_index].rect.center) >= 0.001:
            # print(self.move_vector, self.rect.center)
            self.rect.move_ip(*self.move_vector)
        else:  # soldier has arrived at the target tile
            self.try_to_attack()
            self.tile.soldiers.remove(self)

            # try to go to the next tile
            if self.tile_index == len(self.path.tiles)-1:  # soldier disappears upon reaching the end of the path
                self.kill()
            else:
                self.tile_index += 1
                self.tile = self.path.tiles[self.tile_index]
                self.move_vector = self.get_move_vector()
                self.tile.soldiers.append(self)

    def get_attacked(self, damage):
        self.health -= damage
        print("AUCH!!!  HP:  ", self.health)
        if self.health <= 0:
            print("IM DEAD!")
            self.kill()
            self.tile.soldiers.remove(self)
            del self

    def attack(self, building):
        building.get_attacked(self.damage)
        self.kill()  # :c


def dist_sq(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2
