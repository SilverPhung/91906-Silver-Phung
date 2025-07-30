import arcade
from src.constants import CAR_SCALING, CAR_SPRITE_PATH, REQUIRED_CAR_PARTS


class Car(arcade.Sprite):
    """Car class for starting and ending points in the game"""
    
    def __init__(self, position, is_starting_car=True):
        """Initialize the car sprite"""
        super().__init__(CAR_SPRITE_PATH, CAR_SCALING)
        
        self.position = position
        self.is_starting_car = is_starting_car
        self.required_parts = REQUIRED_CAR_PARTS
        self.collected_parts = 0
        
        # Set initial position
        self.center_x = position[0]
        self.center_y = position[1]
    
    def can_use(self):
        """Check if the car can be used (has enough parts)"""
        return self.collected_parts >= self.required_parts
    
    def add_part(self):
        """Add a car part"""
        if self.collected_parts < self.required_parts:
            self.collected_parts += 1
            return True
        return False
    
    def get_parts_status(self):
        """Get the parts status as a string"""
        return f"{self.collected_parts}/{self.required_parts}"
    
    def get_interaction_text(self):
        """Get the appropriate interaction text based on car type and parts"""
        if self.is_starting_car:
            if self.can_use():
                return "Press E to use car"
            else:
                return f"Need {self.required_parts - self.collected_parts} more parts"
        else:
            return f"Car needs {self.required_parts - self.collected_parts} parts"
    
    def reset_parts(self):
        """Reset collected parts to 0"""
        self.collected_parts = 0 