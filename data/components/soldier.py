import pygame as pg

class Soldier(pg.sprite.Sprite):
    def __init__(self, health, demage):
        pg.sprite.Sprite.__init__(self)
        self.health = health
        self.demage = demage
        self.is_dead = False

    def get_attacked(demage):
        self.health -= demage
        if self.health <= 0:
            self.is_dead = True

    def attacks(self, building):
        building.get_attacked(self.demage)

  
        


