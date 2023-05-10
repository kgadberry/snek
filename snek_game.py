"""
Classic(ish) snake game using Pyxel library.
"""

import time
import pyxel, settings, common.utils as utils
from common.grid import Grid
from common.snake import Snake
from common.item_manager import ItemManager

@staticmethod
def center_text(text: str, page_width: int, char_width: int = pyxel.FONT_WIDTH):
    """Helper function for calculating the start x value for centered text."""

    text_width = len(text) * char_width
    return (page_width - text_width) // 2
@staticmethod
def level_coordinates(level: int) -> utils.Point:
    """Returns the tilemap coordinates for the specified level."""
    level_x = ((level - 1) * settings.GRID_WIDTH) % 256
    level_y = ((level * settings.GRID_WIDTH) // 256) * settings.GRID_HEIGHT
    return utils.Point(level_x, level_y)

class SnekGame:
    """Main game class."""
    def __init__(self, starting_level: int = settings.STARTING_LEVEL):
        """Initialize game and variables."""

        #Initialize game window and load assets
        pyxel.init(
            width = settings.GRID_WIDTH * 8, 
            height = (settings.GRID_HEIGHT * 8) + 8, 
            title = settings.TITLE, 
            fps = settings.FPS, 
            display_scale = settings.SCALE
            )
        pyxel.load(settings.ASSET_FILE)

        self._level_map = pyxel.tilemap(0) #Load the tilemap
        self._grid = None
        self._item_manager = None
        self._snake = None
        self._space_released = True

        #Debug variables
        self._frame_count = 0

        #Initialize game variables
        self.score = 0 
        self.level = starting_level
        self.game_paused = False
        self.game_over = False
        self.controls_reversed = False

        self.start_level(self.level)
        pyxel.run(self.update, self.draw)

    def start_level(self, level: int):
        """Starts the specified level."""
        self.pause()
        self.reset(level)
        self.set_camera()

    def set_camera(self):
        """Sets the camera to the current level."""
        pyxel.camera(settings.LEVELS[self.level]['x'], settings.LEVELS[self.level]['y'])
    def initialize_grid(self, level: int):
        """Initializes the grid with the current level's tilemap."""
        return Grid(self._level_map, settings.GRID_WIDTH, settings.GRID_HEIGHT, settings.LEVELS[self.level]['x'], settings.LEVELS[self.level]['y'])
    def initialize_items(self):
        """Initializes the item manager."""
        return ItemManager(self._grid)
    def initialize_snake(self):
        """Initializes the snake."""
        return Snake(self._grid, self._grid.character_start_position)
    
    def clear(self):
        """Clears the screen."""
        pyxel.cls(settings.BACKGROUND_COLOR)
    def reset(self, level: int):
        """Initialize snake, score, items, etc."""
        self.score = 0
        self.level = level
        self.game_over = False
        self.controls_reversed = False

        self.clear()
        self._grid = self.initialize_grid(self.level)
        self._item_manager = self.initialize_items()
        self._snake = self.initialize_snake()
        # pyxel.playm(0, loop = True) #TODO: add music

    def end(self):
        """Ends the current game."""
        self.game_over = True
    def pause(self):
        """Pauses the game."""
        self.game_paused = True
    def unpause(self):
        """Unpauses the game."""
        self.game_paused = False

    def move_snake(self, direction: int):
        """Checks if the snake can move and moves it."""
        new_head_position = self._snake.get_next_tile(direction)
        elongate_snake = False

        #Check if the snake is going to collide with itself or an item
        if new_head_position.tile_type in [
            "snake_body_straight",
            "snake_body_left",
            "snake_body_right",
            "snake_tail",
            "wall"
            ]:
            self.end() #End the game if the snake is going to collide with itself
        elif new_head_position.tile_type in [
            "item_bomb",
            "item_lemon",
            "item_apple",
            "empty"
            ]:
            match new_head_position.tile_type:
                case "empty": #Does nothing
                    pass
                case "item_bomb": #Explodes the snake
                    self._grid.update_tile(*new_head_position.grid_coordinates,
                                          "animation.exploding_bomb", is_animated = True, animation_cycles = 1)
                    self.end()
                    pass
                case "item_lemon": #Reverses controls until an apple is eaten
                    if self.controls_reversed:
                        self.score += 3
                    self.controls_reversed = True
                    elongate_snake = True
                    pass
                case "item_apple": #Makes the snake longer
                    if self.controls_reversed == True:
                        self.controls_reversed = False
                        self.score += 3
                    else:
                        self.score += 1
                    elongate_snake = True
                    pass
                case _:
                    pass
            if not self.game_over:
                self._snake.move_forward(direction, elongate_snake)
                if elongate_snake:
                    self._item_manager.remove_item(new_head_position.grid_coordinates)

    def update(self):
        """Update game logic."""

        self._grid.update()

        # Pause/unpause game if space is pressed
        if pyxel.btn(pyxel.KEY_SPACE):
            if self._space_released: # Require spacebar to be released before pausing/unpausing
                self._space_timer = time.time()
                if self.game_over:
                    # Restart game if space is pressed and game is over
                    self.reset(self.level)
                elif self.game_paused:
                    # Unpause game if space is pressed and game is paused
                    self.unpause()
                else:
                    # Pause game if space is pressed and game is not paused
                    self.pause()
            self._space_released = False
        else:
            self._space_released = True

        
        if not (self.game_paused or self.game_over):
            # Update game if not paused       
            if not self.game_over and not self.game_paused:   
                # Check for key presses and change direction accordingly
                current_direction = self._snake.body[0]._rotation
                new_direction = None
                # Ensure the snake doesn't double back on itself
                if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                    if not current_direction == settings.DIRECTIONS["down"]:
                        new_direction = settings.DIRECTIONS["up"]
                elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
                    if not current_direction == settings.DIRECTIONS["up"]:
                        new_direction = settings.DIRECTIONS["down"]
                elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                    if not current_direction == settings.DIRECTIONS["right"]:
                        new_direction = settings.DIRECTIONS["left"]
                elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
                    if not current_direction == settings.DIRECTIONS["left"]:
                        new_direction = settings.DIRECTIONS["right"]        
            
            if settings.DEBUG:
                print("New direction:", new_direction)
                print("Before move - Snake body coordinates:", [tile.grid_coordinates for tile in self._snake.body])

            if new_direction is not None and new_direction != current_direction:
                if self.controls_reversed: #TODO: verify snake can't double back on itself
                    # Reverse the direction if controls are reversed
                    new_direction = (new_direction + 2) % 4
                self.move_snake(new_direction)
            else:
                self.move_snake(current_direction)
                if settings.DEBUG:
                    print("After move - Snake body coordinates:", [tile.grid_coordinates for tile in self._snake.body])
                    print("New head position coordinates:", self._snake.body[0].grid_coordinates)

            #Update the items if the game is not over
            if not self.game_over:
                self._item_manager.update()

    def draw(self):
        """Draw game graphics."""

        self.clear() #Clear the screen
        self._grid.draw_all_tiles() #Draw the grid

        # Draw the score with dark blue background
        pyxel.rect(0, 0, pyxel.width, 10, 1)
        pyxel.text(center_text(f"Score: {self.score}", pyxel.width), 3, f"Score: {self.score}", pyxel.COLOR_WHITE)
        if settings.DEBUG:
            self._frame_count += 1
            pyxel.text(3, 3, f"{self._frame_count}", pyxel.COLOR_YELLOW)


        if self.game_over:
            #Draw the game over screen
            pyxel.text(center_text("GAME OVER", pyxel.width), 
                   pyxel.height // 2, 
                   "GAME OVER", 
                   pyxel.COLOR_RED)
            pyxel.text(center_text("press SPACE to restart", pyxel.width), 
                    pyxel.height // 2 + 10, 
                    "press SPACE to restart", 
                    pyxel.COLOR_WHITE)
        elif self.game_paused:
            #Draw the start screen
            for i, line in enumerate(settings.START_TEXT):
                pyxel.text(center_text(line, pyxel.width),
                        pyxel.height // 2 - 20 + (i * 10), 
                        line, 
                        pyxel.COLOR_WHITE)
    
SnekGame()