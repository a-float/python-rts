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
        self.flipped = False
        self.sprites = []
        self.sprites.append(config.gfx['units']['soldier'])
        self.sprites.append(config.gfx['units']['soldier_2'])
        self.current_sprite = 0
        self.movement_iter = 0
        self.image = config.gfx['units']['soldier']
        self.image = pg.transform.scale(self.image, (config.UNIT_SIZE,)*2)
        self.speed = 1
        self.tile = None
        self.tile_index = 1
        self.health_image = config.gfx['utils']['full_hp']
        self.health_image = pg.transform.scale(self.health_image, (config.UNIT_SIZE,)*2)
        self.health_rect = None
        self.damage_timer = 0
        self.damage_image = config.gfx['utils']['boom']
        self.damage_image = pg.transform.scale(self.damage_image, (config.TILE_SPRITE_SIZE,) * 2)
        self.damage_rect = None
        self.is_dead = False
        self.dying_timer = 10

    def release(self, path):
        self.path = path
        self.tile = self.path.tiles[0]
        self.tile.soldiers.append(self)
        if self.type == 1:
            self.sprites = []
            self.sprites.append(config.gfx['units']['swordsman'])
            self.sprites.append(config.gfx['units']['swordsman_2'])
            self.image = config.gfx['units']['swordsman']
        elif self.type == 2:
            self.sprites = []
            self.sprites.append(config.gfx['units']['shieldman'])
            self.sprites.append(config.gfx['units']['shieldman_2'])
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
                self.image = pg.transform.flip(self.image, True, False)

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
        self.damage_timer = 10
        if self.health <= 0:
            print("IM DEAD!")
            self.is_dead = True
            if self in self.tile.soldiers:
                self.tile.soldiers.remove(self)
            del self

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
            surface.blit(self.damage_image, self.damage_rect)
            self.damage_timer -= 1
        health_ratio = self.health / self.max_health
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
