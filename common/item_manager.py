import settings, common.grid as grid

import random
import time

class ItemManager:
    def __init__(self, grid: grid.Grid,):
        self.grid = grid
        self.spawn_interval = settings.ITEM_SPAWN_INTERVAL
        self.despawn_interval = settings.ITEM_DESPAWN_INTERVAL
        self.last_spawn_time = time.time()
        self.items = []

    def update(self):
        """Updates the item manager."""
        # Spawn items
        if time.time() - self.last_spawn_time >= self.spawn_interval:
            self.spawn_item()
            self.last_spawn_time = time.time()

        # Despawn items
        for item in self.items:
            if time.time() - item["spawn_time"] >= self.despawn_interval:
                self.remove_item(item)
    def get_item(self, tile):
        """Returns the item at the specified tile."""
        for item in self.items:
            if item["tile"] == tile:
                return item
        return None

    def spawn_item(self):
        """Spawns an item at a random empty tile."""
        item_types = list(settings.ITEM_PROBABILITY.keys())
        item_weights = list(settings.ITEM_PROBABILITY.values())
        item_type = random.choices(item_types, weights = item_weights, k = 1)[0]

        if self.grid.empty_tiles:
            spawn_tile = random.choice(self.grid.empty_tiles)
            self.grid.update_tile(spawn_tile.x, spawn_tile.y, item_type, 0)
            self.items.append({"tile": spawn_tile, "spawn_time": time.time()})
    def remove_item(self, item):
        """Removes an item from the grid and the item list."""
        if item in self.items:
            self.items.remove(item)
            self.grid.update_tile(item["tile"].x, item["tile"].y, "empty")