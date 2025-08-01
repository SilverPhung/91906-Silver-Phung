import arcade
from src.views.base_view import BaseView
from src.views.game_view import GameView


class MenuView(BaseView):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()
        # Use a more appealing background color
        self.background_color = arcade.color.DARK_GREEN
        
        # Create game title
        self.title_text = self.add_centered_text(
            "Zombie Survival: Car Escape",
            y_offset=100,
            color=arcade.color.WHITE,
            font_size=32
        )
        
        # Create game description as separate text objects
        self.description_line1 = self.add_centered_text(
            "You are a survivor in a zombie apocalypse.",
            y_offset=60,
            color=arcade.color.LIGHT_GRAY,
            font_size=16
        )
        self.description_line2 = self.add_centered_text(
            "Your car is broken and you need to find car parts",
            y_offset=40,
            color=arcade.color.LIGHT_GRAY,
            font_size=16
        )
        self.description_line3 = self.add_centered_text(
            "to repair it and escape to safety.",
            y_offset=20,
            color=arcade.color.LIGHT_GRAY,
            font_size=16
        )
        self.description_line4 = self.add_centered_text(
            "Explore the maps, fight zombies, and collect",
            y_offset=0,
            color=arcade.color.LIGHT_GRAY,
            font_size=16
        )
        self.description_line5 = self.add_centered_text(
            "car parts from chests to complete your mission.",
            y_offset=-20,
            color=arcade.color.LIGHT_GRAY,
            font_size=16
        )
        
        # Create controls text as separate text objects
        self.controls_header = self.add_centered_text(
            "Controls:",
            y_offset=-60,
            color=arcade.color.YELLOW,
            font_size=14
        )
        self.controls_line1 = self.add_centered_text(
            "WASD/Arrow Keys to move",
            y_offset=-80,
            color=arcade.color.YELLOW,
            font_size=14
        )
        self.controls_line2 = self.add_centered_text(
            "SPACE to attack",
            y_offset=-100,
            color=arcade.color.YELLOW,
            font_size=14
        )
        self.controls_line3 = self.add_centered_text(
            "E to interact",
            y_offset=-120,
            color=arcade.color.YELLOW,
            font_size=14
        )
        self.controls_line4 = self.add_centered_text(
            "1-5 to switch weapons",
            y_offset=-140,
            color=arcade.color.YELLOW,
            font_size=14
        )
        
        # Create start game text
        self.start_text = self.add_centered_text(
            "Press SPACE to start your survival journey",
            y_offset=-180,
            color=arcade.color.LIGHT_GREEN,
            font_size=20
        )

    def on_update(self, dt):
        """Handle transitions when fade_out is set"""
        self.update_fade(next_view=GameView)

    def on_show_view(self):
        """Called when switching to this view"""
        self.window.background_color = arcade.color.DARK_GREEN

    def on_key_press(self, key, _modifiers):
        """Handle key presses for menu navigation."""
        if self.fade_out is None:
            if key == arcade.key.SPACE:
                self.fade_out = 0
    


    def setup(self):
        """This should set up your game and get it ready to play"""
        pass 