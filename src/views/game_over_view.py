import arcade

from ui_constants import WIDTH, HEIGHT
from views.fading_view import FadingView
from views.menu_view import MenuView


class GameOverView(FadingView):
    """ Class to manage the game overview """
    def on_update(self, dt):
        self.update_fade(next_view=MenuView)

    def on_show_view(self):
        """ Called when switching to this view"""
        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """ Draw the game overview """
        self.clear()
        arcade.draw_text("Game Over - press SPACE to advance", WIDTH / 2, HEIGHT / 2,
                         arcade.color.WHITE, 30, anchor_x="center")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        """ If user hits escape, go back to the main menu view """
        if key == arcade.key.SPACE:
            self.fade_out = 0

    def setup(self):
        """ This should set up your game and get it ready to play """
        # Replace 'pass' with the code to set up your game
        pass 