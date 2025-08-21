import arcade
from src.views.fading_view import FadingView
from src.utils.text_factory import TextFactory
from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class BaseView(FadingView):
    """Base view class with common functionality for all views"""

    def __init__(self):
        super().__init__()
        self.text_objects = []
        self.background_color = arcade.color.BLACK

    def add_centered_text(
        self,
        text: str,
        y_offset: int = 0,
        color=arcade.color.WHITE,
        font_size: int = 24,
    ) -> arcade.Text:
        """Add a centered text object to this view"""
        try:
            text_obj = TextFactory.create_centered_text(
                text, y_offset, color, font_size
            )
            self.text_objects.append(text_obj)
            return text_obj
        except Exception:
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            self.text_objects.append(fallback)
            return fallback

    def add_positioned_text(
        self, text: str, x: int, y: int, color=arcade.color.WHITE, font_size: int = 24
    ) -> arcade.Text:
        """Add a positioned text object to this view"""
        try:
            text_obj = TextFactory.create_positioned_text(text, x, y, color, font_size)
            self.text_objects.append(text_obj)
            return text_obj
        except Exception:
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            self.text_objects.append(fallback)
            return fallback

    def draw_background(self):
        """Draw the background for this view"""
        try:
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, self.background_color
            )
        except Exception:
            # Fallback to black background
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, arcade.color.BLACK
            )

    def draw_texts(self):
        """Draw all text objects in this view"""
        try:
            for text_obj in self.text_objects:
                text_obj.draw()
        except Exception:
            pass

    def on_draw(self):
        """Default draw implementation"""
        try:
            self.clear()
            self.draw_background()
            self.draw_texts()
            self.draw_fading()
        except Exception:
            # Fallback drawing
            self.clear()
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, arcade.color.BLACK
            )

    def handle_space_key(self, key, modifiers):
        """Common space key handling for views"""
        try:
            if key == arcade.key.SPACE:
                self.fade_out = 0
                return True
            return False
        except Exception:
            return False
