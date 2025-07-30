"""
Managers package for game components.

This package contains manager classes that handle specific aspects of the game,
following the component principle and DRY (Don't Repeat Yourself) principle.
"""

from .input_manager import InputManager
from .ui_manager import UIManager
from .car_manager import CarManager
from .camera_manager import CameraManager

__all__ = ['InputManager', 'UIManager', 'CarManager', 'CameraManager'] 