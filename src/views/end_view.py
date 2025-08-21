import arcade
from src.views.base_view import BaseView


class EndView(BaseView):
    """End screen shown when the player wins the game"""

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.DARK_GREEN

        # Create text objects using the factory
        self.title_text = self.add_centered_text(
            "CONGRATULATIONS!",
            y_offset=100,
            color=arcade.color.GOLD,
            font_size=48,
        )
        self.subtitle_text = self.add_centered_text(
            "You have successfully completed all 3 levels!",
            y_offset=50,
            color=arcade.color.WHITE,
            font_size=24,
        )
        self.stats_text = self.add_centered_text(
            "All cars have been repaired and \
                you've escaped the zombie apocalypse!",
            y_offset=0,
            color=arcade.color.LIGHT_BLUE,
            font_size=20,
        )
        self.instruction_text = self.add_centered_text(
            "Press SPACE to return to main menu",
            y_offset=-50,
            color=arcade.color.YELLOW,
            font_size=24,
        )
        self.credits_text = self.add_centered_text(
            "Thanks for playing!",
            y_offset=-100,
            color=arcade.color.GREEN,
            font_size=18,
        )

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.SPACE:
            # Return to main menu using direct import
            from src.views.menu_view import MenuView

            menu_view = MenuView()
            self.window.show_view(menu_view)
