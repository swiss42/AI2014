# Dimensions of the arena
XDIM = 800
YDIM = 800

# Height of the wall
HEIGHT = 20
OFFSET = -HEIGHT/2

MAX_MOVEMENT_SPEED = 10
MAX_TURN_RADIANS = 0.35
MAX_VISION_RADIUS = 300

# Population size
pop_size = 50

# number of steps per lifetime
DEFAULT_LIFETIME = 200

# default speedup setting (there will be a 0.1 * 99 / 100 second delay between AI steps)
# BUG: when set to 100, makes the head bob up and down until you adjust the slider
DEFAULT_SPEEDUP = 99


# keyboard actions and what they correspond to
FIRST_PERSON_ACTIONS = {
    'FWD': (1, 0), 
    'CW': (0, -MAX_TURN_RADIANS), 
    'CCW': (0, MAX_TURN_RADIANS), 
    'BCK': (-1, 0)}
N_FIRST_PERSON_ACTIONS = len(FIRST_PERSON_ACTIONS) # number of actions


OBJECT_TYPE_OBSTACLE  = (1 << 0) # object type for walls
OBJECT_TYPE_TEAM_0 = (1 << 1) # object type for team 1
OBJECT_TYPE_TEAM_1 = (1 << 2) # object type for team 2 and turrets during training
OBJECT_TYPE_FLAG = (1 << 3) # object type for the flag
OBJECT_TYPE_LEVEL_GEOM = 0 # object type for the level geometry
OBJECT_TYPE_FPS = OBJECT_TYPE_LEVEL_GEOM # object type for first person agent


############################
### SENSOR CONFIGURATION ###
############################

# FriendRadarSensor
FRIEND_RADAR_SENSORS = [0, 1]

# EnemyRadarSensor
ENEMY_RADAR_SENSORS = [(90,12),(18,-3),(3,-18),(-12,-90),(-87,87)]

# Wall Ray Sensors
WALL_RAY_SENSORS = [90,45,0,-45,-90]

# Flag Radar Sensors
FLAG_RADAR_SENSORS = [(90,12),(18,-3),(3,-18),(-12,-90),(-87,87)]

# Number of sensors
N_SENSORS = len(FRIEND_RADAR_SENSORS) + len(FLAG_RADAR_SENSORS) + len(ENEMY_RADAR_SENSORS) + len(WALL_RAY_SENSORS) + 1

# Number of actions
N_ACTIONS = 2

# Network bias value
NEAT_BIAS = 0.3

#############################
### FITNESS CONFIGURATION ###
#############################

FITNESS_STAND_GROUND = "Stand ground"
FITNESS_STICK_TOGETHER = "Stick together"
FITNESS_APPROACH_ENEMY = "Approach enemy"
FITNESS_APPROACH_FLAG = "Approach flag"
FITNESS_HIT_TARGET = "Hit target"
FITNESS_AVOID_FIRE = "Avoid fire"
FITNESS_DIMENSIONS = [FITNESS_STAND_GROUND, FITNESS_STICK_TOGETHER,
    FITNESS_APPROACH_ENEMY, FITNESS_APPROACH_FLAG, FITNESS_HIT_TARGET,
    FITNESS_AVOID_FIRE]

FITNESS_INDEX = dict([(f,i) for i,f in enumerate(FITNESS_DIMENSIONS)])

import itertools
#DISPLAY_HINTS = itertools.cycle([None, 'fitness', 'time alive', 'hit points', 'genome id', 'species id', 'champion', 'debug'])
DISPLAY_HINTS = itertools.cycle([None, 'time alive', 'hit points', 'genome id', 'species id', 'champion'])
DISPLAY_HINT = DISPLAY_HINTS.next()

def getDisplayHint():
    return DISPLAY_HINT

def nextDisplayHint():
    global DISPLAY_HINT
    DISPLAY_HINT = DISPLAY_HINTS.next()
    return DISPLAY_HINT
