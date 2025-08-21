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
            font_size=32,
        )

        # Create game description as separate text objects
        descriptions = [
            ("You are a survivor in a zombie apocalypse.", 60),
            ("Your car is broken and you need to find car parts", 40),
            ("to repair it and escape to safety.", 20),
            ("Explore the maps, fight zombies, and collect", 0),
            ("car parts from chests to complete your mission.", -20),
        ]

        self.description_lines = []
        for desc_text, y_pos in descriptions:
            line = self.add_centered_text(
                desc_text,
                y_offset=y_pos,
                color=arcade.color.LIGHT_GRAY,
                font_size=16,
            )
            self.description_lines.append(line)

        # Create controls text as separate text objects
        controls = [
            ("Controls:", -60),
            ("WASD/Arrow Keys to move", -80),
            ("SPACE to attack", -100),
            ("E to interact", -120),
            ("1-5 to switch weapons", -140),
        ]

        self.control_lines = []
        for control_text, y_pos in controls:
            line = self.add_centered_text(
                control_text,
                y_offset=y_pos,
                color=arcade.color.YELLOW,
                font_size=14,
            )
            self.control_lines.append(line)



        # Create start game text
        self.start_text = self.add_centered_text(
            "Press SPACE to start your survival journey",
            y_offset=-180,
            color=arcade.color.LIGHT_GREEN,
            font_size=20,
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
