import arcade

from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.fading_view import FadingView
from src.views.game_view import GameView


class MenuView(FadingView):
    """ Class that manages the 'menu' view. """

    def on_update(self, dt):
        self.update_fade(next_view=GameView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.window.background_color = arcade.color.WHITE

    def __init__(self):
        super().__init__()
        self.menu_text = arcade.Text(
            "Menu Screen - press space to advance",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2,
            arcade.color.BLACK,
            font_size=30,
            anchor_x="center"
        )

    def on_draw(self):
        """ Draw the menu """
        self.clear()
        self.menu_text.draw()
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ Handle key presses. In this case, we'll just count a 'space' as
        game over and advance to the game over view. """
        if self.fade_out is None and key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        
        pass 