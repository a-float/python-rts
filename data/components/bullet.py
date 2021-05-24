import pygame as pg
import math


class Bullet(pg.sprite.Sprite):
    def __init__(self, image, source, target, damage):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.source = source
        self.target = target
        self.speed = 5
        self.target_center = self.target.tile.rect.center
        self.rect = self.image.get_rect(center=source.rect.center)
        self.move_vector = self.get_move_vector()
        self.damage = damage
        self.max_life = 20
        if self.move_vector[0] < 0 and self.move_vector[1] < 0:
            self.image = pg.transform.flip(self.image, True, False)
        elif self.move_vector[0] >= 0 and self.move_vector[1] >= 0:
            self.image = pg.transform.flip(self.image, False, True)
        elif self.move_vector[0] < 0 and self.move_vector[1] >= 0:
            self.image = pg.transform.flip(self.image, True, True)

    def get_move_vector(self):
        src, to = self.rect.center, self.target_center
        hypot = math.sqrt(dist_sq(src, to))
        scale = self.speed
        dx, dy = (to[0] - src[0]) / hypot * scale, (to[1] - src[1]) / hypot * scale
        return dx, dy

    def update(self): # todo fix, bullets sometimes miss
        if self.max_life <= 0:
            self.target.get_attacked(self.damage)
            self.kill()
        else:
            self.max_life -= 1
        if dist_sq(self.rect.center, self.target_center) >= 25:
            self.rect.move_ip(*self.move_vector)
        else:
            self.target.get_attacked(self.damage)
            self.kill()


def dist_sq(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2