# queue_pywin.py
# to be revised with default config and config init like elsewhere
from matplotlib.pyplot import text
import pygame as pg
from settings import *
import random
import math
import numpy

vec = pg.math.Vector2


class Fix_sprite(pg.sprite.Sprite):
    """
    fix postion sprite
    """

    def __init__(self, win, tmx_object, layer, **kwargs):
        self._layer = layer
        self.groups = win.all_sprites, win.background_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.win = win
        self.tmx_object = tmx_object

        self.x = self.tmx_object.x
        self.y = self.tmx_object.y
        self.width = self.tmx_object.width
        self.height = self.tmx_object.height
        self.pos = vec(self.x, self.y)
        self.rot = self.tmx_object.rotation

        self.image = self.win.map.tmxdata.get_tile_image_by_gid(self.tmx_object.gid)

        self.image = pg.transform.scale(
            self.image,
            (self.width, self.height),
        )

        self.image = pg.transform.rotate(
            self.image,
            -self.rot,
        )

        # dirty fix for stupid tiled/pygame rotation difference
        if self.rot == -90:
            self.x -= self.height
            self.y += self.height - self.width

        if self.rot == 90:
            self.y += self.height

        self.image_ini = self.image.copy()

    def update(self):
        pass


class Mob_fixed(pg.sprite.Sprite):
    """
    fix postion mob to be used elsewhere
    """

    def __init__(self, win, x0, y0, n, **kwargs):
        self._layer = MOB_LAYER
        self.groups = win.all_sprites, win.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.win = win
        self.n = n
        self.x = x0
        self.y = y0
        self.pos = vec(self.x, self.y)
        self.width = 0.8 * TILESIZE
        self.heigth = 0.8 * TILESIZE

        self.image = win.scaled_mob_img.copy()

        if self.win.zoom > 0.5:
            self.draw_tag()

    def draw_tag(self):
        text_tag = self.win.tag_font.render("{}".format(self.n), True, TAG_COLOR)
        text_rect = text_tag.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_tag, text_rect)

    def update(self):
        # killed every frame
        self.kill()


class Mob_variable(pg.sprite.Sprite):
    """
    Mob spawns at (x0,y0), goes to a "queue" and disappears
    """

    def __init__(self, win, x0, y0, n, target_queue, **kwargs):
        self._layer = MOB_LAYER
        self.groups = win.all_sprites, win.mobs, win.moving_mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.win = win
        self.x = x0
        self.y = y0
        self.n = n
        self.queue = target_queue
        self.arrived = False
        self.wandering = False

        # kwargs
        self.__dict__.update(kwargs)

        # image and initial position and hitbox
        self.image = win.scaled_mob_img.copy()
        self.pos = vec(self.x, self.y) * TILESIZE
        self.vel = vec(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.acc = vec(0, 0)
        self.rot = 0

    def goto(self, x, y):
        target = vec(x, y)
        target_dist = target - self.pos

        # go to target
        self.rot = target_dist.angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.win.scaled_mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(MOB_ACC, 0).rotate(-self.rot)

        self.vel += self.acc * self.win.dt
        if self.vel.length() > MOB_MAX_SPEED:
            self.vel.scale_to_length(MOB_MAX_SPEED)
        self.pos += self.vel * self.win.dt
        (self.x, self.y) = self.pos

        target_dist = target - self.pos
        return target_dist

    def wander(self):
        circle_pos = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
        target = circle_pos + vec(WANDER_RING_RADIUS, 0).rotate(random.uniform(0, 360))
        self.goto(*target)

    def goto_queue(self):
        target = self.queue.dct_centers_overflow[len(self.queue.pax_list)]
        target_dist = self.goto(*target)

        if target_dist.length() < REACH_TOLERANCE * TILESIZE:
            self.kill()
            self.arrived = True

    def update(self):
        if self.wandering == True:
            self.wander()
        else:
            self.goto_queue()

        if self.win.zoom > 0.5:
            self.draw_tag()

    def draw_tag(self):
        text_tag = self.win.tag_font.render("{}".format(self.n), True, TAG_COLOR)
        text_rect = text_tag.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_tag, text_rect)


class Snake_queue(pg.sprite.Sprite):
    def __init__(self, win, x, y, config={}):
        self._layer = QUEUE_LAYER
        self.groups = win.all_sprites, win.snake_queues
        pg.sprite.Sprite.__init__(self, self.groups)

        self.win = win

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # define position and image
        self.x = x
        self.y = y
        self.pos = vec(x, y) * TILESIZE
        self.width = self.N_position_1fold
        self.height = self.N_fold
        self.x_exit = self.x
        self.y_exit = self.y + self.height

        # Update configurations TO BE CHANGED for now it's double the trouble
        for attr, val in config.items():
            setattr(self, attr, val)

        self.N_position_total = self.N_fold * self.N_position_1fold
        self.update_dct_centers()

    def set_default_config(self):
        self.N_fold = 4
        self.N_position_1fold = 15
        self.overflow_ratio = OVERFLOW_RATIO
        self.pax_list = []
        self.child_sprites = []

    def update_dct_centers(self):
        # dict with the coordinates of each waiting position, including overflow
        dct_centers_overflow = {
            n: (0, 0) for n in range(self.overflow_ratio * self.N_position_total)
        }
        for n in dct_centers_overflow:
            row = n // self.N_position_1fold
            if row % 2 == 0:
                col = (n) % self.N_position_1fold
            else:
                col = self.N_position_1fold - ((n) % self.N_position_1fold) - 1
            x = self.x + col
            y = self.y + self.height - (row + 1)
            dct_centers_overflow[n] = vec(int(x), int(y)) * TILESIZE

        self.dct_centers_overflow = dct_centers_overflow

    def change_config(self, x, y, N_position_1fold, N_fold):
        # define position and image
        self.x = x
        self.y = y
        self.N_position_1fold = N_position_1fold
        self.N_fold = N_fold
        self.pos = vec(x, y) * TILESIZE
        self.width = N_position_1fold
        self.height = N_fold
        self.x_exit = self.x
        self.y_exit = self.y + self.height

        self.N_position_total = self.N_fold * self.N_position_1fold
        self.image = pg.Surface(
            (
                self.width * TILESIZE * self.win.zoom,
                self.height * TILESIZE * self.win.zoom,
            )
        )
        self.image.fill(SNAKE_QUEUE_COLOR)
        self.update_dct_centers()

    def empty_queue_to_wander(self):
        self.pax_list = []
        pass

    def update(self):
        # update the number of people queueing
        for sprite in self.child_sprites:
            sprite.kill()
            del sprite
        self.child_sprites = []
        for index, n in enumerate(self.pax_list):
            pos = self.dct_centers_overflow[index]
            self.child_sprites.append(Mob_fixed(self.win, pos.x, pos.y, n))
