import arcade
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.fading_view import FadingView


class EndView(FadingView):
    """End screen shown when the player wins the game"""
    
    def __init__(self):
        super().__init__()
        self.title_text = arcade.Text(
            "CONGRATULATIONS!",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 100,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            anchor_y="center"
        )
        self.subtitle_text = arcade.Text(
            "You have successfully completed all 3 levels!",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 50,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        self.stats_text = arcade.Text(
            "All cars have been repaired and you've escaped the zombie apocalypse!",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            arcade.color.LIGHT_BLUE,
            20,
            anchor_x="center",
            anchor_y="center"
        )
        self.instruction_text = arcade.Text(
            "Press SPACE to return to main menu",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 50,
            arcade.color.YELLOW,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        self.credits_text = arcade.Text(
            "Thanks for playing!",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 100,
            arcade.color.GREEN,
            18,
            anchor_x="center",
            anchor_y="center"
        )

    def on_draw(self):
        """Render the end screen"""
        self.clear()
        
        # Draw background
        arcade.draw_lrbt_rectangle_filled(
            0,
            WINDOW_WIDTH,
            0,
            WINDOW_HEIGHT,
            arcade.color.DARK_GREEN
        )
        
        # Draw texts
        self.title_text.draw()
        self.subtitle_text.draw()
        self.stats_text.draw()
        self.instruction_text.draw()
        self.credits_text.draw()

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.SPACE:
            # Return to main menu
            from src.views.menu_view import MenuView
            menu_view = MenuView()
            self.window.show_view(menu_view) 