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

        try:
            car_layers = {
                "Old-car": ("old_car", True),
                "New-car": ("new_car", False),
            }

            for layer_name, (attr_name, is_starting_car) in car_layers.items():
                # Get tile_map from MapManager
                tile_map = self.game_view.map_manager.get_tile_map() if hasattr(self.game_view, 'map_manager') else self.game_view.tile_map
                car_objects = tile_map.object_lists.get(layer_name, [])
                if not car_objects:
                    continue

                pos_x, pos_y = car_objects[0].shape
                car = Car((pos_x, pos_y), is_starting_car=is_starting_car)
                setattr(self, attr_name, car)
                self.game_view.scene.add_sprite("CarsLayer", car)
                car_type = "Old" if is_starting_car else "New"


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
            self.game_view.player.position = self.old_car.position
        else:
            pass

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