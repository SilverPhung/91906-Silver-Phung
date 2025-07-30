import arcade
from src.constants import WINDOW_HEIGHT
from src.utils.text_factory import TextFactory


class UIManager:
    """Manages all UI elements and drawing functionality."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # UI Text objects for better performance using TextFactory
        try:
            self.interaction_text = TextFactory.create_ui_text("", y=WINDOW_HEIGHT - 50)
            self.parts_text = TextFactory.create_ui_text("", y=WINDOW_HEIGHT - 80, color=arcade.color.YELLOW, font_size=14)
            self.map_text = TextFactory.create_ui_text("", y=WINDOW_HEIGHT - 110, color=arcade.color.CYAN, font_size=14)
        except Exception as e:
            print(f"Error initializing UI manager: {e}")
            # Create fallback text objects
            self.interaction_text = arcade.Text("", 10, WINDOW_HEIGHT - 50, arcade.color.WHITE, 16)
            self.parts_text = arcade.Text("", 10, WINDOW_HEIGHT - 80, arcade.color.YELLOW, 14)
            self.map_text = arcade.Text("", 10, WINDOW_HEIGHT - 110, arcade.color.CYAN, 14)

    def draw_ui(self):
        """Draw UI elements including car and chest interaction prompts."""
        # Draw car interaction text
        if self.game_view.car_manager.near_car:
            interaction_text = self.game_view.car_manager.get_near_car_interaction_text()
            if interaction_text:
                arcade.draw_text(
                    interaction_text,
                    self.game_view.camera_gui.viewport_width // 2,
                    self.game_view.camera_gui.viewport_height - 50,
                    arcade.color.WHITE,
                    18,
                    anchor_x="center",
                    anchor_y="center",
                )
        
        # Draw chest interaction text (prioritize chest over car)
        elif self.game_view.chest_manager.near_chest:
            interaction_text = self.game_view.chest_manager.get_near_chest_interaction_text()
            if interaction_text:
                arcade.draw_text(
                    interaction_text,
                    self.game_view.camera_gui.viewport_width // 2,
                    self.game_view.camera_gui.viewport_height - 50,
                    arcade.color.WHITE,
                    18,
                    anchor_x="center",
                    anchor_y="center",
                )
        
        # Draw car parts status
        if self.game_view.car_manager.new_car:
            parts_text = self.game_view.car_manager.new_car.get_parts_status()
            arcade.draw_text(
                f"Car Parts: {parts_text}",
                10,
                self.game_view.camera_gui.viewport_height - 30,
                arcade.color.WHITE,
                14,
            )
        
        # Draw chest stats for debugging
        chest_stats = self.game_view.chest_manager.get_chest_stats()
        if chest_stats["total_chests"] > 0:
            arcade.draw_text(
                f"Chests: {chest_stats['total_chests']} (Parts: {chest_stats['parts_collected']}/{chest_stats['chests_with_parts']})",
                10,
                self.game_view.camera_gui.viewport_height - 50,
                arcade.color.YELLOW,
                12,
            )

    def _draw_interaction_text(self):
        """Draw car interaction text based on proximity and car state."""
        try:
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
        except Exception as e:
            print(f"Error drawing interaction text: {e}")

    def _draw_parts_status(self):
        """Draw car parts status text."""
        try:
            if self.game_view.car_manager.new_car:
                self.parts_text.text = f"Car Parts: {self.game_view.car_manager.new_car.get_parts_status()}"
                self.parts_text.draw()
        except Exception as e:
            print(f"Error drawing parts status: {e}")

    def _draw_map_info(self):
        """Draw current map information."""
        try:
            self.map_text.text = f"Map: {self.game_view.current_map_index}/3"
            self.map_text.draw()
        except Exception as e:
            print(f"Error drawing map info: {e}")

    def reset_ui(self):
        """Reset all UI text elements."""
        try:
            self.interaction_text.text = ""
            self.parts_text.text = ""
            self.map_text.text = ""
        except Exception as e:
            print(f"Error resetting UI: {e}") 