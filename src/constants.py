import arcade

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_RATE = 1 / 144

# Player constants
PLAYER_MOVEMENT_SPEED = 500
PLAYER_FRICTION = 0.9999
PLAYER_ASSETS_DIR = "resources/Players"
PLAYER_CONFIG_FILE = "resources/animation_config/players_config.json"
DEAD_ZONE = 0.1
MAX_HEALTH = 100

# Enemy constants
ZOMBIE_MOVEMENT_SPEED = 100
ENEMY_CONFIG_FILE = "resources/animation_config/enemies_config.json"

# Health bar constants
HEALTHBAR_WIDTH = 75
HEALTHBAR_HEIGHT = 10
INDICATOR_BAR_OFFSET = 32

# Constants for bullet properties
BULLET_SPEED = 100
BULLET_LIFE = 0.5
BULLET_DAMAGE = 10

# Scaling constants
CHARACTER_SCALING = 0.3
TILE_SCALING = 2
COLLECTABLE_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Camera constants
FOLLOW_DECAY_CONST = 0.3
VIEWPORT_MARGIN = 250
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN

# Camera zoom constants
ZOOM_STEP = 0.1
MAX_ZOOM = 2.0
MIN_ZOOM = 0.5

# Key constants
LEFT_KEY = arcade.key.LEFT
RIGHT_KEY = arcade.key.RIGHT
UP_KEY = arcade.key.UP
DOWN_KEY = arcade.key.DOWN
W_KEY = arcade.key.W
A_KEY = arcade.key.A
S_KEY = arcade.key.S
D_KEY = arcade.key.D
ZOOM_KEY = arcade.key.LCTRL
FULLSCREEN_KEY = arcade.key.F11

# Asset directories and configuration files
ZOMBIE_ASSETS_DIR = "resources/Zombies"
ZOMBIE_CONFIG_FILE = "resources/animation_config/zombies_config.json"