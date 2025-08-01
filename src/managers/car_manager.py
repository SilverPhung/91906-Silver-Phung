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

    def clear_cars(self):
        """Clear cars completely for new map."""
        # Simply set to None - the scene will be cleared separately
        self.old_car = None
        self.new_car = None
        self.near_car = None
        self.car_parts_collected = 0
        
    def get_all_cars(self):
        """Get all cars as a list."""
        cars = []
        if self.old_car:
            cars.append(self.old_car)
        if self.new_car:
            cars.append(self.new_car)
        return cars
        
    def load_cars_from_map(self):
        """Load cars (old/new) from the Tiled object layers."""
        # Check if cars are already loaded
        if self.old_car or self.new_car:
            print(f"[CAR_MANAGER] Cars already loaded, skipping")
            return  # Already loaded
            
        try:
            car_layers = {
                "Old-car": ("old_car", True),
                "New-car": ("new_car", False),
            }

            for layer_name, (attr_name, is_starting_car) in car_layers.items():
                # Get tile_map from MapManager
                tile_map = self.game_view.map_manager.get_tile_map() if hasattr(self.game_view, 'map_manager') else self.game_view.tile_map
                car_objects = tile_map.object_lists.get(layer_name, [])
                print(f"[CAR_MANAGER] Looking for {layer_name}, found {len(car_objects)} objects")
                if not car_objects:
                    continue

                pos_x, pos_y = car_objects[0].shape
                car = Car((pos_x, pos_y), is_starting_car=is_starting_car)
                setattr(self, attr_name, car)
                self.game_view.scene.add_sprite("CarsLayer", car)
                car_type = "Old" if is_starting_car else "New"
                print(f"[CAR_MANAGER] Added {car_type} car to scene at ({car.center_x:.1f}, {car.center_y:.1f})")
                
                # Debug: Verify car is actually in the scene
                car_list = self.game_view.scene.get_sprite_list("CarsLayer")
                if car_list and car in car_list:
                    print(f"[CAR_MANAGER] ✓ {car_type} car confirmed in scene")
                else:
                    print(f"[CAR_MANAGER] ✗ {car_type} car NOT found in scene!")


        except Exception as e:
    
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
                    break
        
        # Only log when proximity state changes
        if previous_near_car != self.near_car:
            if self.near_car is None:
                pass
        
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
            return
        
        if not self.near_car.can_interact():
            return
            
        # Use the new Interactable interaction handling
        should_transition = self.near_car.handle_interaction()
        
        if should_transition:
            # Use the car to progress to next level
            self.game_view.key_down = {}
            self.game_view.player.move(arcade.math.Vec2(0, 0))
            self.game_view.transition_to_next_map()

    def position_player_at_old_car(self):
        """Position the player at the old car location."""
        if self.old_car:
            # Update player position and spawn position for this map
            new_position = self.old_car.position
            self.game_view.player.position = new_position
            self.game_view.player.update_spawn_position(new_position)
            print(f"[CAR_MANAGER] Player positioned at old car: {new_position}")
        else:
            print(f"[CAR_MANAGER] No old car found for player positioning")

    def reset_car_parts(self):
        """Reset car parts for new level."""
        self.car_parts_collected = 0
        if self.new_car:
            self.new_car.reset_parts()


    def add_test_car_part(self):
        """Add a car part for testing purposes."""
        if self.new_car:
            self.new_car.add_part()

        else:
            pass

    def reset_cars(self):
        """Reset car state for new map."""
        self.old_car = None
        self.new_car = None
        self.near_car = None
        self.car_parts_collected = 0

    
    def get_near_car_interaction_text(self):
        """
        Get the interaction text for the car the player is near.
        
        Returns:
            str: Interaction text or None if no car nearby
        """
        if self.near_car:
            return self.near_car.get_interaction_text()
        return None 