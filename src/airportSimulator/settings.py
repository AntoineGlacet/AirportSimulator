import pygame as pg
from statistics import mean

# to activate the test for check in opening
DEPARTURE = True

# parameters
TILESIZE = 32
ZOOM = 0.5
# MAP_NAME = "test.tmx"
DRAW_MAP = True
MAP_NAME = "covid_arrival_local_files.tmx"

TAG_COLOR = (0, 255, 0)

BACKGROUND_COLOR = (0, 0, 0)
SNAKE_QUEUE_COLOR = (180, 180, 220)

# time and frames
# real time
FPS = 60
STEPS_PER_UPDATE = 1 / 3600 * 5

QUEUE_X = -10
QUEUE_Y = 0
N_FOLD = 4
N_POSITION_1FOLD = 15
OVERFLOW_RATIO = 1000

# Randomness for processing times
RANDOM = True
RANDOM_SIGMA = 0.1  # times Mu

PT = 3
N = 4

P = 3  # pax per minute
H = 2  # during H hours

# config
CONFIG = {
    "fps": FPS,
    "tilesize": TILESIZE,
    "zoom": ZOOM,
    "dt": STEPS_PER_UPDATE,
}


# Mob settings
MOB_IMG = "manBlue_stand.png"
MOB_ACC = 9999999 * TILESIZE
MOB_MAX_SPEED = 1 * TILESIZE * 60 * 3600 * STEPS_PER_UPDATE
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)


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
PT_CHECKIN_2step = 100 / 60
PT_CHECKIN_1step = 150 / 60
