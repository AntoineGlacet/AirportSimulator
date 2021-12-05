import pygame as pg
from statistics import mean

# parameters

MAP_NAME = "covid_arrival_local_files.tmx"
TILESIZE = 32
ZOOM = 0.5
FPS = 60 * 5
STEPS_PER_UPDATE = 1 / 3600 * 5
TAG_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (200, 200, 200)
SNAKE_QUEUE_COLOR = (180, 180, 220)
CONFIG = {
    "fps": FPS,
    "tilesize": TILESIZE,
    "zoom": ZOOM,
    "dt": STEPS_PER_UPDATE,
}

# Randomness for processing times
RANDOM = True
RANDOM_SIGMA = 0.1  # times Mu

# Mob settings
MOB_IMG = "manBlue_stand.png"
MOB_ACC = 9999999 * TILESIZE
MOB_MAX_SPEED = 1 * TILESIZE * 60 * 3600 * STEPS_PER_UPDATE

SPAWN_BOX = (-20, 10, -12, -8)
SPAWN_BOX_CENTER = (mean(SPAWN_BOX[0:2]), mean(SPAWN_BOX[2:4]))
SPAWN_POINTS = [(x, y) for x in range(-20, 10) for y in range(-12, -8)]

REACH_TOLERANCE = 0.5

WANDER_RING_DISTANCE = 2
WANDER_RING_RADIUS = 1
ATTRACTION_RATIO = 0

# Layers
QUEUE_LAYER = 2
MOB_LAYER = 3
BACKGROUND_LAYER = 1

# test airline class
PT_CHECKIN_1step = 150 / 60
