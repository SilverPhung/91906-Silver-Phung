import arcade
from src.sprites.car import Car
from src.constants import TILE_SCALING, INTERACTION_DISTANCE


class CarManager:
    """
    Manages all car-related functionality including loading, interaction, and state.
    
    Uses the new Interactable-based Car class for consistent interaction behavior.
    """
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # Car-related properties
        self.old_car = None
        self.new_car = None
        self.car_parts_collected = 0
        self.near_car = None  # Track which car player is near

    def load_cars_from_map(self):
        """Load cars (old/new) from the Tiled object layers."""
        print("[CARS] Loading cars from map...")
        try:
            car_layers = {
                "Old-car": ("old_car", True),
                "New-car": ("new_car", False),
            }

            for layer_name, (attr_name, is_starting_car) in car_layers.items():
                car_objects = self.game_view.tile_map.object_lists.get(layer_name, [])
                if not car_objects:
                    print(f"[CARS] No objects found for layer '{layer_name}'")
                    continue

                pos_x, pos_y = car_objects[0].shape
                car = Car((pos_x, pos_y), is_starting_car=is_starting_car)
                setattr(self, attr_name, car)
                self.game_view.scene.add_sprite("CarsLayer", car)
                car_type = "Old" if is_starting_car else "New"
                print(f"[CARS] {car_type} car loaded at ({pos_x}, {pos_y})")

        except Exception as e:
            print(f"[CARS] Error loading cars from map: {e}")
            import traceback
            traceback.print_exc()

    def check_car_interactions(self):
        """
        Check if player is near any car and update interaction state.
        
        Uses the new Interactable proximity checking system.
        """
        previous_near_car = self.near_car
        self.near_car = None
        
        for car in (self.old_car, self.new_car):
            if car and not self.near_car:
                # Use the new Interactable proximity checking
                if car.check_proximity(self.game_view.player):
                    self.near_car = car
                    # Only log when proximity state changes
                    if previous_near_car != self.near_car:
                        car_type = "Old" if car.is_starting_car else "New"
                        print(f"[CARS] Player now near {car_type} car at ({car.center_x:.1f}, {car.center_y:.1f})")
                    break
        
        # Only log when proximity state changes
        if previous_near_car != self.near_car:
            if self.near_car is None:
                print(f"[CARS] Player no longer near any car")
        
        # Reset interaction state for cars not near player
        for car in (self.old_car, self.new_car):
            if car and car != self.near_car:
                car.reset_interaction_state()

    def handle_car_interaction(self):
        """
        Handle car interaction when E key is pressed.
        
        Uses the new Interactable interaction system.
        """
        if not self.near_car:
            print("[INTERACTION] No car nearby")
            return
        
        print(f"[CAR_INTERACTION] ===== CAR INTERACTION DEBUG =====")
        print(f"[CAR_INTERACTION]   Car type: {'Old' if self.near_car.is_starting_car else 'New'}")
        print(f"[CAR_INTERACTION]   Can interact: {self.near_car.can_interact()}")
        print(f"[CAR_INTERACTION]   Can use: {self.near_car.can_use()}")
        print(f"[CAR_INTERACTION]   Parts status: {self.near_car.get_parts_status()}")
        print(f"[CAR_INTERACTION]   Required parts: {self.near_car.required_parts}")
        print(f"[CAR_INTERACTION]   Collected parts: {self.near_car.collected_parts}")
        print(f"[CAR_INTERACTION] =================================")
        
        if not self.near_car.can_interact():
            print("[INTERACTION] Car cannot be interacted with")
            return
            
        print(f"[INTERACTION] Interacting with car: {'Old' if self.near_car.is_starting_car else 'New'}")
        
        # Use the new Interactable interaction handling
        should_transition = self.near_car.handle_interaction()
        
        print(f"[INTERACTION] Should transition: {should_transition}")
        
        if should_transition:
            print("[INTERACTION] Transitioning to next map")
            # Use the car to progress to next level
            self.game_view.key_down = {}
            self.game_view.player.move(arcade.math.Vec2(0, 0))
            self.game_view.transition_to_next_map()
        else:
            print("[INTERACTION] No transition - car interaction completed without transition")

    def position_player_at_old_car(self):
        """Position the player at the old car location."""
        if self.old_car:
            self.game_view.player.position = self.old_car.position
            print(f"[CARS] Player positioned at Old-car: ({self.old_car.center_x}, {self.old_car.center_y})")
            print(f"[CARS] Player actual position: center_x={self.game_view.player.center_x}, center_y={self.game_view.player.center_y}, position={self.game_view.player.position}")
        else:
            print("[CARS] Warning: No Old-car found for player positioning")

    def reset_car_parts(self):
        """Reset car parts for new level."""
        self.car_parts_collected = 0
        if self.new_car:
            self.new_car.reset_parts()
            print(f"[CARS] Car parts reset for new level")

    def add_test_car_part(self):
        """Add a car part for testing purposes."""
        if self.new_car:
            self.new_car.add_part()
            print(f"[PARTS] Added car part! Now have {self.new_car.get_parts_status()}")
        else:
            print("[PARTS] No new car found to add parts to")

    def reset_cars(self):
        """Reset car state for new map."""
        self.old_car = None
        self.new_car = None
        self.near_car = None
        self.car_parts_collected = 0
        print("[CARS] Car state reset")
    
    def get_near_car_interaction_text(self):
        """
        Get the interaction text for the car the player is near.
        
        Returns:
            str: Interaction text or None if no car nearby
        """
        if self.near_car:
            return self.near_car.get_interaction_text()
        return None 