############################################################ GAME PARAMETERS ############################################################
DEBUG = False #Enable debug mode
STARTING_LEVEL = 1 #Starting level
GRID_WIDTH = 32 #Grid size in tiles
GRID_HEIGHT = 32 #Grid size in tiles
TITLE = "SNEK - Eat Fruit, Don't Die!" #Game title
FPS = 8 #Frames per second
SCALE = 2 #Scale of the game window
ASSET_FILE = "bin.pyxres" #File containing assets
SPRITESHEET_NUMBER = 0
BACKGROUND_COLOR = 0 #Background is color 0
TRANSPARENT_COLOR = 6 #Color 6 is transparent
TILE_SIZE = {
    "width": 8,
    "height": 8
}
START_TEXT = [
    "use WASD or arrow keys to move",
    "apples give you points",
    "lemons give you even more points and confuses snek!",
    "-",
    "press SPACE to start/pause/unpause"
]

# Tile types and their vertical offset in the spritesheet.
# Horizontal offset is (rotation * 8)
TILES =  {
    "empty": 0,
    "snake_head": 8,
    "snake_body_straight": 16,
    "snake_tail": 24,
    "snake_body_left": 32,
    "snake_body_right": 40,
    "item_apple": 48,
    "item_lemon": 56,
    "item_bomb": 64,
    "wall": 72,
    "start_marker": 80,
    "animation.exploding_bomb": (88, 4),
}
REVERSE_TILES = {v: k for k, v in TILES.items()}
GAMEOVER_TILES = {
    "snake_head",
    "snake_body_straight",
    "snake_body_left",
    "snake_body_right",
    "snake_tail",
    "wall",
    "item_bomb",
}
# Levels and their corresponding starting coordinates
LEVELS = {
    1: {'x': 0, 'y': 0},
    2: {'x': 32, 'y': 0},
}
# Directions and their corresponding integer values
DIRECTIONS = {
    "up": 0,
    "right": 1,
    "down": 2,
    "left":  3
}

############################################################ SNAKE/ITEM PARAMETERS ############################################################

SNAKE_START_LENGTH = 3 #How many tiles the snake starts with
SNAKE_START_DIRECTION = DIRECTIONS["up"] #Snake starting direction

ITEM_SPAWN_INTERVAL = 2 #How many seconds between item spawns
ITEM_DESPAWN_INTERVAL = 60 #How many seconds before an item despawns
# Items and their corresponding probabilities, must add up to 1
ITEM_PROBABILITY = {
    "item_apple": 0.5,
    "item_lemon": 0.1,
    "item_bomb": 0.4
}