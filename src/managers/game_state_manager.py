"""
Game State Manager for handling game progression and state tracking.

This module contains the GameStateManager class that handles all game state
tracking, progression logic, win/lose conditions, and game reset functionality.
"""

from typing import Optional, Dict, Any
from enum import Enum
from src.constants import MAX_HEALTH


class GameState(Enum):
    """Enumeration of possible game states."""
    PAUSED = "paused"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


class GameStateManager:
    """Manages game state tracking, progression logic, win/lose conditions, and game reset."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # Core game state
        self._state = GameState.PAUSED
        self._current_map_index = 1
        self._max_maps = 3
        
        # Game progression tracking
        self._player_health = MAX_HEALTH
        self._enemies_remaining = 0
        self._car_parts_collected = 0
        


    # === State Management ===
    
    @property
    def state(self) -> GameState:
        """Get the current game state."""
        return self._state
    
    @property
    def is_paused(self) -> bool:
        """Check if the game is currently paused."""
        return self._state == GameState.PAUSED
    
    @property
    def is_complete(self) -> bool:
        """Check if the game is complete (won or lost)."""
        return self._state in (GameState.WON, GameState.LOST)
    
    def pause(self):
        """Pause the game."""
        self._state = GameState.PAUSED
    
    def unpause(self):
        """Unpause the game."""
        self._state = GameState.PLAYING

    # === Map Management ===
    
    @property
    def current_map_index(self) -> int:
        """Get the current map index."""
        return self._current_map_index
    
    @property
    def max_maps(self) -> int:
        """Get the maximum number of maps."""
        return self._max_maps
    
    def set_map_index(self, map_index: int):
        """Set the current map index."""
        self._current_map_index = map_index
    
    def advance_map(self):
        """Advance to the next map and handle game completion."""
        self._current_map_index += 1
        
        if self._current_map_index > self._max_maps:
            self._complete_game()
        else:
            self._transition_to_next_map()

    # === Game Progression ===
    
    @property
    def player_health(self) -> int:
        """Get current player health."""
        return self._player_health
    
    @property
    def enemies_remaining(self) -> int:
        """Get count of remaining enemies."""
        return self._enemies_remaining
    
    @property
    def car_parts_collected(self) -> int:
        """Get count of car parts collected."""
        return self._car_parts_collected
    
    def update_player_health(self, health: int):
        """Update player health and check for death."""
        self._player_health = health
        self._check_lose_conditions()
    
    def update_enemies_remaining(self, count: int):
        """Update the count of remaining enemies."""
        self._enemies_remaining = count
    
    def update_car_parts_collected(self, count: int):
        """Update the count of car parts collected."""
        self._car_parts_collected = count
    
    def can_progress_to_next_map(self) -> bool:
        """Check if the player can progress to the next map."""
        if not self.game_view.car_manager.new_car:
            return False
        return self.game_view.car_manager.new_car.can_use()

    # === Win/Lose Conditions ===
    
    def check_win_conditions(self) -> bool:
        """Check if win conditions are met."""
        return self._current_map_index > self._max_maps
    
    def _check_lose_conditions(self):
        """Check if lose conditions are met and handle accordingly."""
        if self.game_view.player.current_health <= 0:
            self._handle_player_death()
    
    def _handle_player_death(self):
        """Handle player death."""
        self._state = GameState.LOST

        self._show_game_over_screen()

    # === Game Completion ===
    
    def _complete_game(self):
        """Handle game completion."""
        self._state = GameState.WON
        self._show_end_screen()
    
    def _transition_to_next_map(self):
        """Handle transition to the next map."""
        self._show_transition_screen()

    # === View Management (Abstraction) ===
    
    def _show_transition_screen(self):
        """Show transition screen (abstracted view creation)."""
        from src.views.transition_view import TransitionView
        transition_view = TransitionView(
            self._current_map_index, 
            self._max_maps, 
            previous_game_view=self.game_view
        )
        self.game_view.window.show_view(transition_view)
    
    def _show_end_screen(self):
        """Show end screen (abstracted view creation)."""
        from src.views.end_view import EndView
        end_view = EndView()
        self.game_view.window.show_view(end_view)
    
    def _show_game_over_screen(self):
        """Show game over screen (abstracted view creation)."""
        from src.views.game_over_view import GameOverView
        game_over_view = GameOverView()
        self.game_view.window.show_view(game_over_view)

    # === Reset Operations ===
    
    def reset_game(self):
        """Reset the game state for a new game."""
        self._reset_state()
        self._reset_progression()
    
    def reset_for_new_map(self):
        """Reset state for a new map while preserving progression."""
        self._state = GameState.PLAYING
        self._reset_progression()
    
    def _reset_state(self):
        """Reset game state variables."""
        self._state = GameState.PAUSED
        self._current_map_index = 1
    
    def _reset_progression(self):
        """Reset progression tracking variables."""
        self._player_health = MAX_HEALTH
        self._enemies_remaining = 0
        self._car_parts_collected = 0

    # === Progress Reporting ===
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current game progress information."""
        return {
            'current_map': self._current_map_index,
            'max_maps': self._max_maps,
            'player_health': self._player_health,
            'enemies_remaining': self._enemies_remaining,
            'car_parts_collected': self._car_parts_collected,
            'game_state': self._state.value,
            'is_complete': self.is_complete
        } 