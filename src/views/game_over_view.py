import arcade
from src.views.base_view import BaseView
from src.views.menu_view import MenuView


class GameOverView(BaseView):
    """Class to manage the game overview"""

    def __init__(self):
        super().__init__()
        # Use a darker red background for game over
        self.background_color = arcade.color.DARK_RED

        # Create game over text using the factory with better contrast
        self.game_over_text = self.add_centered_text(
            "Game Over - press SPACE to advance",
            y_offset=0,
            color=arcade.color.WHITE,
            font_size=30,
        )

    def on_update(self, dt):
        self.update_fade(next_view=MenuView)

    def on_show_view(self):
        """Called when switching to this view"""
        self.background_color = arcade.color.DARK_RED

    def on_key_press(self, key, _modifiers):
        """If user hits escape, go back to the main menu view"""
        if key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """This should set up your game and get it ready to play"""
