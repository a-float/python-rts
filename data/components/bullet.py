import pygame as pg
import math
from data import config
from data.components.soldier import dist_sq


class Bullet(pg.sprite.Sprite):
    def __init__(self, image, start_pos, target, damage):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(image, (config.BULLET_SIZE,)*2)
        self.target = target
        self.speed = 5
        self.target_rect = self.target.rect
        self.rect = self.image.get_rect(center=start_pos)
        self.move_vector = self.get_move_vector()
        self.damage = damage

    def get_move_vector(self):
        src, to = self.rect.center, self.target_rect.center
        hypot = math.sqrt(dist_sq(src, to))
        if hypot == 0:
            return 0,0
        scale = self.speed
        dx, dy = (to[0] - src[0]) / hypot * scale, (to[1] - src[1]) / hypot * scale
        return dx, dy

    def update(self):
        self.move_vector = self.get_move_vector()
        if dist_sq(self.rect.center, self.target_rect.center) >= 25:
            self.rect.move_ip(*self.move_vector)
        else:
            self.target.get_attacked(self.damage)
            self.kill()
