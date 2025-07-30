from src.views.menu_view import MenuView
from src.views.end_view import EndView
from src.views.game_over_view import GameOverView
from src.views.transition_view import TransitionView


class ViewFactory:
    """Factory class for creating views"""
    
    @staticmethod
    def create_menu_view():
        """Create a menu view"""
        try:
            return MenuView()
        except Exception as e:
            print(f"Error creating menu view: {e}")
            # Return a basic view as fallback
            from src.views.base_view import BaseView
            return BaseView()
    
    @staticmethod
    def create_game_view():
        """Create a game view"""
        try:
            # Use dynamic import to avoid circular dependency
            from src.views.game_view import GameView
            return GameView()
        except Exception as e:
            print(f"Error creating game view: {e}")
            # Return a basic view as fallback
            from src.views.base_view import BaseView
            return BaseView()
    
    @staticmethod
    def create_end_view():
        """Create an end view"""
        try:
            return EndView()
        except Exception as e:
            print(f"Error creating end view: {e}")
            # Return a basic view as fallback
            from src.views.base_view import BaseView
            return BaseView()
    
    @staticmethod
    def create_game_over_view():
        """Create a game over view"""
        try:
            return GameOverView()
        except Exception as e:
            print(f"Error creating game over view: {e}")
            # Return a basic view as fallback
            from src.views.base_view import BaseView
            return BaseView()
    
    @staticmethod
    def create_transition_view(next_map_index: int, total_maps: int = 3, previous_game_view=None):
        """Create a transition view"""
        try:
            return TransitionView(next_map_index, total_maps, previous_game_view)
        except Exception as e:
            print(f"Error creating transition view: {e}")
            # Return a basic view as fallback
            from src.views.base_view import BaseView
            return BaseView() 