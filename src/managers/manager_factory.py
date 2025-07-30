from src.managers.input_manager import InputManager
from src.managers.ui_manager import UIManager
from src.managers.car_manager import CarManager
from src.managers.camera_manager import CameraManager


class ManagerFactory:
    """Factory class for creating and managing game managers"""
    
    @staticmethod
    def create_managers(game_view):
        """Create all managers for the game view"""
        try:
            return {
                'input_manager': InputManager(game_view),
                'ui_manager': UIManager(game_view),
                'car_manager': CarManager(game_view),
                'camera_manager': CameraManager(game_view)
            }
        except Exception as e:
            print(f"Error creating managers: {e}")
            # Return empty dict as fallback
            return {}
    
    @staticmethod
    def setup_managers(managers, game_view):
        """Setup all managers with the game view"""
        try:
            for manager_name, manager in managers.items():
                setattr(game_view, manager_name, manager)
        except Exception as e:
            print(f"Error setting up managers: {e}")
            # Continue with partial setup if possible
            for manager_name, manager in managers.items():
                try:
                    setattr(game_view, manager_name, manager)
                except Exception as setup_error:
                    print(f"Error setting up {manager_name}: {setup_error}") 