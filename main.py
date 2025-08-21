import arcade

# Import refactored classes

# Import constants
from src.constants import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.views.view_factory import ViewFactory


def main():
    """Startup"""
    window = arcade.Window(
        WINDOW_WIDTH, WINDOW_HEIGHT, "Zombie Survival: Car Escape"
    )
    menu_view = ViewFactory.create_menu_view()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
