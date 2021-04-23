import pygame as pg


class Soldier(pg.sprite.Sprite):
    def __init__(self, health, damage, owner_id):
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.damage = damage
        self.is_dead = False
        self.path = None
        self.owner = owner_id

    def update(self):
        if self.path is not None:
            pass

    def get_attacked(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_dead = True

    def attacks(self, building):
        building.get_attacked(self.damage)

  
        


