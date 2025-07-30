import arcade
from src.views.base_view import BaseView
from src.views.game_view import GameView


class MenuView(BaseView):
    """Class that manages the 'menu' view."""

    def __init__(self):
        super().__init__()
        # Use a more appealing background color
        self.background_color = arcade.color.DARK_GREEN
        
        # Create menu text using the factory with better contrast
        self.menu_text = self.add_centered_text(
            "Menu Screen - press space to advance",
            y_offset=0,
            color=arcade.color.WHITE,
            font_size=30
        )
        print("[TESTING] Menu screen loaded - player can start game")

    def on_update(self, dt):
        """Handle transitions when fade_out is set"""
        if self.fade_out is not None:
            self.update_fade(next_view=GameView)

    def on_show_view(self):
        """Called when switching to this view"""
        self.window.background_color = arcade.color.DARK_GREEN

    def on_key_press(self, key, _modifiers):
        """Handle key presses. In this case, we'll just count a 'space' as
        game over and advance to the game over view."""
        if self.fade_out is None and key == arcade.key.SPACE:
            print("[TESTING] Player pressed SPACE - starting game")
            self.fade_out = 0

    def setup(self):
        """This should set up your game and get it ready to play"""
        pass 