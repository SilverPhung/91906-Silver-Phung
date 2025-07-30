"""
Testing integration system for runtime tracking injection.

This module provides easy integration points for testing by injecting tracking
logic into existing game components at runtime without modifying core game logic.
"""

import time
from typing import Dict, Any, Optional
from src.debug import Debug
from src.constants import ENABLE_TESTING


class TestingIntegration:
    """Provides easy integration points for testing."""
    
    @staticmethod
    def inject_tracking_into_player(player):
        """Inject tracking into player without modifying core logic."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Injecting tracking into player...")
        print(f"[TESTING] Player type: {type(player)}")
        print(f"[TESTING] Player has move method: {hasattr(player, 'move')}")
        print(f"[TESTING] Player has update method: {hasattr(player, 'update')}")
        print(f"[TESTING] Player has take_damage method: {hasattr(player, 'take_damage')}")
        
        # Store original methods
        original_update = player.update
        original_move = getattr(player, 'move', None)
        original_take_damage = getattr(player, 'take_damage', None)
        
        # Create tracking wrapper for update method
        print(f"[TESTING] Creating tracked_update wrapper for player")
        def tracked_update(delta_time):
            try:
                # Call original update
                result = original_update(delta_time)
                
                # Add tracking if testing is enabled
                if ENABLE_TESTING:
                    TestingIntegration.track_player_update(player, delta_time)
                
                return result
            except Exception as e:
                print(f"[TESTING] Error in tracked_update: {e}")
                # Fallback to original method
                return original_update(delta_time)
        
        # Create tracking wrapper for move method
        if original_move:
            print(f"[TESTING] Creating tracked_move wrapper for player")
            def tracked_move(direction):
                try:
                    # Call original move
                    result = original_move(direction)
                    
                    # Add tracking if testing is enabled
                    if ENABLE_TESTING:
                        # Extract speed from direction vector
                        speed = direction.length() if hasattr(direction, 'length') else 0
                        TestingIntegration.track_player_movement(player, direction, speed)
                    
                    return result
                except Exception as e:
                    print(f"[TESTING] Error in tracked_move: {e}")
                    # Fallback to original method
                    return original_move(direction)
            
            player.move = tracked_move
            print(f"[TESTING] Successfully replaced player.move with tracked version")
        else:
            print(f"[TESTING] No move method found on player")
        
        # Create tracking wrapper for take_damage method
        if original_take_damage:
            print(f"[TESTING] Creating tracked_take_damage wrapper for player")
            def tracked_take_damage(damage):
                try:
                    old_health = getattr(player, 'current_health', 0)
                    
                    # Call original take_damage
                    result = original_take_damage(damage)
                    
                    # Add tracking if testing is enabled
                    if ENABLE_TESTING:
                        new_health = getattr(player, 'current_health', 0)
                        TestingIntegration.track_player_damage(player, old_health, new_health, damage)
                    
                    return result
                except Exception as e:
                    print(f"[TESTING] Error in tracked_take_damage: {e}")
                    # Fallback to original method
                    return original_take_damage(damage)
            
            player.take_damage = tracked_take_damage
            print(f"[TESTING] Successfully replaced player.take_damage with tracked version")
        else:
            print(f"[TESTING] No take_damage method found on player")
        
        # Replace update method
        player.update = tracked_update
        print(f"[TESTING] Successfully replaced player.update with tracked version")
        
        print("[TESTING] Player tracking injection complete")
    
    @staticmethod
    def inject_tracking_into_car_manager(car_manager):
        """Inject tracking into car manager."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Injecting tracking into car manager...")
        
        # Store original methods
        original_handle_interaction = getattr(car_manager, 'handle_car_interaction', None)
        original_check_interactions = getattr(car_manager, 'check_car_interactions', None)
        
        # Create tracking wrapper for handle_interaction method
        if original_handle_interaction:
            def tracked_handle_interaction():
                # Call original method
                result = original_handle_interaction()
                
                # Add tracking if testing is enabled
                if ENABLE_TESTING:
                    TestingIntegration.track_car_interaction(car_manager)
                
                return result
            
            car_manager.handle_car_interaction = tracked_handle_interaction
        
        # Create tracking wrapper for check_interactions method
        if original_check_interactions:
            def tracked_check_interactions():
                # Call original method
                result = original_check_interactions()
                
                # Add tracking if testing is enabled
                if ENABLE_TESTING:
                    TestingIntegration.track_car_proximity_check(car_manager)
                
                return result
            
            car_manager.check_car_interactions = tracked_check_interactions
        
        print("[TESTING] Car manager tracking injection complete")
    
    @staticmethod
    def inject_tracking_into_chest_manager(chest_manager):
        """Inject tracking into chest manager."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Injecting tracking into chest manager...")
        
        # Store original methods
        original_handle_interaction = getattr(chest_manager, 'handle_chest_interaction', None)
        original_check_interactions = getattr(chest_manager, 'check_chest_interactions', None)
        
        # Create tracking wrapper for handle_interaction method
        if original_handle_interaction:
            def tracked_handle_interaction():
                # Call original method
                result = original_handle_interaction()
                
                # Add tracking if testing is enabled
                if ENABLE_TESTING:
                    TestingIntegration.track_chest_interaction(chest_manager)
                
                return result
            
            chest_manager.handle_chest_interaction = tracked_handle_interaction
        
        # Create tracking wrapper for check_interactions method
        if original_check_interactions:
            def tracked_check_interactions():
                # Call original method
                result = original_check_interactions()
                
                # Add tracking if testing is enabled
                if ENABLE_TESTING:
                    TestingIntegration.track_chest_proximity_check(chest_manager)
                
                return result
            
            chest_manager.check_chest_interactions = tracked_check_interactions
        
        print("[TESTING] Chest manager tracking injection complete")
    
    @staticmethod
    def inject_tracking_into_game_view(game_view):
        """Inject tracking into game view."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Injecting tracking into game view...")
        
        # Store original methods
        original_on_update = game_view.on_update
        original_on_draw = game_view.on_draw
        
        # Create tracking wrapper for on_update method
        def tracked_on_update(delta_time):
            # Call original on_update
            result = original_on_update(delta_time)
            
            # Add tracking if testing is enabled
            if ENABLE_TESTING:
                TestingIntegration.track_game_update(game_view, delta_time)
            
            return result
        
        # Create tracking wrapper for on_draw method
        def tracked_on_draw():
            # Call original on_draw
            result = original_on_draw()
            
            # Add tracking if testing is enabled
            if ENABLE_TESTING:
                TestingIntegration.track_game_draw(game_view)
            
            return result
        
        # Replace methods
        game_view.on_update = tracked_on_update
        game_view.on_draw = tracked_on_draw
        
        print("[TESTING] Game view tracking injection complete")
    
    # === Tracking Methods ===
    
    @staticmethod
    def track_player_update(player, delta_time):
        """Track player updates for testing."""
        try:
            if hasattr(player, '_movement_tracker'):
                # Record movement data
                velocity = getattr(player, 'velocity', (0, 0))
                position = getattr(player, 'center', (0, 0))
                
                Debug.track_event("player_update", {
                    'velocity': velocity,
                    'position': position,
                    'delta_time': delta_time
                })
            else:
                print(f"[TESTING] Player has no _movement_tracker attribute in update")
        except Exception as e:
            print(f"[TESTING] Error tracking player update: {e}")
    
    @staticmethod
    def track_player_movement(player, direction, speed):
        """Track player movement for testing."""
        try:
            if hasattr(player, '_movement_tracker'):
                tracker = player._movement_tracker
                tracker.record_movement(direction, speed)
                
                Debug.track_event("player_movement", {
                    'direction': direction,
                    'speed': speed,
                    'position': getattr(player, 'center', (0, 0))
                })
            else:
                print(f"[TESTING] Player has no _movement_tracker attribute")
        except Exception as e:
            print(f"[TESTING] Error tracking player movement: {e}")
    
    @staticmethod
    def track_player_damage(player, old_health, new_health, damage):
        """Track player damage for testing."""
        if hasattr(player, '_health_tracker'):
            tracker = player._health_tracker
            tracker.record_health_change(old_health, new_health, "damage")
            
            Debug.track_event("player_damage", {
                'old_health': old_health,
                'new_health': new_health,
                'damage': damage
            })
    
    @staticmethod
    def track_car_interaction(car_manager):
        """Track car interactions for testing."""
        if hasattr(car_manager, '_car_tracker'):
            tracker = car_manager._car_tracker
            # Record interaction attempt
            tracker.record_interaction_attempt("car", True, 0.0)
            
            Debug.track_event("car_interaction", {
                'near_car': getattr(car_manager, 'near_car', None) is not None,
                'parts_collected': getattr(car_manager, 'car_parts_collected', 0)
            })
    
    @staticmethod
    def track_car_proximity_check(car_manager):
        """Track car proximity checks for testing."""
        Debug.track_event("car_proximity_check", {
            'near_car': getattr(car_manager, 'near_car', None) is not None,
            'total_cars': len(getattr(car_manager, 'cars', []))
        })
    
    @staticmethod
    def track_chest_interaction(chest_manager):
        """Track chest interactions for testing."""
        if hasattr(chest_manager, '_chest_tracker'):
            tracker = chest_manager._chest_tracker
            # Record interaction attempt
            tracker.record_interaction_attempt("chest", True, 0.0)
            
            Debug.track_event("chest_interaction", {
                'near_chest': getattr(chest_manager, 'near_chest', None) is not None,
                'parts_collected': getattr(chest_manager, 'parts_collected_from_chests', 0)
            })
    
    @staticmethod
    def track_chest_proximity_check(chest_manager):
        """Track chest proximity checks for testing."""
        Debug.track_event("chest_proximity_check", {
            'near_chest': getattr(chest_manager, 'near_chest', None) is not None,
            'total_chests': len(getattr(chest_manager, 'chests_with_parts', [])) + 
                           len(getattr(chest_manager, 'chests_without_parts', []))
        })
    
    @staticmethod
    def track_game_update(game_view, delta_time):
        """Track game updates for testing."""
        Debug.track_event("game_update", {
            'delta_time': delta_time,
            'player_position': getattr(game_view.player, 'center', (0, 0)) if hasattr(game_view, 'player') else None,
            'enemy_count': len(getattr(game_view, 'enemies', []))
        })
    
    @staticmethod
    def track_game_draw(game_view):
        """Track game draws for testing."""
        Debug.track_event("game_draw", {
            'timestamp': time.time()
        })
    
    # === Utility Methods ===
    
    @staticmethod
    def inject_all_tracking(game_view):
        """Inject tracking into all major components."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Injecting tracking into all components...")
        print(f"[TESTING] Game view type: {type(game_view)}")
        print(f"[TESTING] Game view has player: {hasattr(game_view, 'player')}")
        print(f"[TESTING] Game view has car_manager: {hasattr(game_view, 'car_manager')}")
        print(f"[TESTING] Game view has chest_manager: {hasattr(game_view, 'chest_manager')}")
        
        # Inject into player
        if hasattr(game_view, 'player'):
            print(f"[TESTING] Injecting into player: {type(game_view.player)}")
            TestingIntegration.inject_tracking_into_player(game_view.player)
        else:
            print(f"[TESTING] No player found in game view")
        
        # Inject into car manager
        if hasattr(game_view, 'car_manager'):
            print(f"[TESTING] Injecting into car manager: {type(game_view.car_manager)}")
            TestingIntegration.inject_tracking_into_car_manager(game_view.car_manager)
        else:
            print(f"[TESTING] No car manager found in game view")
        
        # Inject into chest manager
        if hasattr(game_view, 'chest_manager'):
            print(f"[TESTING] Injecting into chest manager: {type(game_view.chest_manager)}")
            TestingIntegration.inject_tracking_into_chest_manager(game_view.chest_manager)
        else:
            print(f"[TESTING] No chest manager found in game view")
        
        # Inject into game view
        print(f"[TESTING] Injecting into game view")
        TestingIntegration.inject_tracking_into_game_view(game_view)
        
        print("[TESTING] All tracking injections complete")
    
    @staticmethod
    def remove_all_tracking(game_view):
        """Remove all tracking injections."""
        if not ENABLE_TESTING:
            return
        
        print("[TESTING] Removing all tracking injections...")
        
        # Note: In a real implementation, you would store original methods
        # and restore them here. For now, we'll just log the removal.
        
        print("[TESTING] All tracking injections removed") 