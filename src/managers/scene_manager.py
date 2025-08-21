import arcade
import threading
from src.constants import TILE_SCALING, MAP_WIDTH_PIXEL, MAP_HEIGHT_PIXEL


class SceneManager:
    """Manages all scene-related functionality including map loading, tile \
        layers, and sprite lists."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.scene = arcade.Scene()
        self.tile_map = None
        self.wall_list = None
        self.threads = []

    def load_map(self, map_index):
        """Load a Tiled map and set up the scene."""
        map_name = f"resources/maps/map{map_index}.tmx"
        print(f"[SCENE] Loading map: {map_name}")

        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
        print(
            f"[SCENE] Tilemap loaded with {len(self.tile_map.sprite_lists)} \
                sprite lists"
        )

        self._setup_scene()
        self._setup_camera_bounds()
        self._setup_pathfinding_barrier()

    def _setup_scene(self):
        """Set up the scene with tile layers and sprite lists."""
        print(
            f"[SCENE] Available sprite lists: \
                {list(self.tile_map.sprite_lists.keys())}"
        )

        # Add tile layers to scene
        for layer_name in ("Dirt", "Grass", "Road"):
            self.scene.add_sprite_list(
                layer_name, sprite_list=self.tile_map.sprite_lists[layer_name]
            )

        # Add walls layer
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.scene.add_sprite_list("Walls", sprite_list=self.wall_list)

        # Add sprite lists for entities
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("CarsLayer")

        print("[SCENE] Added tile layers to scene")

    def _setup_camera_bounds(self):
        """Set up camera bounds based on the tile map."""
        self.game_view.camera_manager.setup_camera_bounds(self.tile_map)

    def _setup_pathfinding_barrier(self):
        """Set up pathfinding barrier for AI navigation."""

        def create_pathfind_barrier():
            with self.game_view.pathfind_barrier_thread_lock:
                if self.game_view.pathfind_barrier is None:
                    self.game_view.pathfind_barrier = arcade.AStarBarrierList(
                        moving_sprite=self.game_view.player,
                        blocking_sprites=self.wall_list,
                        grid_size=30,
                        left=0,
                        right=MAP_WIDTH_PIXEL,
                        bottom=0,
                        top=MAP_HEIGHT_PIXEL,
                    )

        self._start_thread(create_pathfind_barrier)

    def _start_thread(self, target_func):
        """Start a thread and add it to the threads list."""
        thread = threading.Thread(target=target_func)
        thread.start()
        self.threads.append(thread)

    def get_scene(self):
        """Get the current scene."""
        return self.scene

    def get_tile_map(self):
        """Get the current tile map."""
        return self.tile_map

    def get_wall_list(self):
        """Get the wall list for collision detection."""
        return self.wall_list

    def clear_scene(self):
        """Clear the current scene and create a new one."""
        self.scene = arcade.Scene()
        print("[SCENE] New scene created")

    def join_threads(self):
        """Join all threads to ensure they complete."""
        for thread in self.threads:
            thread.join()

    def reset_enemy_sprite_list(self):
        """Reset the enemies sprite list in the scene."""
        if "Enemies" not in self.scene._name_mapping:
            self.scene.add_sprite_list("Enemies", self.game_view.enemies)
        else:
            self.scene.get_sprite_list("Enemies").clear()
            self.scene.get_sprite_list("Enemies").extend(
                self.game_view.enemies
            )
