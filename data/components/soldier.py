import math
import pygame as pg
from data import config


class Soldier(pg.sprite.Sprite): # todo soldiers get damage but cant die, and newly made sum up
    def __init__(self, health, damage):
        pg.sprite.Sprite.__init__(self)
        self.max_health = health
        self.health = health
        self.damage = damage
        self.path = None
        self.owner = None
        self.move_vector = None
        self.image = config.gfx['units']['soldier']
        self.image = pg.transform.scale(self.image, (config.UNIT_SIZE,)*2)
        self.speed = 1

    def release(self, path):
        self.path = path
        self.path.tile.soldiers.append(self)
        self.rect = self.image.get_rect(center=path.tile.rect.center)
        self.move_vector = self.get_move_vector()
        self.owner = self.path.tile.owner

    def get_move_vector(self):
        src, to = self.path.tile.rect.center, self.path.target.tile.rect.center
        hypot = math.sqrt(dist_sq(src, to))
        scale = self.speed
        dx, dy = (to[0] - src[0]) / hypot * scale, (to[1] - src[1]) / hypot * scale
        return dx, dy

    def update(self):
        if self.path is None:
            self.kill()
        if dist_sq(self.rect.center, self.path.target.tile.rect.center) >= 0.001:
            # print(self.move_vector, self.rect.center)
            self.rect.move_ip(*self.move_vector)
            if self.path.tile.building is not None and self.path.tile.owner != self.owner:
                self.attack(self.path.tile.building)
        else:  # soldier has arrived at the target tile
            self.path.tile.soldiers.remove(self)
            self.path = self.path.target
            self.path.tile.soldiers.append(self)
            if self.path.target is None:  # soldier disappears upon reaching end of the path
                self.kill()
            else:
                self.move_vector = self.get_move_vector()

    def get_attacked(self, damage):
        print("AUCH!!!  HP:  ", self.health)
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def attack(self, building):
        building.get_attacked(self.damage)
        self.kill()  # :c


def dist_sq(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2
