import arcade
from src.sprites.car import Car
from src.constants import TILE_SCALING, INTERACTION_DISTANCE


class CarManager:
    """Manages all car-related functionality including loading, interaction, and state."""
    
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
        """Check if player is near any car and update interaction state."""
        self.near_car = None
        
        for car in (self.old_car, self.new_car):
            if car and not self.near_car:
                distance = arcade.get_distance_between_sprites(self.game_view.player, car)
                if distance <= INTERACTION_DISTANCE:
                    self.near_car = car
                    break

    def handle_car_interaction(self):
        """Handle car interaction when E key is pressed."""
        if not self.near_car:
            print("[INTERACTION] No car nearby")
            return
            
        print(f"[INTERACTION] Interacting with car: {'Old' if self.near_car.is_starting_car else 'New'}")
        
        # Only allow interaction with New-car when it can be used
        if not self.near_car.is_starting_car:
            if self.near_car.can_use():
                print("[INTERACTION] New car can be used, transitioning to next map")
                # Use the car to progress to next level
                self.game_view.key_down = {}
                self.game_view.player.move(arcade.math.Vec2(0, 0))
                self.game_view.transition_to_next_map()
            else:
                print(f"[INTERACTION] Cannot use car yet. Need {self.near_car.required_parts - self.near_car.collected_parts} more parts")
        else:
            # Old car - no interaction allowed
            print("[INTERACTION] This car is broken and cannot be used")

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