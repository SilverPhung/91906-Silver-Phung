import arcade
from arcade.math import clamp

from src.constants import FADE_RATE


class FadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fade_out = None
        self.fade_in = None  # Start with no fade overlay so views are visible
        self.next_view = None

    def update_fade(self, next_view=None):
        if self.next_view is None:
            self.next_view = next_view()

        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if (
                self.fade_out is not None
                and self.fade_out > 255
                and next_view is not None
                and self.next_view
            ):
                self.next_view.setup()
                self.window.show_view(self.next_view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self):
        if self.fade_out is not None:
            arcade.draw_rect_filled(
                arcade.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height,
                ),
                color=(0, 0, 0, clamp(self.fade_out, 0, 255)),
            )

        if self.fade_in is not None:
            arcade.draw_rect_filled(
                arcade.XYWH(
                    self.window.width / 2,
                    self.window.height / 2,
                    self.window.width,
                    self.window.height,
                ),
                color=(0, 0, 0, clamp(self.fade_in, 0, 255)),
            )
