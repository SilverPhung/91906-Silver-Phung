import arcade
import time
from enum import Enum
from src.sprites.interactable import Interactable
from src.constants import (
    CHEST_SCALING, CHEST_CLOSED_SPRITE, 
    CHEST_OPEN_EMPTY_SPRITE, CHEST_OPEN_WITH_PART_SPRITE
)


class ChestState(Enum):
    """Enumeration for chest states."""
    CLOSED = "closed"
    OPEN_EMPTY = "open_empty"
    OPEN_WITH_PART = "open_with_part"
    COLLECTED = "collected"


class Chest(Interactable):
    """
    Chest class for collectible items in the game.
    
    Inherits from Interactable to provide consistent interaction behavior
    while implementing chest-specific state management and part collection.
    
    States:
    - CLOSED: Initial state, shows closed.png
    - OPEN_EMPTY: After first E press if no part, shows open-empty.png
    - OPEN_WITH_PART: After first E press if has part, shows open-glow1.png
    - COLLECTED: After second E press, part collected, shows open-empty.png
    """
    
    def __init__(self, position, has_part=True):
        """
        Initialize the chest sprite.
        
        Args:
            position (tuple): The (x, y) position of the chest
            has_part (bool): Whether this chest contains a car part
        """
        # Try to load chest sprite, fallback to colored rectangle if failed
        try:
            # print(f"[CHEST] Loading chest sprite: {CHEST_CLOSED_SPRITE}")
            super().__init__(position, CHEST_CLOSED_SPRITE, CHEST_SCALING)
            self.use_sprites = True
            # print(f"[CHEST] Chest sprite loaded successfully")
        except Exception as e:
            # print(f"[CHEST] Failed to load chest sprite: {e}, using fallback")
            # Create a fallback colored rectangle
            self.use_sprites = False
            super().__init__(position, None, CHEST_SCALING)
            # Set a default color for the chest
            self.color = arcade.color.BROWN if has_part else arcade.color.GRAY
        
        # Chest-specific properties
        self.has_part = has_part
        self.state = ChestState.CLOSED
        self.interaction_count = 0  # Track number of interactions
    
    def can_interact(self):
        """
        Check if the chest can be interacted with.
        
        Returns:
            bool: True if interaction is possible
        """
        # Can always interact with chest regardless of state
        return True
    
    def handle_interaction(self):
        """
        Handle chest interaction when E key is pressed.
        
        Implements the two-interaction system:
        - First E press: Opens chest, reveals if part exists
        - Second E press: Collects part (only if chest has part)
        
        Returns:
            bool: True if a part was collected, False otherwise
        """
        self.interaction_count += 1
        # print(f"[CHEST] Interaction {self.interaction_count} - Current state: {self.state.value}")
        
        if self.state == ChestState.CLOSED:
            # First interaction: Open the chest
            # print(f"[CHEST] Opening chest with part: {self.has_part}")
            if self.has_part:
                self.state = ChestState.OPEN_WITH_PART
                # print(f"[CHEST] State changed to OPEN_WITH_PART")
                if self.use_sprites:
                    try:
                        # print(f"[CHEST] Loading texture: {CHEST_OPEN_WITH_PART_SPRITE}")
                        self.texture = arcade.load_texture(CHEST_OPEN_WITH_PART_SPRITE)
                        # print(f"[CHEST] Texture loaded successfully")
                    except Exception as e:
                        # print(f"[CHEST] Failed to load texture: {e}")
                        self.color = arcade.color.GOLD
                else:
                    self.color = arcade.color.GOLD
                    # print(f"[CHEST] Using fallback color: GOLD")
            else:
                self.state = ChestState.OPEN_EMPTY
                # print(f"[CHEST] State changed to OPEN_EMPTY")
                if self.use_sprites:
                    try:
                        # print(f"[CHEST] Loading texture: {CHEST_OPEN_EMPTY_SPRITE}")
                        self.texture = arcade.load_texture(CHEST_OPEN_EMPTY_SPRITE)
                        # print(f"[CHEST] Texture loaded successfully")
                    except Exception as e:
                        # print(f"[CHEST] Failed to load texture: {e}")
                        self.color = arcade.color.LIGHT_GRAY
                else:
                    self.color = arcade.color.LIGHT_GRAY
                    # print(f"[CHEST] Using fallback color: LIGHT_GRAY")
            return False
            
        elif self.state == ChestState.OPEN_WITH_PART:
            # Second interaction: Collect the part
            self.state = ChestState.COLLECTED
            if self.use_sprites:
                try:
                    self.texture = arcade.load_texture(CHEST_OPEN_EMPTY_SPRITE)
                except Exception as e:
                    self.color = arcade.color.LIGHT_GRAY
            else:
                self.color = arcade.color.LIGHT_GRAY
            return True  # Signal that a part was collected
            
        elif self.state == ChestState.OPEN_EMPTY:
            # Already opened empty - no further action
            return False
            
        elif self.state == ChestState.COLLECTED:
            # Already collected - no further action
            return False
        
        return False
    
    def get_interaction_text(self):
        """
        Get the appropriate interaction text based on chest state.
        
        Returns:
            str: The interaction prompt text
        """
        if self.state == ChestState.CLOSED:
            return "Press E to open chest"
        elif self.state == ChestState.OPEN_WITH_PART:
            return "Press E to collect part"
        elif self.state == ChestState.OPEN_EMPTY:
            return "Chest is empty"
        elif self.state == ChestState.COLLECTED:
            return "Part collected"
        else:
            return "Press E to interact"
    
    def get_state_info(self):
        """
        Get detailed debug information about the chest state.
        
        Returns:
            str: Debug information about the chest
        """
        base_info = super().get_state_info()
        return f"{base_info}, State: {self.state.value}, Has Part: {self.has_part}, Interactions: {self.interaction_count}"
    
    def reset_state(self):
        """
        Reset the chest to its initial state.
        Useful for testing or level reset.
        """
        self.state = ChestState.CLOSED
        self.interaction_count = 0
        if self.use_sprites:
            try:
                self.texture = arcade.load_texture(CHEST_CLOSED_SPRITE)
            except Exception as e:
                self.color = arcade.color.BROWN if self.has_part else arcade.color.GRAY
        else:
            self.color = arcade.color.BROWN if self.has_part else arcade.color.GRAY
    
    def draw(self):
        """Override draw method to handle fallback colored rectangles."""
        if not self.use_sprites and hasattr(self, 'color'):
            # Draw a colored rectangle as fallback
            arcade.draw_rectangle_filled(
                self.center_x, self.center_y,
                self.width, self.height,
                self.color
            )
            # Draw a border
            arcade.draw_rectangle_outline(
                self.center_x, self.center_y,
                self.width, self.height,
                arcade.color.BLACK, 2
            )
        else:
            # Use the parent arcade.Sprite draw method
            super(arcade.Sprite, self).draw() 