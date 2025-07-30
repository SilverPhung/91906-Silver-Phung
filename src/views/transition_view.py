import arcade
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.views.fading_view import FadingView


class TransitionView(FadingView):
    """Transition screen shown when moving to the next map"""
    
    def __init__(self, next_map_index: int, total_maps: int = 3, previous_game_view=None):
        super().__init__()
        self.next_map_index = next_map_index
        self.total_maps = total_maps
        self.previous_game_view = previous_game_view
        self.transition_text = arcade.Text(
            f"Moving to Map {next_map_index}",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 50,
            arcade.color.WHITE,
            32,
            anchor_x="center",
            anchor_y="center"
        )
        self.instruction_text = arcade.Text(
            "Press SPACE to continue",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 50,
            arcade.color.YELLOW,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        self.progress_text = arcade.Text(
            f"Progress: {next_map_index - 1}/{total_maps} → {next_map_index}/{total_maps}",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 100,
            arcade.color.CYAN,
            18,
            anchor_x="center",
            anchor_y="center"
        )

    def on_draw(self):
        """Render the transition screen"""
        self.clear()
        
        # Draw background
        arcade.draw_lrbt_rectangle_filled(
            0,
            WINDOW_WIDTH,
            0,
            WINDOW_HEIGHT,
            arcade.color.BLACK
        )
        
        # Draw texts
        self.transition_text.draw()
        self.instruction_text.draw()
        self.progress_text.draw()

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.SPACE:
            print(f"[TRANSITION] Space pressed, transitioning to map {self.next_map_index}")
            
            if self.previous_game_view:
                # Use existing GameView and call load_map
                print(f"[TRANSITION] Using existing GameView, calling load_map({self.next_map_index})")
                self.previous_game_view.load_map(self.next_map_index)
                print(f"[TRANSITION] load_map complete, showing existing GameView")
                self.window.show_view(self.previous_game_view)
            else:
                # Fallback: create new GameView (shouldn't happen)
                print(f"[TRANSITION] No previous GameView, creating new one")
                from src.views.game_view import GameView
                game_view = GameView()
                game_view.current_map_index = self.next_map_index
                print(f"[TRANSITION] Created new GameView with map index: {game_view.current_map_index}")
                game_view.setup()
                print(f"[TRANSITION] GameView setup complete, showing view")
                self.window.show_view(game_view) 