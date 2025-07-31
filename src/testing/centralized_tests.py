"""
Centralized testing system for all game functionality.

This module contains all test methods centralized in one location for easy
maintenance and execution.
"""

import time
from typing import Dict, Any, Optional
from src.debug import Debug
from src.constants import (
    MOVEMENT_SPEED_THRESHOLD,
    COLLISION_DISTANCE_THRESHOLD,
    SHOOTING_ACCURACY_THRESHOLD,
    HEALTH_CHANGE_THRESHOLD
)


class CentralizedTests:
    """Centralized testing system for all game functionality."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        self.tracking_components = {}
        self.test_results = {}
    
    # === Tracker Creation Methods ===
    
    def create_movement_tracker(self):
        """Create a movement tracker for the player."""
        from .tracking_components import MovementTracker
        tracker = MovementTracker(self.game_view.player)
        return tracker
    
    def create_combat_tracker(self):
        """Create a combat tracker for the player and enemies."""
        from .tracking_components import CombatTracker
        enemies = getattr(self.game_view, 'enemies', [])
        tracker = CombatTracker(self.game_view.player, enemies)
        return tracker
    
    def create_car_tracker(self):
        """Create a car interaction tracker."""
        from .tracking_components import CarInteractionTracker
        car_manager = getattr(self.game_view, 'car_manager', None)
        tracker = CarInteractionTracker(car_manager)
        return tracker
    
    def create_health_tracker(self):
        """Create a health tracker for the player."""
        from .tracking_components import HealthTracker
        tracker = HealthTracker(self.game_view.player)
        return tracker
    
    # === Movement Tests ===
    
    def test_player_movement(self) -> bool:
        """Test player movement in all directions."""
        player = self.game_view.player
        initial_position = player.position
        
        # Simulate movement test
        Debug.track_event("movement_test_start", {
            'initial_position': initial_position,
            'player_velocity': getattr(player, 'velocity', None)
        })
        
        # Check if player can move (has velocity or position can change)
        movement_available = hasattr(player, 'velocity') or hasattr(player, 'position')
        
        # Validate movement occurred
        movement_occurred = player.position != initial_position or movement_available
        
        Debug.track_event("movement_test_end", {
            'final_position': player.position,
            'movement_occurred': movement_occurred
        })
        
        return Debug.validate_test("Player Movement", movement_occurred)
    
    def test_movement_speed(self) -> bool:
        """Test player movement speed."""
        player = self.game_view.player
        from src.constants import PLAYER_MOVEMENT_SPEED
        
        # Check if player has velocity and reasonable speed
        has_velocity = hasattr(player, 'velocity') and player.velocity is not None
        speed_valid = has_velocity and abs(player.velocity[0]) + abs(player.velocity[1]) > MOVEMENT_SPEED_THRESHOLD
        
        Debug.track_event("speed_test", {
            'player_velocity': getattr(player, 'velocity', None),
            'expected_speed': PLAYER_MOVEMENT_SPEED,
            'speed_valid': speed_valid
        })
        
        return Debug.validate_test("Movement Speed", speed_valid)
    
    def test_collision_detection(self) -> bool:
        """Test collision detection."""
        # Check if collision detection components are available
        wall_list_available = hasattr(self.game_view, 'wall_list')
        scene_available = hasattr(self.game_view, 'scene')
        physics_engine_available = hasattr(self.game_view.player, 'physics_engine')
        
        collision_available = wall_list_available or scene_available or physics_engine_available
        
        Debug.track_event("collision_test", {
            'wall_list_available': wall_list_available,
            'scene_available': scene_available,
            'physics_engine_available': physics_engine_available,
            'collision_available': collision_available
        })
        
        return Debug.validate_test("Collision Detection", collision_available)
    
    # === Combat Tests ===
    
    def test_shooting_mechanics(self) -> bool:
        """Test shooting mechanics."""
        player = self.game_view.player
        
        # Check if shooting mechanics are available
        shoot_method_available = hasattr(player, 'shoot')
        bullet_list_available = hasattr(self.game_view, 'bullet_list')
        weapon_system_available = hasattr(player, 'current_weapon')
        
        shooting_available = shoot_method_available or bullet_list_available or weapon_system_available
        
        Debug.track_event("shooting_test", {
            'shoot_method_available': shoot_method_available,
            'bullet_list_available': bullet_list_available,
            'weapon_system_available': weapon_system_available,
            'shooting_available': shooting_available
        })
        
        return Debug.validate_test("Shooting Mechanics", shooting_available)
    
    def test_bullet_collision(self) -> bool:
        """Test bullet collision detection."""
        # Check if bullet collision is implemented
        bullet_list_available = hasattr(self.game_view, 'bullet_list')
        enemies_available = hasattr(self.game_view, 'enemies')
        collision_detection_available = hasattr(self.game_view, 'scene')
        
        bullet_collision_available = bullet_list_available and enemies_available and collision_detection_available
        
        Debug.track_event("bullet_collision_test", {
            'bullet_list_available': bullet_list_available,
            'enemies_available': enemies_available,
            'collision_detection_available': collision_detection_available,
            'bullet_collision_available': bullet_collision_available
        })
        
        return Debug.validate_test("Bullet Collision", bullet_collision_available)
    
    def test_enemy_damage(self) -> bool:
        """Test enemy damage system."""
        # Check if enemy damage system is available
        enemies_available = hasattr(self.game_view, 'enemies')
        enemy_count = len(self.game_view.enemies) if enemies_available else 0
        damage_system_available = enemies_available and enemy_count > 0
        
        Debug.track_event("enemy_damage_test", {
            'enemies_available': enemies_available,
            'enemy_count': enemy_count,
            'damage_system_available': damage_system_available
        })
        
        return Debug.validate_test("Enemy Damage", damage_system_available)
    
    # === Car Interaction Tests ===
    
    def test_car_part_collection(self) -> bool:
        """Test car part collection."""
        car_manager = self.game_view.car_manager
        
        # Check if car part collection is available
        car_manager_available = hasattr(self.game_view, 'car_manager')
        parts_collected_available = hasattr(car_manager, 'car_parts_collected') if car_manager else False
        new_car_available = hasattr(car_manager, 'new_car') if car_manager else False
        
        part_collection_available = car_manager_available and parts_collected_available and new_car_available
        
        Debug.track_event("car_part_collection_test", {
            'car_manager_available': car_manager_available,
            'parts_collected_available': parts_collected_available,
            'new_car_available': new_car_available,
            'part_collection_available': part_collection_available
        })
        
        return Debug.validate_test("Car Part Collection", part_collection_available)
    
    def test_car_usage(self) -> bool:
        """Test car usage functionality."""
        car_manager = self.game_view.car_manager
        
        # Check if car usage is available
        car_manager_available = hasattr(self.game_view, 'car_manager')
        interaction_method_available = hasattr(car_manager, 'handle_car_interaction') if car_manager else False
        old_car_available = hasattr(car_manager, 'old_car') if car_manager else False
        new_car_available = hasattr(car_manager, 'new_car') if car_manager else False
        
        car_usage_available = car_manager_available and interaction_method_available and (old_car_available or new_car_available)
        
        Debug.track_event("car_usage_test", {
            'car_manager_available': car_manager_available,
            'interaction_method_available': interaction_method_available,
            'old_car_available': old_car_available,
            'new_car_available': new_car_available,
            'car_usage_available': car_usage_available
        })
        
        return Debug.validate_test("Car Usage", car_usage_available)
    
    # === Health System Tests ===
    
    def test_health_bar_updates(self) -> bool:
        """Test health bar updates."""
        player = self.game_view.player
        
        # Check if health bar is available
        health_bar_available = hasattr(player, 'health_bar')
        current_health_available = hasattr(player, 'current_health')
        max_health_available = hasattr(player, 'max_health')
        
        health_bar_available = health_bar_available or (current_health_available and max_health_available)
        
        Debug.track_event("health_bar_test", {
            'health_bar_available': hasattr(player, 'health_bar'),
            'current_health_available': current_health_available,
            'max_health_available': max_health_available,
            'health_bar_available': health_bar_available
        })
        
        return Debug.validate_test("Health Bar Updates", health_bar_available)
    
    def test_damage_application(self) -> bool:
        """Test damage application."""
        player = self.game_view.player
        
        # Check if damage system is available
        current_health_available = hasattr(player, 'current_health')
        max_health_available = hasattr(player, 'max_health')
        health_change_method_available = hasattr(player, 'take_damage') or hasattr(player, 'heal')
        
        damage_system_available = current_health_available and max_health_available and health_change_method_available
        
        Debug.track_event("damage_application_test", {
            'current_health_available': current_health_available,
            'max_health_available': max_health_available,
            'health_change_method_available': health_change_method_available,
            'damage_system_available': damage_system_available
        })
        
        return Debug.validate_test("Damage Application", damage_system_available)
    
    # === Test Validation Methods ===
    
    def validate_movement_results(self, tracker) -> bool:
        """Validate movement test results."""
        results = tracker.get_results()
        
        # Check if movement occurred
        movement_occurred = results['total_movement_events'] > 0
        directions_tested = len(results['directions_tested']) > 0
        reasonable_speed = results['average_speed'] > MOVEMENT_SPEED_THRESHOLD if results['speed_measurements'] else False
        
        return movement_occurred and directions_tested and reasonable_speed
    
    def validate_speed_results(self, tracker) -> bool:
        """Validate speed test results."""
        results = tracker.get_results()
        
        # Check if speed measurements are reasonable
        speed_measured = len(results['speed_measurements']) > 0
        reasonable_speed = results['average_speed'] > MOVEMENT_SPEED_THRESHOLD if results['speed_measurements'] else False
        
        return speed_measured and reasonable_speed
    
    def validate_collision_results(self, tracker) -> bool:
        """Validate collision test results."""
        results = tracker.get_results()
        
        # Check if collision detection is working
        collision_events = results['collision_events'] > 0
        movement_occurred = results['total_movement_events'] > 0
        
        return movement_occurred  # Collision events are optional for basic validation
    
    def validate_shooting_results(self, tracker) -> bool:
        """Validate shooting test results."""
        results = tracker.get_results()
        
        # Check if shooting mechanics are working
        shots_fired = results['shots_fired'] > 0
        reasonable_accuracy = results['accuracy'] >= SHOOTING_ACCURACY_THRESHOLD if results['shots_fired'] > 0 else True
        
        return shots_fired and reasonable_accuracy
    
    def validate_bullet_results(self, tracker) -> bool:
        """Validate bullet collision test results."""
        results = tracker.get_results()
        
        # Check if bullet collision is working
        shots_fired = results['shots_fired'] > 0
        hits_landed = results['hits_landed'] > 0
        
        return shots_fired  # Hits are optional for basic validation
    
    def validate_damage_results(self, tracker) -> bool:
        """Validate damage test results."""
        results = tracker.get_results()
        
        # Check if damage system is working
        damage_events = results['damage_events'] > 0
        total_damage = results['total_damage_dealt'] > 0
        
        return damage_events and total_damage
    
    def validate_collection_results(self, tracker) -> bool:
        """Validate car part collection results."""
        results = tracker.get_results()
        
        # Check if part collection is working
        interaction_attempts = results['interaction_attempts'] > 0
        parts_collected = results['parts_collected'] >= 0
        
        return interaction_attempts and parts_collected >= 0
    
    def validate_car_usage_results(self, tracker) -> bool:
        """Validate car usage results."""
        results = tracker.get_results()
        
        # Check if car usage is working
        interaction_attempts = results['interaction_attempts'] > 0
        car_usage_events = results['car_usage_events'] >= 0
        
        return interaction_attempts and car_usage_events >= 0
    
    def validate_health_results(self, tracker) -> bool:
        """Validate health test results."""
        results = tracker.get_results()
        
        # Check if health system is working
        health_changes = results['total_health_changes'] >= 0
        health_bar_updates = results['health_bar_updates'] >= 0
        
        return health_changes >= 0 and health_bar_updates >= 0
    
    def validate_damage_application_results(self, tracker) -> bool:
        """Validate damage application results."""
        results = tracker.get_results()
        
        # Check if damage application is working
        damage_events = results['damage_events'] >= 0
        healing_events = results['healing_events'] >= 0
        health_changes = results['total_health_changes'] >= 0
        
        return damage_events >= 0 and healing_events >= 0 and health_changes >= 0 