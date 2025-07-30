import arcade

MAP_WIDTH = 39
MAP_HEIGHT = 57

ENABLE_DEBUG = True
ENABLE_TESTING = True

# Testing constants
TESTING_OBJECTIVES = {
    "movement": "Test player movement controls (WASD/Arrow keys)",
    "combat": "Test shooting mechanics and enemy interaction",
    "car_interaction": "Test car part collection and car usage",
    "chest_interaction": "Test chest opening, part collection, and state management",
    "spawn_system": "Test zombie spawn points, validation, and distribution",
    "map_progression": "Test map transitions and level completion",
    "health_system": "Test health bar and damage mechanics"
}

# Testing validation thresholds
MOVEMENT_SPEED_THRESHOLD = 0.1
COLLISION_DISTANCE_THRESHOLD = 50
SHOOTING_ACCURACY_THRESHOLD = 0.3
HEALTH_CHANGE_THRESHOLD = 1

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_RATE = 1 / 144
FADE_RATE = 5

# Player constants
PLAYER_MOVEMENT_SPEED = 5
PLAYER_FRICTION = 0.9999
PLAYER_ASSETS_DIR = "resources/Players"
PLAYER_CONFIG_FILE = "resources/animation_config/players_config.json"
DEAD_ZONE = 0.1
MAX_HEALTH = 100
SHOOT_COOLDOWN = 0.1
SPAWN_POSITION = (500, 350)

# Enemy constants
ZOMBIE_MOVEMENT_SPEED = 2
ENEMY_CONFIG_FILE = "resources/animation_config/zombies_config.json"
ZOMBIE_RANDOM_MOVE_INTERVAL = 1

# Health bar constants
HEALTHBAR_WIDTH = 75
HEALTHBAR_HEIGHT = 10
INDICATOR_BAR_OFFSET = 32

# Bullet constants
BULLET_SPEED = 50
BULLET_LIFE = 0.5
BULLET_DAMAGE = 10

# Scaling constants
CHARACTER_SCALING = 0.15
TILE_SCALING = 1
COLLECTABLE_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING
TILE_SIZE = 89

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

# Map constants
MAP_WIDTH = 39
MAP_HEIGHT = 57
MAP_WIDTH_PIXEL=   MAP_WIDTH * TILE_SIZE * TILE_SCALING
MAP_HEIGHT_PIXEL = MAP_HEIGHT* TILE_SIZE * TILE_SCALING

# Car constants
CAR_SCALING = 1.0
INTERACTION_DISTANCE = 100
REQUIRED_CAR_PARTS = 5
CAR_SPRITE_PATH = "resources/Car/sprite/Viper.png"

# Chest constants
CHEST_SCALING = 1.0
CHEST_CLOSED_SPRITE = "resources/Chest/closed.png"
CHEST_OPEN_EMPTY_SPRITE = "resources/Chest/open-empty.png"
CHEST_OPEN_WITH_PART_SPRITE = "resources/Chest/open-glow1.png"
