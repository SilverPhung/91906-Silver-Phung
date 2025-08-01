"""
Spawn Manager for handling zombie spawn points and spawning logic.

This module provides a centralized system for managing zombie spawn points,
validating spawn locations, and distributing zombies across available spawn points.
"""

import arcade
import random
import time
from typing import List, Tuple, Optional
from src.constants import MAP_WIDTH_PIXEL, MAP_HEIGHT_PIXEL, ENABLE_TESTING
from src.debug import Debug


class SpawnPoint:
    """Represents a single spawn point with validation and usage tracking."""
    
    def __init__(self, x: float, y: float, is_valid: bool = True):
        self.x = x
        self.y = y
        self.is_valid = is_valid
        self.usage_count = 0
        self.last_used = 0.0  # Timestamp for spawn cooldown
    
    def __str__(self):
        return f"SpawnPoint({self.x:.1f}, {self.y:.1f}, valid={self.is_valid}, used={self.usage_count})"


class SpawnManager:
    """
    Manages zombie spawn points and spawning logic.
    
    Responsibilities:
    - Load spawn points from map object layers
    - Validate spawn points against walls and obstacles
    - Distribute zombies across available spawn points
    - Track spawn point usage and cooldowns
    """
    
    def __init__(self, game_view):
        """Initialize the spawn manager with game view reference."""
        self.game_view = game_view
        self.spawn_points: List[SpawnPoint] = []
        self.wall_list = None
        self.min_spawn_distance = 50  # Minimum distance between spawns
        self.spawn_cooldown = 5.0  # Seconds between spawns at same point
        
        if ENABLE_TESTING:
            Debug.track_event("spawn_manager_initialized", {
                'game_view': str(game_view),
                'spawn_points_count': 0
            })
    
    def load_spawn_points_from_map(self, tile_map) -> List[SpawnPoint]:
        """
        Load spawn points from map object layer.
        
        Args:
            tile_map: The loaded tile map containing object layers
            
        Returns:
            List of SpawnPoint objects loaded from the map
        """
        spawn_points = []
        
        try:
            # Look for "Zombie-spawns" object layer in object_lists
            if "Zombie-spawns" in tile_map.object_lists:
                spawn_objects = tile_map.object_lists["Zombie-spawns"]
                print(f"[SPAWN_MANAGER] Found {len(spawn_objects)} spawn points in Zombie-spawns layer")
                
                for spawn_object in spawn_objects:
                    spawn_point = SpawnPoint(
                        x=spawn_object.shape[0],
                        y=spawn_object.shape[1]
                    )
                    spawn_points.append(spawn_point)
                    print(f"[SPAWN_MANAGER] Loaded spawn point at ({spawn_point.x:.1f}, {spawn_point.y:.1f})")
                    
                    if ENABLE_TESTING:
                        Debug.track_event("spawn_point_loaded", {
                            'x': spawn_point.x,
                            'y': spawn_point.y,
                            'is_valid': spawn_point.is_valid
                        })
            else:
                print(f"[SPAWN_MANAGER] No Zombie-spawns layer found in map")
                print(f"[SPAWN_MANAGER] Available object layers: {list(tile_map.object_lists.keys())}")
                
        except Exception as e:
            print(f"[SPAWN_MANAGER] Error loading spawn points: {e}")
            
        return spawn_points
    
    def validate_spawn_point(self, spawn_point: SpawnPoint, wall_list) -> bool:
        """
        Validate a spawn point to ensure it's not inside walls.
        
        Args:
            spawn_point: The spawn point to validate
            wall_list: List of wall sprites to check against
            
        Returns:
            True if spawn point is valid, False otherwise
        """
        if not spawn_point.is_valid:
            return False
            
        try:
            # Create a temporary sprite to check collisions
            temp_sprite = arcade.Sprite()
            temp_sprite.center_x = spawn_point.x
            temp_sprite.center_y = spawn_point.y
            temp_sprite.width = 32  # Approximate zombie size
            temp_sprite.height = 32
            
            # Check collision with walls
            wall_collisions = arcade.check_for_collision_with_list(temp_sprite, wall_list)
            
            is_valid = len(wall_collisions) == 0
            
            if not is_valid:
                pass
                
            return is_valid
            
        except Exception as e:
            return False
    
    def validate_all_spawn_points(self, wall_list) -> List[SpawnPoint]:
        """
        Validate all spawn points against walls.
        
        Args:
            wall_list: List of wall sprites to check against
            
        Returns:
            List of valid spawn points
        """
        valid_spawn_points = []
        
        for spawn_point in self.spawn_points:
            if self.validate_spawn_point(spawn_point, wall_list):
                valid_spawn_points.append(spawn_point)
            else:
                spawn_point.is_valid = False
                

        
        if ENABLE_TESTING:
            Debug.track_event("spawn_points_validated", {
                'total_spawn_points': len(self.spawn_points),
                'valid_spawn_points': len(valid_spawn_points),
                'invalid_spawn_points': len(self.spawn_points) - len(valid_spawn_points)
            })
            
        return valid_spawn_points
    
    def select_spawn_points(self, zombie_count: int, current_time: float) -> List[Tuple[float, float]]:
        """
        Select spawn points for zombies with distribution logic.
        
        Args:
            zombie_count: Number of zombies to spawn
            current_time: Current game time for cooldown tracking
            
        Returns:
            List of (x, y) coordinates for zombie spawning
        """
        valid_spawn_points = [sp for sp in self.spawn_points if sp.is_valid]
        
        if not valid_spawn_points:
            return self._generate_random_positions(zombie_count)
        
        # Filter spawn points by cooldown
        available_spawn_points = [
            sp for sp in valid_spawn_points 
            if current_time - sp.last_used >= self.spawn_cooldown
        ]
        
        if len(available_spawn_points) < zombie_count:
            available_spawn_points = valid_spawn_points
        
        # Select spawn points with weighted distribution (prefer less used points)
        selected_positions = []
        
        for _ in range(min(zombie_count, len(available_spawn_points))):
            # Weight by inverse usage count (less used = higher weight)
            weights = [1.0 / (sp.usage_count + 1) for sp in available_spawn_points]
            total_weight = sum(weights)
            
            if total_weight > 0:
                # Normalize weights
                normalized_weights = [w / total_weight for w in weights]
                
                # Select spawn point based on weights
                selected_spawn = random.choices(available_spawn_points, weights=normalized_weights)[0]
            else:
                # Fallback to random selection
                selected_spawn = random.choice(available_spawn_points)
            
            # Add some randomization around the spawn point
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            
            position = (selected_spawn.x + offset_x, selected_spawn.y + offset_y)
            selected_positions.append(position)
            
            # Update spawn point usage
            selected_spawn.usage_count += 1
            selected_spawn.last_used = current_time
            
            # Remove from available list to avoid duplicates
            available_spawn_points.remove(selected_spawn)
        
        if ENABLE_TESTING:
            Debug.track_event("spawn_points_selected", {
                'zombie_count': zombie_count,
                'selected_positions': len(selected_positions),
                'valid_spawn_points': len(valid_spawn_points),
                'available_spawn_points': len(available_spawn_points)
            })
        
        return selected_positions
    
    def _generate_random_positions(self, zombie_count: int) -> List[Tuple[float, float]]:
        """
        Generate random positions as fallback when no spawn points are available.
        
        Args:
            zombie_count: Number of random positions to generate
            
        Returns:
            List of (x, y) coordinates
        """
        positions = []
        for _ in range(zombie_count):
            x = random.randint(50, MAP_WIDTH_PIXEL - 50)
            y = random.randint(50, MAP_HEIGHT_PIXEL - 50)
            positions.append((x, y))
        
        return positions
    
    def setup_for_map(self, tile_map, wall_list) -> None:
        """
        Set up spawn manager for a new map.
        
        Args:
            tile_map: The loaded tile map
            wall_list: List of wall sprites for validation
        """

        
        # Load spawn points from map
        self.spawn_points = self.load_spawn_points_from_map(tile_map)
        self.wall_list = wall_list
        
        # Validate spawn points
        valid_spawn_points = self.validate_all_spawn_points(wall_list)
        

        
        if ENABLE_TESTING:
            Debug.track_event("spawn_manager_setup", {
                'total_spawn_points': len(self.spawn_points),
                'valid_spawn_points': len(valid_spawn_points),
                'wall_list_count': len(wall_list) if wall_list else 0
            })
    
    def get_spawn_positions(self, zombie_count: int, current_time: float) -> List[Tuple[float, float]]:
        """
        Get spawn positions for zombies.
        
        Args:
            zombie_count: Number of zombies to spawn
            current_time: Current game time
            
        Returns:
            List of (x, y) coordinates for zombie spawning
        """
        return self.select_spawn_points(zombie_count, current_time)
    
    def clear_zombies(self):
        """Clear all zombies completely."""
        zombie_count = len(self.game_view.enemies)
        print(f"[SPAWN_MANAGER] Clearing {zombie_count} zombies")
        
        for zombie in self.game_view.enemies:
            zombie.cleanup()
        self.game_view.enemies.clear()
        
    def spawn_zombies_for_map(self, count: int):
        """Spawn new zombies for current map."""
        print(f"[SPAWN_MANAGER] Spawning {count} zombies for map")
        
        # Always spawn fresh zombies for new map
        spawn_positions = self.get_spawn_positions(count, time.time())
        for x, y in spawn_positions:
            self.create_zombie(x, y)
            
    def create_zombie(self, x: float, y: float):
        """
        Create a zombie at the specified position.
        
        Args:
            x: X coordinate for zombie spawn
            y: Y coordinate for zombie spawn
            
        Returns:
            Zombie: The created zombie instance
        """
        from src.entities.zombie import Zombie
        from src.constants import CHARACTER_SCALING, ZOMBIE_MOVEMENT_SPEED
        
        zombie = Zombie(
            game_view=self.game_view,
            scale=CHARACTER_SCALING,
            speed=ZOMBIE_MOVEMENT_SPEED,
            player_ref=self.game_view.player
        )
        zombie.spawn_at_position(x, y)
        print(f"[SPAWN_MANAGER] Added zombie to scene at ({zombie.center_x:.1f}, {zombie.center_y:.1f})")
        
        if ENABLE_TESTING:
            Debug.track_event("enemy_spawned_at_position", {
                'x': int(x),
                'y': int(y),
                'enemy_type': 'Army_zombie'
            })
        
        return zombie
    
    def get_spawn_stats(self) -> dict:
        """
        Get statistics about spawn points.
        
        Returns:
            Dictionary with spawn statistics
        """
        valid_spawn_points = [sp for sp in self.spawn_points if sp.is_valid]
        total_usage = sum(sp.usage_count for sp in self.spawn_points)
        
        return {
            'total_spawn_points': len(self.spawn_points),
            'valid_spawn_points': len(valid_spawn_points),
            'total_usage': total_usage,
            'average_usage': total_usage / len(self.spawn_points) if self.spawn_points else 0
        } 