import arcade

from ui_constants import WIDTH, HEIGHT
from views.fading_view import FadingView
from views.game_view import GameView


class MenuView(FadingView):
    """ Class that manages the 'menu' view. """

    def on_update(self, dt):
        self.update_fade(next_view=GameView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.window.background_color = arcade.color.WHITE

    def on_draw(self):
        """ Draw the menu """
        self.clear()
        arcade.draw_text("Menu Screen - press space to advance", WIDTH / 2, HEIGHT / 2,
                         arcade.color.BLACK, font_size=30, anchor_x="center")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ Handle key presses. In this case, we'll just count a 'space' as
        game over and advance to the game over view. """
        if self.fade_out is None and key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        # Replace 'pass' with the code to set up your game
        pass 