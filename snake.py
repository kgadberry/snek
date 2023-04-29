import settings, utils
from grid import Grid, Tile
from collections import deque

class Snake:
    """Snake object class."""

    def __init__(self, grid: Grid, snake_start: utils.Point):

        head_tile = grid.update_tile(snake_start.x, snake_start.y, "snake_head", 0)
        body_tiles = [
            grid.update_tile(
                head_tile.grid_coordinates.x,
                head_tile.grid_coordinates.y + (i + 1),
                "snake_body_straight",
                head_tile._rotation,
            )
            for i in range(settings.SNAKE_START_LENGTH)
        ]
        tail_tile = grid.update_tile(
            head_tile.grid_coordinates.x,
            body_tiles[-1].grid_coordinates.y + 1,
            "snake_tail",
            body_tiles[-1]._rotation,
        )

        # Include head and tail as part of the body deque
        self._body = deque([head_tile] + body_tiles + [tail_tile])
        self._grid = grid

    @property
    def body(self) -> deque:
        return self._body
    @property
    def grid(self) -> Grid:
        return self._grid

    def _body_tile_index(self, tile: Tile) -> int:
        """Returns the index of a tile in the snake's body if it exists, or -1 if not found."""
        indices = [index for index, body_tile in enumerate(self.body) if body_tile == tile]
        return indices[0] if indices else -1
    
    def get_next_tile(self, direction: int) -> Tile:
        """Returns the tile that the snake will move into if it moves in the specified direction."""
        return self.grid.get_neighbor(self.body[0], direction)

    def move_forward(self, new_direction: int, elongate_snake: bool = False):
        """Moves the snake 1 tile in the specified direction."""
        current_head_position = self.body[0]
        new_head_position = self.grid.get_neighbor(current_head_position, new_direction)

        #Move the head
        new_head = self.grid.update_tile(new_head_position.x, new_head_position.y, "snake_head", new_direction)
        old_head = self.body.popleft()
        self.body.appendleft(new_head)
        #Update the previous head location with a new body tile
        direction_change = (new_direction - old_head._rotation) % 4
        body_tile_type = "snake_body_straight"
        if direction_change == 1:
            body_tile_type = "snake_body_right"
        elif direction_change == 3:
            body_tile_type = "snake_body_left"

        self.body.insert(1, old_head)
        if settings.DEBUG:
            print("Old head body tile index should always be 1:", self._body_tile_index(old_head))
        self.grid.update_tile(old_head.x, old_head.y, body_tile_type, old_head._rotation)
        #Move the tail if the snake is not getting longer
        if not elongate_snake:
            old_tail = self.body.pop()
            self.grid.update_tile(old_tail.x, old_tail.y, "empty")
            new_tail = self.grid.update_tile(self.body[-1].x, self.body[-1].y, "snake_tail", self.body[-2]._rotation)