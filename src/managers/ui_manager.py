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
        
        # Fullscreen button properties
        self.fullscreen_button = {
            'x': 0,  # Will be set in draw method
            'y': 0,  # Will be set in draw method
            'width': 80,
            'height': 30,
            'text': '⛶',  # Fullscreen symbol
            'color': arcade.color.WHITE,
            'bg_color': arcade.color.BLACK,
            'border_color': arcade.color.GRAY,
            'hover_color': arcade.color.LIGHT_GRAY
        }

    def draw_ui(self):
        """Draw UI elements including car and chest interaction prompts."""
        # Update and draw interaction text
        self._draw_interaction_text()
        
        # Update and draw parts status
        self._draw_parts_status()
        
        # Update and draw map info
        self._draw_map_info()
        
        # Draw fullscreen button (temporarily disabled due to arcade method issues)
        # self._draw_fullscreen_button()

    def _draw_interaction_text(self):
        """Draw interaction text based on proximity to cars or chests."""
        try:
            # Prioritize chest interactions over car interactions
            if self.game_view.chest_manager.near_chest:
                interaction_text = self.game_view.chest_manager.get_near_chest_interaction_text()
                if interaction_text:
                    self.interaction_text.text = interaction_text
                else:
                    self.interaction_text.text = ""
            elif self.game_view.car_manager.near_car:
                interaction_text = self.game_view.car_manager.get_near_car_interaction_text()
                if interaction_text:
                    self.interaction_text.text = interaction_text
                else:
                    self.interaction_text.text = ""
            else:
                self.interaction_text.text = ""
            
            # Draw the interaction text centered on screen
            if self.interaction_text.text:
                arcade.draw_text(
                    self.interaction_text.text,
                    self.game_view.camera_gui.viewport_width // 2,
                    self.game_view.camera_gui.viewport_height - 50,
                    arcade.color.WHITE,
                    18,
                    anchor_x="center",
                    anchor_y="center",
                )
        except Exception as e:
            print(f"Error drawing interaction text: {e}")

    def _draw_parts_status(self):
        """Draw car parts status text."""
        try:
            # Get parts count from car manager, but use car's count if available for accuracy
            if (hasattr(self.game_view, 'car_manager') and 
                hasattr(self.game_view.car_manager, 'new_car') and 
                self.game_view.car_manager.new_car):
                parts_collected = self.game_view.car_manager.new_car.collected_parts
                required_parts = self.game_view.car_manager.new_car.required_parts
            else:
                parts_collected = getattr(self.game_view.car_manager, 'car_parts_collected', 0)
                from src.constants import REQUIRED_CAR_PARTS
                required_parts = REQUIRED_CAR_PARTS
            
            # Always display parts status, even if no new car exists
            parts_text = f"{parts_collected}/{required_parts}"
            arcade.draw_text(
                f"Car Parts: {parts_text}",
                10,
                self.game_view.camera_gui.viewport_height - 30,
                arcade.color.WHITE,
                14,
            )
        except Exception as e:
            print(f"Error drawing parts status: {e}")

    def _draw_map_info(self):
        """Draw current map information."""
        try:
            map_index = self.game_view.map_manager.current_map_index if hasattr(self.game_view, 'map_manager') else 1
            arcade.draw_text(
                f"Map: {map_index}/3",
                10,
                self.game_view.camera_gui.viewport_height - 110,
                arcade.color.CYAN,
                14,
            )
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
    
    def _draw_fullscreen_button(self):
        """Draw the fullscreen button in the top right corner."""
        try:
            # Position button in top right corner
            button = self.fullscreen_button
            button['x'] = self.game_view.camera_gui.viewport_width - button['width'] - 10
            button['y'] = self.game_view.camera_gui.viewport_height - button['height'] - 10
            
            # For now, just draw the button without hover detection
            is_hovering = False
            
            # Draw button background using simple rectangle
            bg_color = button['hover_color'] if is_hovering else button['bg_color']
            arcade.draw_rectangle_filled(
                button['x'] + button['width'] // 2,
                button['y'] + button['height'] // 2,
                button['width'],
                button['height'],
                bg_color
            )
            
            # Draw button border
            arcade.draw_rectangle_outline(
                button['x'] + button['width'] // 2,
                button['y'] + button['height'] // 2,
                button['width'],
                button['height'],
                button['border_color'],
                2
            )
            
            # Draw button text
            arcade.draw_text(
                button['text'],
                button['x'] + button['width'] // 2,
                button['y'] + button['height'] // 2,
                button['color'],
                16,
                anchor_x="center",
                anchor_y="center"
            )
            
        except Exception as e:
            print(f"Error drawing fullscreen button: {e}")
    
    def check_fullscreen_button_click(self, x, y):
        """Check if the fullscreen button was clicked."""
        try:
            button = self.fullscreen_button
            if (button['x'] <= x <= button['x'] + button['width'] and 
                button['y'] <= y <= button['y'] + button['height']):
                # Toggle fullscreen
                self.game_view.input_manager._toggle_fullscreen()
                return True
        except Exception as e:
            print(f"Error checking fullscreen button click: {e}")
        return False 