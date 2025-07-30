import arcade
from src.views.base_view import BaseView


class TransitionView(BaseView):
    """Transition screen shown when moving to the next map"""
    
    def __init__(self, next_map_index: int, total_maps: int = 3, previous_game_view=None):
        print(f"[TRANSITION_VIEW] Initializing TransitionView with map_index: {next_map_index}")
        super().__init__()
        self.next_map_index = next_map_index
        self.total_maps = total_maps
        self.previous_game_view = previous_game_view
        
        # Set background color for better visibility
        self.background_color = arcade.color.DARK_BLUE
        print(f"[TRANSITION_VIEW] Set background_color to: {self.background_color}")
        
        # Create text objects using the factory with better colors
        print(f"[TRANSITION_VIEW] Creating text objects...")
        self.transition_text = self.add_centered_text(
            f"Moving to Map {next_map_index}",
            y_offset=50,
            color=arcade.color.WHITE,
            font_size=32
        )
        self.instruction_text = self.add_centered_text(
            "Press SPACE to continue",
            y_offset=-50,
            color=arcade.color.YELLOW,
            font_size=24
        )
        self.progress_text = self.add_centered_text(
            f"Progress: {next_map_index - 1}/{total_maps} → {next_map_index}/{total_maps}",
            y_offset=-100,
            color=arcade.color.LIGHT_CYAN,
            font_size=18
        )
        print(f"[TRANSITION_VIEW] TransitionView initialization complete")

    def on_draw(self):
        """Override on_draw to add specific logging"""
        print(f"[TRANSITION_VIEW] on_draw called for TransitionView")
        print(f"[TRANSITION_VIEW] Background color: {self.background_color}")
        print(f"[TRANSITION_VIEW] Number of text objects: {len(self.text_objects)}")
        super().on_draw()
        print(f"[TRANSITION_VIEW] on_draw completed for TransitionView")

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
                # Fallback: create new GameView using direct import
                print(f"[TRANSITION] No previous GameView, creating new one")
                from src.views.game_view import GameView
                game_view = GameView()
                game_view.current_map_index = self.next_map_index
                print(f"[TRANSITION] Created new GameView with map index: {game_view.current_map_index}")
                game_view.setup()
                print(f"[TRANSITION] GameView setup complete, showing view")
                self.window.show_view(game_view) 