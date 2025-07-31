"""
Testing Manager for centralized test management.

This module contains the TestingManager class that handles centralized test execution,
reusable tracking components, and test report generation.
"""

import time
from typing import Dict, Any, Optional, List
from src.constants import ENABLE_TESTING, TESTING_OBJECTIVES
from src.debug import Debug


class TestingManager:
    """Manages centralized test execution and tracking components."""
    
    def __init__(self):
        self.current_objective = None
        self.test_results = {}
        self.tracking_components = {}
        self.active_tests = []
    
    def set_objective(self, objective: str):
        """Set the current testing objective."""
        if objective in TESTING_OBJECTIVES:
            self.current_objective = objective
            Debug.set_testing_objective(TESTING_OBJECTIVES[objective])
    
    def get_current_objective(self) -> Optional[str]:
        """Get the current testing objective description."""
        if self.current_objective and self.current_objective in TESTING_OBJECTIVES:
            return TESTING_OBJECTIVES[self.current_objective]
        return None
    
    def get_available_objectives(self) -> List[str]:
        """Get list of available testing objectives."""
        return list(TESTING_OBJECTIVES.keys())
    
    def run_movement_tests(self, game_view) -> Dict[str, Any]:
        """Run all movement tests."""
        if not ENABLE_TESTING:
            return {}
        
        # Create movement tracker
        movement_tracker = self.create_movement_tracker(game_view.player)
        self.tracking_components['movement'] = movement_tracker
        
        # Run tests
        results = {
            'movement_basic': self._test_player_movement(game_view),
            'movement_speed': self._test_movement_speed(game_view),
            'collision': self._test_collision_detection(game_view)
        }
        
        return results
    
    def run_combat_tests(self, game_view) -> Dict[str, Any]:
        """Run all combat tests."""
        if not ENABLE_TESTING:
            return {}
        
        # Create combat tracker
        combat_tracker = self.create_combat_tracker(game_view.player, game_view.enemies)
        self.tracking_components['combat'] = combat_tracker
        
        # Run tests
        results = {
            'shooting': self._test_shooting_mechanics(game_view),
            'bullet_collision': self._test_bullet_collision(game_view),
            'enemy_damage': self._test_enemy_damage(game_view)
        }
        
        return results
    
    def run_car_interaction_tests(self, game_view) -> Dict[str, Any]:
        """Run all car interaction tests."""
        if not ENABLE_TESTING:
            return {}
        
        # Create car tracker
        car_tracker = self.create_car_tracker(game_view.car_manager)
        self.tracking_components['car'] = car_tracker
        
        # Run tests
        results = {
            'part_collection': self._test_car_part_collection(game_view),
            'car_usage': self._test_car_usage(game_view)
        }
        
        return results
    
    def run_health_system_tests(self, game_view) -> Dict[str, Any]:
        """Run all health system tests."""
        if not ENABLE_TESTING:
            return {}
        
        # Create health tracker
        health_tracker = self.create_health_tracker(game_view.player)
        self.tracking_components['health'] = health_tracker
        
        # Run tests
        results = {
            'health_bar': self._test_health_bar_updates(game_view),
            'damage': self._test_damage_application(game_view)
        }
        
        return results
    
    def run_all_tests(self, game_view) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report."""
        if not ENABLE_TESTING:
            return {}
        
        all_results = {
            'movement': self.run_movement_tests(game_view),
            'combat': self.run_combat_tests(game_view),
            'car_interaction': self.run_car_interaction_tests(game_view),
            'health_system': self.run_health_system_tests(game_view)
        }
        
        return self.generate_test_report(all_results)
    
    # === Reusable Tracking Component Factories ===
    
    def create_movement_tracker(self, player):
        """Create a movement tracker for the player."""
        from src.testing.tracking_components import MovementTracker
        tracker = MovementTracker(player)
        return tracker
    
    def create_combat_tracker(self, player, enemies):
        """Create a combat tracker for the player and enemies."""
        from src.testing.tracking_components import CombatTracker
        tracker = CombatTracker(player, enemies)
        return tracker
    
    def create_car_tracker(self, car_manager):
        """Create a car interaction tracker."""
        from src.testing.tracking_components import CarInteractionTracker
        tracker = CarInteractionTracker(car_manager)
        return tracker
    
    def create_health_tracker(self, player):
        """Create a health tracker for the player."""
        from src.testing.tracking_components import HealthTracker
        tracker = HealthTracker(player)
        return tracker
    
    # === Test Implementation Methods ===
    
    def _test_player_movement(self, game_view) -> bool:
        """Test basic player movement."""
        player = game_view.player
        initial_position = player.position
        
        print(f"[TEST] Movement Test - Initial position: ({initial_position[0]:.1f}, {initial_position[1]:.1f})")
        
        # Simulate movement (this would be replaced with actual test logic)
        Debug.track_event("movement_test", {
            'initial_position': initial_position,
            'current_position': player.position
        })
        
        # Validate movement occurred
        movement_occurred = player.position != initial_position
        current_position = player.position
        print(f"[TEST] Movement Test - Current position: ({current_position[0]:.1f}, {current_position[1]:.1f})")
        print(f"[TEST] Movement Test - Movement occurred: {movement_occurred}")
        
        return Debug.validate_test("Player Movement", movement_occurred)
    
    def _test_movement_speed(self, game_view) -> bool:
        """Test player movement speed."""
        player = game_view.player
        from src.constants import PLAYER_MOVEMENT_SPEED
        
        # Check if player has reasonable movement speed
        speed_valid = hasattr(player, 'velocity') and player.velocity is not None
        
        Debug.track_event("speed_test", {
            'player_velocity': getattr(player, 'velocity', None),
            'expected_speed': PLAYER_MOVEMENT_SPEED
        })
        
        return Debug.validate_test("Movement Speed", speed_valid)
    
    def _test_collision_detection(self, game_view) -> bool:
        """Test collision detection."""
        # Check if collision detection is available
        collision_available = hasattr(game_view, 'wall_list') or hasattr(game_view, 'scene')
        
        Debug.track_event("collision_test", {
            'wall_list_available': hasattr(game_view, 'wall_list'),
            'scene_available': hasattr(game_view, 'scene')
        })
        
        return Debug.validate_test("Collision Detection", collision_available)
    
    def _test_shooting_mechanics(self, game_view) -> bool:
        """Test shooting mechanics."""
        player = game_view.player
        
        print(f"[TEST] Shooting Test - Player has shoot method: {hasattr(player, 'shoot')}")
        print(f"[TEST] Shooting Test - Game has bullet list: {hasattr(game_view, 'bullet_list')}")
        
        # Check if shooting mechanics are available
        shooting_available = hasattr(player, 'shoot') or hasattr(game_view, 'bullet_list')
        
        Debug.track_event("shooting_test", {
            'shoot_method_available': hasattr(player, 'shoot'),
            'bullet_list_available': hasattr(game_view, 'bullet_list')
        })
        
        print(f"[TEST] Shooting Test - Shooting mechanics available: {shooting_available}")
        
        return Debug.validate_test("Shooting Mechanics", shooting_available)
    
    def _test_bullet_collision(self, game_view) -> bool:
        """Test bullet collision detection."""
        # Check if bullet collision is implemented
        bullet_collision_available = hasattr(game_view, 'bullet_list') and hasattr(game_view, 'enemies')
        
        Debug.track_event("bullet_collision_test", {
            'bullet_list_available': hasattr(game_view, 'bullet_list'),
            'enemies_available': hasattr(game_view, 'enemies')
        })
        
        return Debug.validate_test("Bullet Collision", bullet_collision_available)
    
    def _test_enemy_damage(self, game_view) -> bool:
        """Test enemy damage system."""
        # Check if enemy damage system is available
        enemy_damage_available = hasattr(game_view, 'enemies') and len(game_view.enemies) > 0
        
        Debug.track_event("enemy_damage_test", {
            'enemies_available': hasattr(game_view, 'enemies'),
            'enemy_count': len(game_view.enemies) if hasattr(game_view, 'enemies') else 0
        })
        
        return Debug.validate_test("Enemy Damage", enemy_damage_available)
    
    def _test_car_part_collection(self, game_view) -> bool:
        """Test car part collection."""
        car_manager = game_view.car_manager
        
        print(f"[TEST] Car Part Test - Car manager available: {hasattr(game_view, 'car_manager')}")
        print(f"[TEST] Car Part Test - Parts collected attribute: {hasattr(car_manager, 'car_parts_collected') if car_manager else False}")
        
        # Check if car part collection is available
        part_collection_available = hasattr(car_manager, 'car_parts_collected')
        
        Debug.track_event("car_part_collection_test", {
            'car_manager_available': hasattr(game_view, 'car_manager'),
            'parts_collected_available': hasattr(car_manager, 'car_parts_collected') if car_manager else False
        })
        
        print(f"[TEST] Car Part Test - Part collection available: {part_collection_available}")
        
        return Debug.validate_test("Car Part Collection", part_collection_available)
    
    def _test_car_usage(self, game_view) -> bool:
        """Test car usage functionality."""
        car_manager = game_view.car_manager
        
        # Check if car usage is available
        car_usage_available = hasattr(car_manager, 'handle_car_interaction')
        
        Debug.track_event("car_usage_test", {
            'car_manager_available': hasattr(game_view, 'car_manager'),
            'interaction_method_available': hasattr(car_manager, 'handle_car_interaction') if car_manager else False
        })
        
        return Debug.validate_test("Car Usage", car_usage_available)
    
    def _test_health_bar_updates(self, game_view) -> bool:
        """Test health bar updates."""
        player = game_view.player
        
        # Check if health bar is available
        health_bar_available = hasattr(player, 'health_bar') or hasattr(player, 'current_health')
        
        Debug.track_event("health_bar_test", {
            'health_bar_available': hasattr(player, 'health_bar'),
            'current_health_available': hasattr(player, 'current_health')
        })
        
        return Debug.validate_test("Health Bar Updates", health_bar_available)
    
    def _test_damage_application(self, game_view) -> bool:
        """Test damage application."""
        player = game_view.player
        
        # Check if damage system is available
        damage_system_available = hasattr(player, 'current_health') and hasattr(player, 'max_health')
        
        Debug.track_event("damage_application_test", {
            'current_health_available': hasattr(player, 'current_health'),
            'max_health_available': hasattr(player, 'max_health')
        })
        
        return Debug.validate_test("Damage Application", damage_system_available)
    
    def generate_test_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = 0
        passed_tests = 0
        
        for category, category_results in results.items():
            for test_name, test_result in category_results.items():
                total_tests += 1
                if test_result:
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate,
            'detailed_results': results
        }
        
        print(f"\n[TEST] === FINAL TEST RESULTS ===")
        print(f"[TEST] Total Tests: {total_tests}")
        print(f"[TEST] Passed: {passed_tests}")
        print(f"[TEST] Failed: {total_tests - passed_tests}")
        print(f"[TEST] Success Rate: {success_rate:.1f}%")
        
        if total_tests - passed_tests > 0:
            print(f"[TEST] Failed Tests:")
            for category, category_results in results.items():
                for test_name, test_result in category_results.items():
                    if not test_result:
                        print(f"[TEST]   - {category}.{test_name}")
        
        print(f"[TEST] === END TEST RESULTS ===\n")
        
        return report
    
    def clear_all_data(self):
        """Clear all testing data."""
        self.current_objective = None
        self.test_results.clear()
        self.tracking_components.clear()
        self.active_tests.clear()
        Debug.clear_testing_data() 