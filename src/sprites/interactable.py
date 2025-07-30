import arcade
from abc import ABC, abstractmethod
from src.constants import INTERACTION_DISTANCE


class Interactable(arcade.Sprite, ABC):
    """
    Base class for all interactable objects in the game.
    
    Provides common functionality for objects that can be interacted with
    by the player, such as cars, chests, doors, etc.
    
    This class follows the Open/Closed Principle - open for extension
    but closed for modification, allowing new interactable types to be
    added without changing existing code.
    """
    
    def __init__(self, position, sprite_path, scaling=1.0):
        """
        Initialize the interactable object.
        
        Args:
            position (tuple): The (x, y) position of the interactable
            sprite_path (str): Path to the sprite image
            scaling (float): Scaling factor for the sprite
        """
        super().__init__(sprite_path, scaling)
        
        # Set position
        self.center_x = position[0]
        self.center_y = position[1]
        self.position = position
        
        # Interaction state
        self.is_near_player = False
        self.interaction_distance = INTERACTION_DISTANCE
    
    def check_proximity(self, player):
        """
        Check if the player is within interaction distance.
        
        Args:
            player: The player sprite to check distance against
            
        Returns:
            bool: True if player is within interaction distance
        """
        try:
            distance = arcade.get_distance_between_sprites(self, player)
            self.is_near_player = distance <= self.interaction_distance
            return self.is_near_player
        except Exception as e:
            print(f"[INTERACTABLE] Error checking proximity: {e}")
            return False
    
    @abstractmethod
    def can_interact(self):
        """
        Check if the interactable can be interacted with.
        
        Returns:
            bool: True if interaction is possible
        """
        pass
    
    @abstractmethod
    def handle_interaction(self):
        """
        Handle the interaction when the player presses the interaction key.
        
        This method should be implemented by subclasses to define
        specific interaction behavior.
        """
        pass
    
    @abstractmethod
    def get_interaction_text(self):
        """
        Get the text to display when the player is near this interactable.
        
        Returns:
            str: The interaction prompt text
        """
        pass
    
    def reset_interaction_state(self):
        """
        Reset the interaction state when player moves away.
        """
        self.is_near_player = False
    
    def get_state_info(self):
        """
        Get debug information about the current state.
        
        Returns:
            str: Debug information about the interactable
        """
        return f"Position: ({self.center_x:.1f}, {self.center_y:.1f}), Near Player: {self.is_near_player}" 