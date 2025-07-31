import arcade
from src.constants import CAR_SCALING, CAR_SPRITE_PATH, REQUIRED_CAR_PARTS
from src.sprites.interactable import Interactable


class Car(Interactable):
    """
    Car class for starting and ending points in the game.
    
    Inherits from Interactable to provide consistent interaction behavior
    while maintaining car-specific functionality like parts collection.
    """
    
    def __init__(self, position, is_starting_car=True):
        """
        Initialize the car sprite.
        
        Args:
            position (tuple): The (x, y) position of the car
            is_starting_car (bool): Whether this is the starting car (old car)
        """
        super().__init__(position, CAR_SPRITE_PATH, CAR_SCALING)
        
        # Car-specific properties
        self.is_starting_car = is_starting_car
        self.required_parts = REQUIRED_CAR_PARTS
        self.collected_parts = 0
    
    def can_use(self):
        """
        Check if the car can be used (has enough parts).
        
        Returns:
            bool: True if the car has enough parts to be used
        """
        return self.collected_parts >= self.required_parts
    
    def add_part(self):
        """
        Add a car part.
        
        Returns:
            bool: True if part was added successfully
        """
        if self.collected_parts < self.required_parts:
            self.collected_parts += 1

            return True
        return False
    
    def get_parts_status(self):
        """
        Get the parts status as a string.
        
        Returns:
            str: Parts status in format "collected/required"
        """
        return f"{self.collected_parts}/{self.required_parts}"
    
    def can_interact(self):
        """
        Check if the car can be interacted with.
        
        Returns:
            bool: True if interaction is possible
        """
        # Starting car can always be interacted with (for positioning)
        # New car can be interacted with if it has enough parts
        if self.is_starting_car:
            return True
        else:
            return self.can_use()
    
    def handle_interaction(self):
        """
        Handle car interaction when E key is pressed.
        
        For starting cars: No action (just positioning)
        For new cars: Transition to next map if ready
        """
        if self.is_starting_car:
            return False
        else:
            if self.can_use():
                return True  # Signal to transition to next map
            else:
                return False
    
    def get_interaction_text(self):
        """
        Get the appropriate interaction text based on car type and parts.
        
        Returns:
            str: The interaction prompt text
        """
        if self.is_starting_car:
            if self.can_use():
                return "Press E to use car"
            else:
                return f"Need {self.required_parts - self.collected_parts} more parts"
        else:
            if self.can_use():
                return "Press E to use car"
            else:
                return f"Car needs {self.required_parts - self.collected_parts} parts"
    
    def reset_parts(self):
        """
        Reset collected parts to 0.
        """
        self.collected_parts = 0
 