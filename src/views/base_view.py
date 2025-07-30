import arcade
from src.views.fading_view import FadingView
from src.utils.text_factory import TextFactory
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT


class BaseView(FadingView):
    """Base view class with common functionality for all views"""
    
    def __init__(self):
        super().__init__()
        self.text_objects = []
        self.background_color = arcade.color.BLACK
        print(f"[BASEVIEW] BaseView initialized with background_color: {self.background_color}")
        
    def add_centered_text(
        self,
        text: str,
        y_offset: int = 0,
        color = arcade.color.WHITE,
        font_size: int = 24
    ) -> arcade.Text:
        """Add a centered text object to this view"""
        try:
            print(f"[BASEVIEW] Adding centered text: '{text}' with color: {color}, font_size: {font_size}")
            text_obj = TextFactory.create_centered_text(
                text, y_offset, color, font_size
            )
            self.text_objects.append(text_obj)
            print(f"[BASEVIEW] Text object added successfully. Total text objects: {len(self.text_objects)}")
            return text_obj
        except Exception as e:
            print(f"[BASEVIEW] Error adding centered text to view: {e}")
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            self.text_objects.append(fallback)
            return fallback
    
    def add_positioned_text(
        self,
        text: str,
        x: int,
        y: int,
        color = arcade.color.WHITE,
        font_size: int = 24
    ) -> arcade.Text:
        """Add a positioned text object to this view"""
        try:
            print(f"[BASEVIEW] Adding positioned text: '{text}' at ({x}, {y}) with color: {color}")
            text_obj = TextFactory.create_positioned_text(
                text, x, y, color, font_size
            )
            self.text_objects.append(text_obj)
            print(f"[BASEVIEW] Positioned text object added successfully")
            return text_obj
        except Exception as e:
            print(f"[BASEVIEW] Error adding positioned text to view: {e}")
            # Return a fallback text object
            fallback = arcade.Text("Error", 0, 0, arcade.color.RED, 12)
            self.text_objects.append(fallback)
            return fallback
    
    def draw_background(self):
        """Draw the background for this view"""
        try:
            print(f"[BASEVIEW] Drawing background with color: {self.background_color}")
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, self.background_color
            )
            print(f"[BASEVIEW] Background drawn successfully")
        except Exception as e:
            print(f"[BASEVIEW] Error drawing background: {e}")
            # Fallback to black background
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, arcade.color.BLACK
            )
    
    def draw_texts(self):
        """Draw all text objects in this view"""
        try:
            print(f"[BASEVIEW] Drawing {len(self.text_objects)} text objects")
            for i, text_obj in enumerate(self.text_objects):
                print(f"[BASEVIEW] Drawing text object {i+1}: '{text_obj.text}' at ({text_obj.x}, {text_obj.y})")
                text_obj.draw()
            print(f"[BASEVIEW] All text objects drawn successfully")
        except Exception as e:
            print(f"[BASEVIEW] Error drawing texts: {e}")
    
    def on_draw(self):
        """Default draw implementation"""
        try:
            print(f"[BASEVIEW] on_draw called - clearing screen")
            self.clear()
            print(f"[BASEVIEW] Screen cleared, drawing background")
            self.draw_background()
            print(f"[BASEVIEW] Background drawn, drawing texts")
            self.draw_texts()
            print(f"[BASEVIEW] Texts drawn, drawing fading")
            self.draw_fading()
            print(f"[BASEVIEW] on_draw completed successfully")
        except Exception as e:
            print(f"[BASEVIEW] Error in view drawing: {e}")
            # Fallback drawing
            self.clear()
            arcade.draw_lrbt_rectangle_filled(
                0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, arcade.color.BLACK
            )
    
    def handle_space_key(self, key, modifiers):
        """Common space key handling for views"""
        try:
            if key == arcade.key.SPACE:
                print(f"[BASEVIEW] Space key pressed, setting fade_out to 0")
                self.fade_out = 0
                return True
            return False
        except Exception as e:
            print(f"[BASEVIEW] Error handling space key: {e}")
            return False 