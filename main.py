import arcade
from arcade.experimental.crt_filter import CRTFilter
from arcade.math import rotate_point
from arcade.texture.transforms import (
    Rotate180Transform,
    Transform,
    VertexOrder,
)
from arcade.types import Point2List
import random
from pyglet.math import Vec2, clamp
import time
import os
import asyncio
import math
import concurrent.futures

# Import refactored classes
from src.debug import Debug
from src.entities.entity import EntityState
from src.sprites.bullet import Bullet
from src.sprites.indicator_bar import IndicatorBar
from src.entities.player import Player, WeaponType
from src.entities.zombie import Zombie

# Import constants
from src.constants import *

from src.constants import WINDOW_HEIGHT, WINDOW_WIDTH
from src.views.view_factory import ViewFactory

def main():
    """Startup"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Different Views Minimal Example")
    menu_view = ViewFactory.create_menu_view()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
