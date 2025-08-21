import arcade
from src.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class TextFactory:
    """Factory class for creating consistent text objects across views"""

    @staticmethod
    def create_centered_text(
        text: str,
        y_offset: int = 0,
        color=arcade.color.WHITE,
        font_size: int = 24,
        anchor_x: str = "center",
        anchor_y: str = "center",
    ) -> arcade.Text:
        """Create a centered text object with consistent positioning"""
        try:
            text_obj = arcade.Text(
                text,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + y_offset,
                color,
                font_size,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
            )
            return text_obj
        except Exception:
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback

    @staticmethod
    def create_positioned_text(
        text: str,
        x: int,
        y: int,
        color=arcade.color.WHITE,
        font_size: int = 24,
        anchor_x: str = "center",
        anchor_y: str = "center",
    ) -> arcade.Text:
        """Create a text object at specific coordinates"""
        try:
            text_obj = arcade.Text(
                text,
                x,
                y,
                color,
                font_size,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
            )
            return text_obj
        except Exception:
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback

    @staticmethod
    def create_ui_text(
        text: str,
        x: int = 10,
        y: int = WINDOW_HEIGHT - 50,
        color=arcade.color.WHITE,
        font_size: int = 16,
    ) -> arcade.Text:
        """Create a UI text object for overlays"""
        try:
            text_obj = arcade.Text(text, x, y, color, font_size)
            return text_obj
        except Exception:
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback
