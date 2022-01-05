from typing import NamedTuple
import numpy as np
import matplotlib.pyplot as plt
import pygame as pg
from pygame import gfxdraw
import numpy as np
from os import path, sep
from settings import *
from sprites import *
from tiledmap import *


from collections import namedtuple


class Window:
    def __init__(self, sim, config={}):

        pg.init()
        # Simulation to draw
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        self.previous_zoom = self.zoom

        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.mobs = pg.sprite.Group()
        self.moving_mobs = pg.sprite.Group()
        self.snake_queues = pg.sprite.Group()
        self.airlines = pg.sprite.Group()
        self.background_group = pg.sprite.Group()

        # Create a pg window
        self.screen = pg.display.set_mode((self.width, self.height))
        pg.display.flip()

        # Fixed fps
        self.clock = pg.time.Clock()

        # To draw text
        pg.font.init()
        self.text_font = pg.font.SysFont("Lucida Console", 16)
        self.tag_font = pg.font.SysFont("Calibri", 16)

        # Create a plot window
        # creating initial data values
        # of x and y
        self.i = 0
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)

        # to run GUI event loop
        plt.ion()

        # here we are creating sub plots
        self.figure, ax = plt.subplots(figsize=(10, 8))
        (self.line1,) = ax.plot(self.x, self.y)

        # setting title
        plt.title("Geeks For Geeks", fontsize=20)

        # setting x-axis label and y-axis label
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")

        self.load_data()

    def set_default_config(self):
        """Set default configuration"""
        self.width = 1024
        self.height = 768
        self.tilesize = 32
        self.bg_color = BACKGROUND_COLOR

        self.fps = 60
        self.zoom = 5

        self.offset = (-20 * TILESIZE, -20 * TILESIZE)

        self.mouse_last = (0, 0)
        self.mouse_down = False

    def load_tmx_objects(self):
        self.dct_tmx = {}
        for object_group in self.map.tmxdata.objectgroups:
            if "fixed_sprite" in object_group.properties.keys():
                layer = object_group.properties["layer"]
                for obj in object_group:
                    Fix_sprite(
                        self,
                        obj,
                        layer,
                    )

            if "rectangles" in object_group.properties.keys():
                Rectangle = namedtuple("Rectangle", ["x", "y", "width", "height"])
                for obj in object_group:
                    self.dct_tmx[obj.name] = Rectangle(
                        obj.x, obj.y, obj.width, obj.height
                    )

            if "vectors" in object_group.properties.keys():
                Vector = namedtuple("Vector", ["x", "y"])

            if "points" in object_group.properties.keys():
                Point = namedtuple("Point", ["x", "y"])
                for obj in object_group:
                    self.dct_tmx[obj.name] = Point(obj.x, obj.y)

    def load_data(self):
        # initialize paths
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "img")
        map_folder = path.join(game_folder, "maps")
        self.map = TiledMap(path.join(map_folder, MAP_NAME))

        # mob image
        self.mob_img_ini = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.scaled_mob_img = pg.transform.scale(
            self.mob_img_ini, (0.8 * TILESIZE * self.zoom, 0.8 * TILESIZE * self.zoom)
        )

        # tmx objects
        self.load_tmx_objects()

    def loop(self, loop=None):
        """Shows a window visualizing the simulation and runs the loop function."""

        # Draw loop
        running = True
        while running:

            # Update airlines firts
            self.airlines.update()

            # Update sprites
            self.all_sprites.update()

            # Draw simulation
            self.draw()

            # Update window
            pg.display.update()
            self.clock.tick(self.fps)

            # Store zoom
            self.previous_zoom = self.zoom

            # Handle all events
            for event in pg.event.get():
                # Quit program if window is closed
                if event.type == pg.QUIT:
                    running = False
                # Handle mouse events
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # If mouse button down
                    if event.button == 1:
                        # Left click
                        x, y = pg.mouse.get_pos()
                        x0, y0 = self.offset
                        self.mouse_last = (x - x0 * self.zoom, y - y0 * self.zoom)
                        self.mouse_down = True
                    if event.button == 4:
                        # Mouse wheel up
                        self.zoom *= (self.zoom ** 2 + self.zoom / 4 + 1) / (
                            self.zoom ** 2 + 1
                        )
                    if event.button == 5:
                        # Mouse wheel down
                        self.zoom *= (self.zoom ** 2 + 1) / (
                            self.zoom ** 2 + self.zoom / 4 + 1
                        )
                elif event.type == pg.MOUSEMOTION:
                    # Drag content
                    if self.mouse_down:
                        x1, y1 = self.mouse_last
                        x2, y2 = pg.mouse.get_pos()
                        self.offset = ((x2 - x1) / self.zoom, (y2 - y1) / self.zoom)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.mouse_down = False

            # Update simulation
            if loop:
                loop(self.sim)

    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""

        def loop(sim):
            sim.run(steps_per_update)

        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width / 2 + (x + self.offset[0]) * self.zoom),
            int(self.height / 2 + (y + self.offset[1]) * self.zoom),
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width / 2) / self.zoom),
            int(-self.offset[1] + (y - self.height / 2) / self.zoom),
        )

    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))

    def line(self, start_pos, end_pos, color):
        """Draws a line."""
        gfxdraw.line(self.screen, *start_pos, *end_pos, color)

    def draw_grid(self, unit=50, color=(150, 150, 150)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit) + 1
        m_y = int(y_end / unit) + 1

        for i in range(n_x, m_x):
            self.line(
                self.convert((unit * i, y_start)),
                self.convert((unit * i, y_end)),
                color,
            )
        for i in range(n_y, m_y):
            self.line(
                self.convert((x_start, unit * i)),
                self.convert((x_end, unit * i)),
                color,
            )

    def draw_status(self):
        t = self.sim.env.now
        str_time = "{}h {}m {}s".format(
            int(t // 60), int(t % 60), int((t % 60 * 60) % 60)
        )
        text_time = self.text_font.render(
            "time={}, zoom={}".format(str_time, self.zoom), False, (0, 0, 0)
        )

        self.screen.blit(text_time, (0, 0))

    def draw_sprites(self):
        for sprite in self.background_group:
            if self.previous_zoom != self.zoom or self.sim.env.now == 0:
                sprite.image = pg.transform.scale(
                    sprite.image_ini,
                    (
                        sprite.image_ini.get_width() * self.zoom,
                        sprite.image_ini.get_height() * self.zoom,
                    ),
                )
            self.screen.blit(sprite.image, self.convert((sprite.x, sprite.y)))

        for sprite in self.snake_queues:
            sprite.image = pg.Surface(
                (
                    sprite.width * self.zoom,
                    sprite.height * self.zoom,
                )
            )
            sprite.image.fill(SNAKE_QUEUE_COLOR)
            self.screen.blit(sprite.image, self.convert((sprite.pos.x, sprite.pos.y)))

        for sprite in self.mobs:
            self.scaled_mob_img = pg.transform.scale(
                self.mob_img_ini,
                (TILESIZE * 0.8 * self.zoom, TILESIZE * 0.8 * self.zoom),
            )

            self.screen.blit(sprite.image, self.convert((sprite.pos.x, sprite.pos.y)))

    def draw_graph(self):
        # creating new Y values
        self.i += 1
        new_y = np.sin(self.x - 0.5 * self.i)

        # updating data values
        self.line1.set_xdata(self.x)
        self.line1.set_ydata(new_y)

        # drawing updated values
        self.figure.canvas.draw()

        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        self.figure.canvas.flush_events()

    def draw(self):
        # Fill background
        self.background(*self.bg_color)

        # Major and minor grid and axes
        self.draw_grid(self.tilesize, (220, 220, 220))

        # Draw sprites
        self.draw_sprites()

        # Draw status info
        self.draw_status()
        pg.display.flip()

        # Draw graphs
        if self.sim.env.now == 0:
            self.draw_graph()
            self.last_graph_draw_time = self.sim.env.now

        if self.sim.env.now - self.last_graph_draw_time > 1:
            self.draw_graph()
            self.last_graph_draw_time = self.sim.env.now
