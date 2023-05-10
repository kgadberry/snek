import settings, pyxel, common.utils as utils

class Tile:
    """Tile object class."""
    def __init__(self, grid_x: int, grid_y: int, tile_type: str, rotation: int):
        # Tile variables
        self._x: int = grid_x
        self._y: int = grid_y
        self._tile_type: str = tile_type
        self._rotation: int = rotation

    @property
    def x(self) -> int:
        """Returns tile x coordinate as an integer."""
        return self._x
    @property
    def y(self) -> int:
        """Returns tile y coordinate as an integer."""
        return self._y
    @property
    def grid_coordinates(self) -> utils.Point:
        """Returns tile coordinates as a Point object."""
        return utils.Point(self._x, self._y)
    @property
    def tile_type(self) -> str:
        """Returns tile type as a string."""
        return self._tile_type
    @property
    def rotation(self) -> int:
        """Returns tile rotation as an integer."""
        return self._rotation
    @property
    def is_animated(self) -> bool:
        """Returns whether the tile is animated."""
        return False
class AnimatedTile(Tile):
    """Animated tile object class."""
    def __init__(self, grid_x: int, grid_y: int, tile_type: str, rotation: int, 
                    animation_cycles: int = -1, 
                    tile_type_after_animation: str = "empty", rotation_after_animation: int = 0):
        super().__init__(grid_x, grid_y, tile_type, rotation)
        # Animation variables
        self.current_animation_frame: int = 0
        self.animation_cycles_remaining: int = animation_cycles
        self._total_animation_frames: int = settings.TILES[tile_type][1]
        self._tile_type_after_animation: str = tile_type_after_animation
        self._rotation_after_animation: int = rotation_after_animation

    @property
    def total_animation_frames(self) -> int:
        """Returns the total number of animation frames."""
        return self._total_animation_frames
    @property
    def is_animated(self) -> bool:
            """Returns whether the tile is animated."""
            return True
    @property
    def tile_type_after_animation(self) -> str:
        """Returns the tile type after the animation is complete."""
        return self._tile_type_after_animation
    @property
    def rotation_after_animation(self) -> int:
        """Returns the rotation after the animation is complete."""
        return self._rotation_after_animation
class Grid:
    """Grid object class."""

    def __init__(self, tilemap: pyxel.Tilemap, width: int, height: int, level_x: int, level_y: int):
        self.tilemap = tilemap
        self.width = width
        self.height = height
        self.total_tiles = width * height
        self.tiles = [[] for _ in range(width)] #Initialize grid as a 2D list
        #Fill grid with empty tiles and keep track of them in a list
        self.empty_tiles = []
        for i in range(self.total_tiles):
            new_tile_x = i % width
            new_tile_y = int(i / width)
            self.tiles[new_tile_x].append(Tile(new_tile_x, new_tile_y, "empty", 0))
            self.empty_tiles.append(self.tiles[new_tile_x][new_tile_y])
        self.updated_tiles = [] #List of tiles that have been updated since the last frame
        self.animated_tiles = [] #List of tiles that are currently animating
        self.character_tiles = [] #List of tiles that are currently occupied by the character
        self.character_start_position = self.load_level(level_x, level_y, self.tilemap) #Load the character's starting position from the level file

    def get_tile(self, x: int, y: int) -> Tile:
        """Returns tile at (x,y)."""
        return self.tiles[x % len(self.tiles)][y % len(self.tiles[0])]
    def update_tile(self, x: int, y: int, tile_type: str, rotation: int = 0,
                    is_animated: bool = False, 
                    animation_cycles: int = -1, 
                    tile_type_after_animation: str = "empty",
                    rotation_after_animation: int = 0,
                    animation_starting_frame: int = 0) -> Tile:
        """Change, draw, and return the tile at (x,y)."""
        old_tile = self.get_tile(x, y)
        new_tile = None
        if is_animated:
            new_tile = AnimatedTile(x, y, tile_type, rotation,
                                           animation_cycles, tile_type_after_animation, rotation_after_animation)
            new_tile.current_animation_frame = animation_starting_frame
            self.animated_tiles.append(new_tile)
        else:
            new_tile = Tile(x, y, tile_type, rotation)

        # Maintain list of empty tiles
        if old_tile._tile_type == "empty":
            self.empty_tiles.remove(old_tile)
        if new_tile._tile_type == "empty":
            self.empty_tiles.append(new_tile)

        # Maintain list of updated tiles
        if (
            (old_tile._tile_type != new_tile._tile_type) or (old_tile._rotation != new_tile._rotation)
            or (old_tile.is_animated and old_tile.current_animation_frame != new_tile.current_animation_frame)
        ):
            self.updated_tiles.append(new_tile)

        self.tiles[old_tile.x][old_tile.y] = new_tile
        return new_tile

    def load_level(self, level_x: int, level_y: int, tilemap: pyxel.Tilemap) -> utils.Point:
        """Loads a level from a tilemap and sets character starting coordinates."""
        character_start_position = utils.Point(self.width // 2, self.height // 2) #Set default character starting coordinates to the middle of the grid
        for i in range(self.total_tiles):
            new_tile_x = i % len(self.tiles) #Convert tile to grid coordinates
            new_tile_y = int(i / len(self.tiles))
            tilemap_x = (i % self.width) + level_x #Convert tile to tilemap/level coordinates
            tilemap_y = int(i / self.width) + level_y
            spritesheet_x, spritesheet_y = tilemap.pget(tilemap_x, tilemap_y) #Get tile from tilemap
            spritesheet_x *= 8; spritesheet_y *= 8 #Convert tile to pixel coordinates
            tile_type = settings.REVERSE_TILES[spritesheet_y] #Get tile type
            # Check if tile is animated
            if tile_type.startswith("animation."):
                animation_cycles = -1
                tile_type_after_animation = "empty"
                rotation_after_animation = 0
                self.update_tile(new_tile_x, new_tile_y, tile_type, is_animated = True,
                                 animation_starting_frame = (spritesheet_x // settings.TILE_size["width"]))
            elif tile_type != "start_marker":
                self.update_tile(new_tile_x, new_tile_y, tile_type, 
                                 rotation = (spritesheet_x // settings.TILE_SIZE["width"]))
            elif tile_type == "start_marker":
                character_start_position = utils.Point(new_tile_x, new_tile_y)
        return character_start_position

    def screen_coordinates(self, x: int, y: int,
                           horizontal_offset: int = 0, vertical_offset: int = 10) -> tuple:
        """Returns the screen coordinates of a grid tile."""
        return ((x * settings.TILE_SIZE["width"]) + horizontal_offset, (y * settings.TILE_SIZE["height"]) + vertical_offset)
    def sprite_coordinates(self, tile_type: str, rotation: int = 0, animation_frame: int = 0) -> tuple:
        """Returns the sprite coordinates of a tile from given animation frame or rotation value.
        If the tile is animated, the animation frame is used to determine y value. 
        Otherwise, the rotation value is used."""
        if tile_type.startswith("animation."):
            return (settings.TILES[tile_type][0], animation_frame * settings.TILE_SIZE["width"])
        else:
            return (settings.TILES[tile_type], rotation * settings.TILE_SIZE["width"])
    def draw_all_tiles(self):
        """Draws the entire grid of tiles on the screen."""
        for row in self.tiles:
            for tile in row:
                if tile.is_animated: # Update animated tiles
                    self.draw_tile(*self.screen_coordinates(tile.x, tile.y),
                                    *self.sprite_coordinates(tile.tile_type, animation_frame = tile.current_animation_frame))
                else: # Update static tiles
                    self.draw_tile(*self.screen_coordinates(tile.x, tile.y),
                                    *self.sprite_coordinates(tile.tile_type, tile.rotation))
        self.updated_tiles = [] #Clear list of updated tiles
    def draw_tile(self, x: int, y: int,
                  sprite_x: int, sprite_y: int, spritesheet_number: int = 0,
                  size_x = settings.TILE_SIZE["width"], size_y: int = settings.TILE_SIZE["height"]):
        """Draws an individual tile on the screen at (x,y)."""
        pyxel.blt(
            x, y,
            spritesheet_number,
            sprite_y, sprite_x,
            size_x, size_y,
            settings.TRANSPARENT_COLOR)

    def advance_animation(self, tile: AnimatedTile):
        """Advances the animation of the tile by one frame."""
        if tile.current_animation_frame < (tile.total_animation_frames - 1):
            tile.current_animation_frame += 1
        else:
            tile.current_animation_frame = 0
            if tile.animation_cycles_remaining > 1 and tile.animation_cycles_remaining != -1:
                tile.animation_cycles_remaining -= 1
            else:
                self.stop_animation(tile)
    def stop_animation(self, tile: AnimatedTile):
        """Stops the animation of the tile."""
        self.update_tile(tile.x, tile.y, 
                         tile.tile_type_after_animation, tile.rotation_after_animation)
        self.animated_tiles.remove(tile)
    def update(self):
        """Advances animations by one frame and redraws updated tiles."""
        for tile in self.animated_tiles:
            self.advance_animation(tile)

    def get_neighbor(self, tile: Tile, direction: int = 0) -> Tile:
        """Returns the neighboring tile in the specified direction."""
        if direction == 0:
            return self.get_tile(tile.x, tile.y - 1)
        elif direction == 1:
            return self.get_tile(tile.x + 1, tile.y)
        elif direction == 2:
            return self.get_tile(tile.x, tile.y + 1)
        elif direction == 3:
            return self.get_tile(tile.x - 1, tile.y)
    def get_relative_neighbor(self, tile: Tile, direction: int = 0) -> Tile:
        """Returns the neighboring tile in the specified direction relative to the current rotation of the tile."""
        return self.get_neighbor((tile.rotation + direction) % 4)
    def get_next(self, tile: Tile) -> Tile:
        """Returns the tile in front."""
        return self.get_relative_neighbor(tile, 0)
    def get_previous(self, tile: Tile) -> Tile:
        """Returns the tile behind."""
        return self.get_relative_neighbor(tile, 2)      