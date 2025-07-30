"""
Reusable tracking components for testing.

This module contains modular tracking components that can be used to monitor
various aspects of the game during testing.
"""

import time
from typing import Dict, Any, List, Optional
from src.debug import Debug


class MovementTracker:
    """Tracks player movement for testing."""
    
    def __init__(self, player):
        self.player = player
        self.initial_position = player.position
        self.movement_events = []
        self.speed_measurements = []
        self.direction_changes = []
        self.collision_events = []
        
        print("[TESTING] MovementTracker initialized")
    
    def start_tracking(self):
        """Start tracking movement."""
        self.initial_position = self.player.position
        print("[TESTING] Movement tracking started")
    
    def record_movement(self, direction: str, speed: float):
        """Record a movement event."""
        event = {
            'direction': direction,
            'speed': speed,
            'position': self.player.position,
            'timestamp': time.time()
        }
        self.movement_events.append(event)
        self.speed_measurements.append(speed)
        
        Debug.track_event("movement", event)
    
    def record_direction_change(self, old_direction: str, new_direction: str):
        """Record a direction change."""
        change = {
            'old_direction': old_direction,
            'new_direction': new_direction,
            'timestamp': time.time()
        }
        self.direction_changes.append(change)
        
        Debug.track_event("direction_change", change)
    
    def record_collision(self, collision_type: str, position: tuple):
        """Record a collision event."""
        collision = {
            'type': collision_type,
            'position': position,
            'timestamp': time.time()
        }
        self.collision_events.append(collision)
        
        Debug.track_event("collision", collision)
    
    def get_results(self) -> Dict[str, Any]:
        """Get movement tracking results."""
        directions_tested = set(event['direction'] for event in self.movement_events)
        avg_speed = sum(self.speed_measurements) / len(self.speed_measurements) if self.speed_measurements else 0
        
        return {
            'total_movement_events': len(self.movement_events),
            'directions_tested': list(directions_tested),
            'speed_measurements': self.speed_measurements,
            'average_speed': avg_speed,
            'direction_changes': len(self.direction_changes),
            'collision_events': len(self.collision_events),
            'final_position': self.player.position,
            'movement_distance': self._calculate_movement_distance()
        }
    
    def _calculate_movement_distance(self) -> float:
        """Calculate total movement distance."""
        if not self.movement_events:
            return 0.0
        
        total_distance = 0.0
        for i in range(1, len(self.movement_events)):
            prev_pos = self.movement_events[i-1]['position']
            curr_pos = self.movement_events[i]['position']
            distance = ((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)**0.5
            total_distance += distance
        
        return total_distance


class CombatTracker:
    """Tracks combat interactions for testing."""
    
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.shots_fired = 0
        self.hits_landed = 0
        self.enemy_damage_events = []
        self.weapon_switches = []
        self.accuracy_measurements = []
        
        print("[TESTING] CombatTracker initialized")
    
    def record_shot(self, target_position: tuple, weapon_type: str = "default"):
        """Record a shot fired."""
        shot = {
            'target_position': target_position,
            'weapon_type': weapon_type,
            'timestamp': time.time()
        }
        self.shots_fired += 1
        
        Debug.track_event("shot_fired", shot)
    
    def record_hit(self, enemy, damage: int, weapon_type: str = "default"):
        """Record a successful hit."""
        hit = {
            'enemy': enemy,
            'damage': damage,
            'weapon_type': weapon_type,
            'timestamp': time.time()
        }
        self.hits_landed += 1
        self.enemy_damage_events.append(hit)
        
        # Calculate accuracy
        if self.shots_fired > 0:
            accuracy = self.hits_landed / self.shots_fired
            self.accuracy_measurements.append(accuracy)
        
        Debug.track_event("hit_landed", hit)
    
    def record_weapon_switch(self, old_weapon: str, new_weapon: str):
        """Record a weapon switch."""
        switch = {
            'old_weapon': old_weapon,
            'new_weapon': new_weapon,
            'timestamp': time.time()
        }
        self.weapon_switches.append(switch)
        
        Debug.track_event("weapon_switch", switch)
    
    def get_results(self) -> Dict[str, Any]:
        """Get combat tracking results."""
        accuracy = self.hits_landed / self.shots_fired if self.shots_fired > 0 else 0
        avg_accuracy = sum(self.accuracy_measurements) / len(self.accuracy_measurements) if self.accuracy_measurements else 0
        
        return {
            'shots_fired': self.shots_fired,
            'hits_landed': self.hits_landed,
            'accuracy': accuracy,
            'average_accuracy': avg_accuracy,
            'damage_events': len(self.enemy_damage_events),
            'weapon_switches': len(self.weapon_switches),
            'total_damage_dealt': sum(event['damage'] for event in self.enemy_damage_events)
        }


class CarInteractionTracker:
    """Tracks car interactions for testing."""
    
    def __init__(self, car_manager):
        self.car_manager = car_manager
        self.interaction_attempts = []
        self.parts_collected = 0
        self.car_usage_events = []
        self.interaction_distances = []
        
        print("[TESTING] CarInteractionTracker initialized")
    
    def record_interaction_attempt(self, car_type: str, success: bool, distance: float = 0.0):
        """Record a car interaction attempt."""
        attempt = {
            'car_type': car_type,
            'success': success,
            'distance': distance,
            'timestamp': time.time()
        }
        self.interaction_attempts.append(attempt)
        self.interaction_distances.append(distance)
        
        Debug.track_event("car_interaction_attempt", attempt)
    
    def record_part_collection(self, part_type: str = "generic"):
        """Record a car part collection."""
        collection = {
            'part_type': part_type,
            'timestamp': time.time()
        }
        self.parts_collected += 1
        
        Debug.track_event("part_collection", collection)
    
    def record_car_usage(self, car_type: str, success: bool):
        """Record car usage."""
        usage = {
            'car_type': car_type,
            'success': success,
            'timestamp': time.time()
        }
        self.car_usage_events.append(usage)
        
        Debug.track_event("car_usage", usage)
    
    def get_results(self) -> Dict[str, Any]:
        """Get car interaction tracking results."""
        successful_interactions = len([a for a in self.interaction_attempts if a['success']])
        avg_distance = sum(self.interaction_distances) / len(self.interaction_distances) if self.interaction_distances else 0
        
        return {
            'interaction_attempts': len(self.interaction_attempts),
            'successful_interactions': successful_interactions,
            'success_rate': successful_interactions / len(self.interaction_attempts) if self.interaction_attempts else 0,
            'parts_collected': self.parts_collected,
            'car_usage_events': len(self.car_usage_events),
            'average_interaction_distance': avg_distance,
            'car_types_interacted': list(set(attempt['car_type'] for attempt in self.interaction_attempts))
        }


class HealthTracker:
    """Tracks health system for testing."""
    
    def __init__(self, player):
        self.player = player
        self.initial_health = player.current_health
        self.health_changes = []
        self.damage_events = []
        self.healing_events = []
        self.health_bar_updates = []
        
        print("[TESTING] HealthTracker initialized")
    
    def record_health_change(self, old_health: int, new_health: int, reason: str):
        """Record a health change."""
        change = new_health - old_health
        health_event = {
            'old_health': old_health,
            'new_health': new_health,
            'change': change,
            'reason': reason,
            'timestamp': time.time()
        }
        self.health_changes.append(health_event)
        
        if change < 0:
            self.damage_events.append({
                'damage': abs(change),
                'reason': reason,
                'timestamp': time.time()
            })
        elif change > 0:
            self.healing_events.append({
                'healing': change,
                'reason': reason,
                'timestamp': time.time()
            })
        
        Debug.track_event("health_change", health_event)
    
    def record_health_bar_update(self, old_fullness: float, new_fullness: float):
        """Record a health bar update."""
        update = {
            'old_fullness': old_fullness,
            'new_fullness': new_fullness,
            'change': new_fullness - old_fullness,
            'timestamp': time.time()
        }
        self.health_bar_updates.append(update)
        
        Debug.track_event("health_bar_update", update)
    
    def get_results(self) -> Dict[str, Any]:
        """Get health tracking results."""
        total_damage = sum(event['damage'] for event in self.damage_events)
        total_healing = sum(event['healing'] for event in self.healing_events)
        
        return {
            'initial_health': self.initial_health,
            'current_health': self.player.current_health,
            'total_health_changes': len(self.health_changes),
            'damage_events': len(self.damage_events),
            'healing_events': len(self.healing_events),
            'total_damage_taken': total_damage,
            'total_healing_received': total_healing,
            'health_bar_updates': len(self.health_bar_updates),
            'net_health_change': self.player.current_health - self.initial_health
        } 