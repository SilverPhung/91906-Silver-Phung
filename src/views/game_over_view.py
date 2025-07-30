import arcade

from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.fading_view import FadingView
from src.views.menu_view import MenuView


class GameOverView(FadingView):
    """ Class to manage the game overview """
    def __init__(self):
        super().__init__()
        self.game_over_text = arcade.Text(
            "Game Over - press SPACE to advance",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center"
        )

    def on_update(self, dt):
        self.update_fade(next_view=MenuView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """ Draw the game overview """
        self.clear()
        self.game_over_text.draw()
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ If user hits escape, go back to the main menu view """
        if key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        
        pass 