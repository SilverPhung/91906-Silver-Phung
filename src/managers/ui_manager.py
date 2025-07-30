import arcade
from src.constants import WINDOW_HEIGHT


class UIManager:
    """Manages all UI elements and drawing functionality."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # UI Text objects for better performance
        self.interaction_text = arcade.Text("", 10, WINDOW_HEIGHT - 50, arcade.color.WHITE, 16)
        self.parts_text = arcade.Text("", 10, WINDOW_HEIGHT - 80, arcade.color.YELLOW, 14)
        self.map_text = arcade.Text("", 10, WINDOW_HEIGHT - 110, arcade.color.CYAN, 14)

    def draw_ui(self):
        """Draw all UI elements including car interaction prompts."""
        self._draw_interaction_text()
        self._draw_parts_status()
        self._draw_map_info()

    def _draw_interaction_text(self):
        """Draw car interaction text based on proximity and car state."""
        if not self.game_view.car_manager.near_car:
            self.interaction_text.text = ""
            return

        if self.game_view.car_manager.near_car.is_starting_car:
            # Old car - no interaction text
            self.interaction_text.text = ""
        elif self.game_view.car_manager.near_car.can_use():
            self.interaction_text.text = "Press E to use car"
        else:
            parts_needed = self.game_view.car_manager.near_car.required_parts - self.game_view.car_manager.near_car.collected_parts
            self.interaction_text.text = f"Need {parts_needed} more parts"
        
        self.interaction_text.draw()

    def _draw_parts_status(self):
        """Draw car parts status text."""
        if self.game_view.car_manager.new_car:
            self.parts_text.text = f"Car Parts: {self.game_view.car_manager.new_car.get_parts_status()}"
            self.parts_text.draw()

    def _draw_map_info(self):
        """Draw current map information."""
        self.map_text.text = f"Map: {self.game_view.current_map_index}/3"
        self.map_text.draw()

    def reset_ui(self):
        """Reset all UI text elements."""
        self.interaction_text.text = ""
        self.parts_text.text = ""
        self.map_text.text = ""
        print("[UI] UI elements reset") 