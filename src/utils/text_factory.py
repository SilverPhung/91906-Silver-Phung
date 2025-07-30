import arcade
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from typing import Optional, Tuple


class TextFactory:
    """Factory class for creating consistent text objects across views"""
    
    @staticmethod
    def create_centered_text(
        text: str,
        y_offset: int = 0,
        color = arcade.color.WHITE,
        font_size: int = 24,
        anchor_x: str = "center",
        anchor_y: str = "center"
    ) -> arcade.Text:
        """Create a centered text object with consistent positioning"""
        try:
            print(f"[TEXT_FACTORY] Creating centered text: '{text}'")
            print(f"[TEXT_FACTORY] Position: ({WINDOW_WIDTH // 2}, {WINDOW_HEIGHT // 2 + y_offset})")
            print(f"[TEXT_FACTORY] Color: {color}, Font size: {font_size}")
            text_obj = arcade.Text(
                text,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + y_offset,
                color,
                font_size,
                anchor_x=anchor_x,
                anchor_y=anchor_y
            )
            print(f"[TEXT_FACTORY] Centered text created successfully")
            return text_obj
        except Exception as e:
            print(f"[TEXT_FACTORY] Error creating centered text: {e}")
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback
    
    @staticmethod
    def create_positioned_text(
        text: str,
        x: int,
        y: int,
        color = arcade.color.WHITE,
        font_size: int = 24,
        anchor_x: str = "center",
        anchor_y: str = "center"
    ) -> arcade.Text:
        """Create a text object at specific coordinates"""
        try:
            print(f"[TEXT_FACTORY] Creating positioned text: '{text}' at ({x}, {y})")
            print(f"[TEXT_FACTORY] Color: {color}, Font size: {font_size}")
            text_obj = arcade.Text(
                text,
                x,
                y,
                color,
                font_size,
                anchor_x=anchor_x,
                anchor_y=anchor_y
            )
            print(f"[TEXT_FACTORY] Positioned text created successfully")
            return text_obj
        except Exception as e:
            print(f"[TEXT_FACTORY] Error creating positioned text: {e}")
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback
    
    @staticmethod
    def create_ui_text(
        text: str,
        x: int = 10,
        y: int = WINDOW_HEIGHT - 50,
        color = arcade.color.WHITE,
        font_size: int = 16
    ) -> arcade.Text:
        """Create a UI text object for overlays"""
        try:
            print(f"[TEXT_FACTORY] Creating UI text: '{text}' at ({x}, {y})")
            print(f"[TEXT_FACTORY] Color: {color}, Font size: {font_size}")
            text_obj = arcade.Text(text, x, y, color, font_size)
            print(f"[TEXT_FACTORY] UI text created successfully")
            return text_obj
        except Exception as e:
            print(f"[TEXT_FACTORY] Error creating UI text: {e}")
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            return fallback 