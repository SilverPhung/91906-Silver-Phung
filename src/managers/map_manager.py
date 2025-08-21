"""
Map Manager for handling map loading, scene creation, and map transitions.

This module provides a centralized system for managing map-related operations
including tile map loading, scene setup, camera bounds calculation, and map transitions.
"""

import arcade
import os
from typing import Optional, Tuple
from src.constants import (
    TILE_SCALING,
    MAP_WIDTH_PIXEL,
    MAP_HEIGHT_PIXEL,
    ENABLE_TESTING,
)
from src.debug import Debug


class MapManager:
    """Manages map loading, scene creation, and map transitions."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.current_map_index = 1
        self.tile_map = None
        self.wall_list = None
        self.scene = None

    def load_map(self, map_index: int) -> bool:
        """
        Load a specific map by index.

        Args:
            map_index: The index of the map to load

        Returns:
            bool: True if map loaded successfully, False otherwise
        """
        print(
            f"[MAP_MANAGER] ===== LOAD_MAP CALLED with " f"map_index: {map_index} ====="
        )
        map_name = f"resources/maps/map{map_index}.tmx"
        print(f"[MAP_MANAGER] Map file: {map_name}")

        # Check if map file exists
        if not os.path.exists(map_name):
            print(f"[MAP_MANAGER] ERROR: Map file {map_name} does not exist!")
            available_maps = [
                f for f in os.listdir("resources/maps") if f.endswith(".tmx")
            ]
            print(f"[MAP_MANAGER] Available maps: {available_maps}")

            # Fallback to map1 if map doesn't exist
            map_index = 1
            map_name = f"resources/maps/map{map_index}.tmx"
            print(f"[MAP_MANAGER] Falling back to {map_name}")

        try:
            # Load new tile map
            self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
            print(f"[MAP_MANAGER] Tilemap loaded successfully")
            self.current_map_index = map_index
            return True
        except Exception as e:
            print(f"[MAP_MANAGER] ERROR loading tilemap: {e}")
            # Fallback to map1
            map_index = 1
            map_name = f"resources/maps/map{map_index}.tmx"
            print(f"[MAP_MANAGER] Falling back to {map_name}")
            try:
                self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
                print(f"[MAP_MANAGER] Fallback tilemap loaded successfully")
                self.current_map_index = map_index
                return True
            except Exception as fallback_error:
                print(
                    f"[MAP_MANAGER] CRITICAL ERROR: Could not load "
                    f"fallback map: {fallback_error}"
                )
                return False

    def create_scene(self) -> arcade.Scene:
        """
        Create a new scene with the current tile map.

        Returns:
            arcade.Scene: The created scene
        """
        print(
            f"[MAP_MANAGER] Creating scene for map: "
            f"resources/maps/map{self.current_map_index}.tmx"
        )

        # COMPLETELY DELETE AND RECREATE SCENE
        print(f"[MAP_MANAGER] Completely deleting existing scene...")
        self.scene = None  # Force garbage collection of old scene

        # Create new scene
        self.scene = arcade.Scene()
        print(f"[MAP_MANAGER] New scene created from scratch")

        # Add the ground layers to the scene (in drawing order from bottom to top)
        print(f"[MAP_MANAGER] Adding ground layers to scene...")
        for layer_name in ("Dirt", "Grass", "Road"):
            sprite_list = self.tile_map.sprite_lists[layer_name]
            self.scene.add_sprite_list(layer_name, sprite_list=sprite_list)
        print(f"[MAP_MANAGER] Ground layers added")

        # Add the walls layer
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        self.scene.add_sprite_list("Walls", sprite_list=self.wall_list)
        print(f"[MAP_MANAGER] Walls layer added with " f"{len(self.wall_list)} sprites")

        # Add sprite lists for entities (drawn on top)
        print("[MAP_MANAGER] Adding entity sprite layers to scene")
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("CarsLayer")
        self.scene.add_sprite_list("ChestsLayer")
        self.scene.add_sprite_list("Enemies")
        print("[MAP_MANAGER] Entity sprite layers added successfully")

        # Debug: Verify layer order is correct (entities should be on top)
        print(f"[MAP_MANAGER] Layer order verification:")
        layer_names = list(self.scene._name_mapping.keys())
        for i, layer_name in enumerate(layer_names):
            print(f"[MAP_MANAGER]   Layer {i}: {layer_name}")

        # Verify entities are at the end (on top)
        entity_layers = ["Player", "CarsLayer", "ChestsLayer", "Enemies"]
        for entity_layer in entity_layers:
            if entity_layer in layer_names:
                layer_index = layer_names.index(entity_layer)
                print(
                    f"[MAP_MANAGER]   {entity_layer} is at layer "
                    f"{layer_index} (should be near end)"
                )

        # Debug: Log the final drawing order
        print(f"[MAP_MANAGER] Final scene drawing order:")
        for i, layer_name in enumerate(self.scene._name_mapping.keys()):
            print(f"[MAP_MANAGER]   {i + 1}. {layer_name}")

        # Log scene sprite counts
        print(f"[MAP_MANAGER] Scene sprite counts:")
        for layer_name in self.scene._name_mapping.keys():
            sprite_list = self.scene._name_mapping[layer_name]
            print(f"[MAP_MANAGER]   {layer_name}: {len(sprite_list)} sprites")

        # Debug: Log entity addition tracking
        print(f"[MAP_MANAGER] Entity layers ready for sprites")

        return self.scene

    def setup_camera_bounds(self) -> None:
        """Set up camera bounds based on the current tile map."""
        if self.tile_map:
            self.game_view.camera_manager.setup_camera_bounds(self.tile_map)
            print(f"[MAP_MANAGER] Camera bounds set up")

    def create_pathfinding_barrier(self) -> None:
        """Create or regenerate the pathfinding barrier for AI navigation."""

        def create_pathfind_barrier():
            with self.game_view.pathfind_barrier_thread_lock:
                # Always recreate the barrier for new maps
                self.game_view.pathfind_barrier = arcade.AStarBarrierList(
                    moving_sprite=self.game_view.player,
                    blocking_sprites=self.wall_list,
                    grid_size=30,
                    left=0,
                    right=MAP_WIDTH_PIXEL,
                    bottom=0,
                    top=MAP_HEIGHT_PIXEL,
                )
                print(
                    f"[MAP_MANAGER] Pathfinding barrier created with "
                    f"{len(self.wall_list)} blocking sprites"
                )

        self.game_view._start_thread(create_pathfind_barrier)
        print(f"[MAP_MANAGER] Pathfinding barrier thread started")

    def transition_to_next_map(self) -> Optional[str]:
        """
        Transition to the next map.

        Returns:
            Optional[str]: The name of the view to transition to, or None if continuing with current view
        """
        self.current_map_index += 1
        print(f"[MAP_MANAGER] Transitioning to map " f"{self.current_map_index}")

        if self.current_map_index > 3:
            print("[MAP_MANAGER] All maps completed, transitioning to end view")
            return "EndView"

        # Show transition screen
        print(
            f"[MAP_MANAGER] Showing transition screen to map "
            f"{self.current_map_index}"
        )
        return "TransitionView"

    def get_map_info(self) -> Tuple[int, str]:
        """
        Get current map information.

        Returns:
            Tuple[int, str]: (map_index, map_name)
        """
        map_name = f"resources/maps/map{self.current_map_index}.tmx"
        return self.current_map_index, map_name

    def get_wall_list(self) -> arcade.SpriteList:
        """Get the wall list for collision detection."""
        return self.wall_list

    def get_tile_map(self) -> arcade.TileMap:
        """Get the current tile map."""
        return self.tile_map

    def get_scene(self) -> arcade.Scene:
        """Get the current scene."""
        return self.scene

    def clear_health_bars(self) -> None:
        """Clear health bars from the previous map."""
        bar_count = len(self.game_view.bar_list)
        print(f"[MAP_MANAGER] Clearing {bar_count} health bars")
        self.game_view.bar_list.clear()

    def reset_entities(self) -> None:
        """Reset entities for the new map."""
        # Clear enemies from previous map
        for enemy in self.game_view.enemies:
            enemy.cleanup()
        self.game_view.enemies.clear()

        # Clear bullets from previous map
        self.game_view.bullet_list.clear()

        # Re-add player to the new scene
        player_list = self.scene.get_sprite_list("Player")
        if not player_list or self.game_view.player not in player_list:
            self.scene.add_sprite("Player", self.game_view.player)

    def setup_managers_for_map(self) -> None:
        """Set up all managers for the new map."""
        # Set up spawn manager for new map
        self.game_view.spawn_manager.setup_for_map(self.tile_map, self.wall_list)

        # Use new car manager methods for better asset optimization
        self.game_view.car_manager.clear_cars()
        self.game_view.car_manager.load_cars_from_map()

        # Use new chest manager methods for better asset optimization
        self.game_view.chest_manager.clear_chests()
        self.game_view.chest_manager.load_chests_from_map()

        # Position player at old car
        with self.game_view.pathfind_barrier_thread_lock:
            self.game_view.car_manager.position_player_at_old_car()

    def spawn_enemies_for_map(self, zombie_count: int = 10) -> None:
        """
        Spawn enemies for the new map.

        Args:
            zombie_count: Number of zombies to spawn
        """
        # Use new spawn manager methods for better asset optimization
        self.game_view.spawn_manager.clear_zombies()
        self.game_view.spawn_manager.spawn_zombies_for_map(zombie_count)

    def reset_game_state_for_map(self) -> None:
        """Reset game state for the new map."""
        # Reset car parts for new level
        self.game_view.car_manager.reset_car_parts()

        # Reset input keys for new map
        self.game_view.input_manager.reset_keys()

        # Reset UI elements for new map
        print(f"[MAP_MANAGER] Resetting UI elements...")
        self.game_view.ui_manager.reset_ui()

    def load_complete_map(self, map_index: int) -> bool:
        """
        Load a complete map with all setup and entity spawning.

        Args:
            map_index: The index of the map to load

        Returns:
            bool: True if map loaded successfully, False otherwise
        """
        print(f"[MAP_MANAGER] ===== LOADING COMPLETE MAP {map_index} =====")

        # Load the map
        if not self.load_map(map_index):
            return False

        # Clear health bars from previous map
        self.clear_health_bars()

        # Create new scene
        self.create_scene()

        # Set up camera bounds
        self.setup_camera_bounds()

        # Create pathfinding barrier
        self.create_pathfinding_barrier()

        # Set up managers for new map
        self.setup_managers_for_map()

        # Spawn enemies
        self.spawn_enemies_for_map()

        # Add player to scene (if not already added)
        player_list = self.scene.get_sprite_list("Player")
        if not player_list or self.game_view.player not in player_list:
            self.scene.add_sprite("Player", self.game_view.player)
            player_x = self.game_view.player.center_x
            player_y = self.game_view.player.center_y
            print(
                f"[MAP_MANAGER] Player added to scene at "
                f"({player_x:.1f}, {player_y:.1f})"
            )

        # Don't call GameView reset here - entities are already loaded properly
        # The reset was clearing entities that were just loaded
        print("[MAP_MANAGER] Skipping GameView reset to preserve loaded entities")

        print(f"[MAP_MANAGER] Map {map_index} loaded successfully")

        # Final scene sprite counts
        print(f"[MAP_MANAGER] Final scene sprite counts:")
        for layer_name in self.scene._name_mapping.keys():
            sprite_list = self.scene._name_mapping[layer_name]
            print(f"[MAP_MANAGER]   {layer_name}: {len(sprite_list)} sprites")

        # Debug: Check specific entity counts
        player_list = self.scene.get_sprite_list("Player")
        car_list = self.scene.get_sprite_list("CarsLayer")
        chest_list = self.scene.get_sprite_list("ChestsLayer")
        enemy_list = self.scene.get_sprite_list("Enemies")

        player_count = len(player_list) if player_list else 0
        car_count = len(car_list) if car_list else 0
        chest_count = len(chest_list) if chest_list else 0
        enemy_count = len(enemy_list) if enemy_list else 0
        print(
            f"[MAP_MANAGER] Entity counts - Player: {player_count}, "
            f"Cars: {car_count}, Chests: {chest_count}, "
            f"Enemies: {enemy_count}"
        )

        # Debug: Check if entities are actually in the scene
        if car_list:
            car_positions = [
                f"({car.center_x:.1f}, {car.center_y:.1f})" for car in car_list
            ]
            print(f"[MAP_MANAGER] Cars in scene: {car_positions}")
        if enemy_list:
            enemy_positions = [
                f"({enemy.center_x:.1f}, {enemy.center_y:.1f})" for enemy in enemy_list
            ]
            print(f"[MAP_MANAGER] Enemies in scene: {enemy_positions}")

        # Debug: Check if entities are in the game view lists
        print(f"[MAP_MANAGER] Game view enemies: {len(self.game_view.enemies)}")
        if hasattr(self.game_view.car_manager, "get_all_cars"):
            car_manager_count = len(self.game_view.car_manager.get_all_cars())
        else:
            car_manager_count = "N/A"
        print(f"[MAP_MANAGER] Game view cars: {car_manager_count}")

        if ENABLE_TESTING:
            Debug.track_event(
                "map_loaded",
                {
                    "map_index": map_index,
                    "wall_count": len(self.wall_list),
                    "scene_layers": len(self.scene._name_mapping),
                    "enemy_count": len(self.game_view.enemies),
                },
            )

        return True
