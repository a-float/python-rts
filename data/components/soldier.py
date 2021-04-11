import pygame as pg


class Soldier(pg.sprite.Sprite):
    def __init__(self, health, damage):
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.damage = damage
        self.is_dead = False

    def get_attacked(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_dead = True

    def attacks(self, building):
        building.get_attacked(self.damage)

  
        


