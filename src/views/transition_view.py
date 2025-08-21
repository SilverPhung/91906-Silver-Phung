import arcade
from src.views.base_view import BaseView


class TransitionView(BaseView):
    """Transition screen shown when moving to the next map"""

    def __init__(
        self, next_map_index: int, total_maps: int = 3, previous_game_view=None
    ):
        super().__init__()
        self.next_map_index = next_map_index
        self.total_maps = total_maps
        self.previous_game_view = previous_game_view

        # Set background color for better visibility
        self.background_color = arcade.color.DARK_BLUE

        # Create text objects using the factory with better colors
        self.transition_text = self.add_centered_text(
            f"Moving to Map {next_map_index}",
            y_offset=50,
            color=arcade.color.WHITE,
            font_size=32,
        )
        self.instruction_text = self.add_centered_text(
            "Press SPACE to continue",
            y_offset=-50,
            color=arcade.color.YELLOW,
            font_size=24,
        )
        self.progress_text = self.add_centered_text(
            f"Progress: {next_map_index - 1}/{total_maps} → {next_map_index}/{total_maps}",
            y_offset=-100,
            color=arcade.color.LIGHT_CYAN,
            font_size=18,
        )

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.SPACE:
            if self.previous_game_view:
                # Reset player velocity before transitioning to prevent momentum carry-over
                if (
                    hasattr(self.previous_game_view, "player")
                    and self.previous_game_view.player
                ):
                    self.previous_game_view.player.reset_velocity()

                # Use existing GameView and call load_map
                self.previous_game_view.reset_scene()
                self.previous_game_view.create_initial_scene()
                self.window.show_view(self.previous_game_view)
            else:
                # Fallback: create new GameView using direct import
                from src.views.game_view import GameView

                game_view = GameView()
                game_view.current_map_index = self.next_map_index
                game_view.setup()
                self.window.show_view(game_view)
