import arcade
from pyglet.math import Vec2
from src.constants import (
    LEFT_KEY, RIGHT_KEY, UP_KEY, DOWN_KEY,
    A_KEY, D_KEY, W_KEY, S_KEY,
    FULLSCREEN_KEY, MIN_ZOOM
)
from src.entities.player import WeaponType


class InputManager:
    """Manages all input handling including keyboard and mouse events."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # Track the current state of what key is pressed
        movement_keys = [LEFT_KEY, RIGHT_KEY, UP_KEY, DOWN_KEY, A_KEY, D_KEY, W_KEY, S_KEY]
        self.key_down = {key: False for key in movement_keys}
        
        # Mouse position tracking
        self.mouse_offset = Vec2(0, 0)
        self.mouse_position = Vec2(0, 0)
        self.left_mouse_pressed = False
        
        # Key action mapping
        self.key_actions = {
            FULLSCREEN_KEY: self._toggle_fullscreen,
            arcade.key.SPACE: self._attack,
            arcade.key.K: self._die,
            arcade.key.R: self._reset,
            arcade.key.E: self._handle_car_interaction,
            arcade.key.P: self._add_test_car_part,
            arcade.key.LCTRL: self._zoom_in,
        }
        
        # Weapon switching mapping
        self.weapon_map = {
            arcade.key.KEY_1: WeaponType.GUN,
            arcade.key.KEY_2: WeaponType.BAT,
            arcade.key.KEY_3: WeaponType.KNIFE,
            arcade.key.KEY_4: WeaponType.RIFLE,
            arcade.key.KEY_5: WeaponType.FLAMETHROWER,
        }

    def update_player_speed(self):
        """Calculate movement based on pressed keys."""
        movement_x = sum([
            -1 if self.key_down.get(LEFT_KEY) or self.key_down.get(A_KEY) else 0,
            1 if self.key_down.get(RIGHT_KEY) or self.key_down.get(D_KEY) else 0
        ])
        movement_y = sum([
            1 if self.key_down.get(UP_KEY) or self.key_down.get(W_KEY) else 0,
            -1 if self.key_down.get(DOWN_KEY) or self.key_down.get(S_KEY) else 0
        ])
        
        self.game_view.player.move(Vec2(movement_x, movement_y))

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        self.key_down[key] = True

        # Execute action if key is mapped
        if key in self.key_actions:
            self.key_actions[key]()
        else:
            # Handle weapon switching
            self._switch_weapon(key)

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        self.key_down[key] = False
        
        if key == arcade.key.Z:
            self.game_view.target_zoom = 1.0

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement."""
        from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
        
        # Convert screen coordinates to world coordinates
        offset_x = (x - WINDOW_WIDTH / 2) / self.game_view.camera.zoom
        offset_y = (y - WINDOW_HEIGHT / 2) / self.game_view.camera.zoom
        self.mouse_offset = (offset_x, offset_y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = True
            self.game_view.player.attack()

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = False

    def _switch_weapon(self, key):
        """Switch weapon based on number key pressed."""
        if key in self.weapon_map:
            self.game_view.player.set_weapon(self.weapon_map[key])

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode and update camera."""
        self.game_view.window.set_fullscreen(not self.game_view.window.fullscreen)
        self.game_view.on_resize(self.game_view.window.width, self.game_view.window.height)

    def _attack(self):
        """Trigger player attack."""
        self.game_view.player.attack()

    def _die(self):
        """Trigger player death animation."""
        self.game_view.player.die()

    def _reset(self):
        """Reset the game."""
        self.game_view.reset()

    def _handle_car_interaction(self):
        """Handle car interaction."""
        self.game_view.handle_car_interaction()

    def _add_test_car_part(self):
        """Add a car part for testing purposes."""
        if self.game_view.new_car:
            self.game_view.new_car.add_part()
            print(f"[PARTS] Added car part! Now have {self.game_view.new_car.get_parts_status()}")
        else:
            print("[PARTS] No new car found to add parts to")

    def _zoom_in(self):
        """Zoom in with left control."""
        self.game_view.target_zoom = MIN_ZOOM

    def update_mouse_position(self):
        """Update mouse position for the game view."""
        self.game_view.mouse_position = (
            self.mouse_offset[0] + self.game_view.camera.position[0],
            self.mouse_offset[1] + self.game_view.camera.position[1],
        )
        self.game_view.player.mouse_position = self.game_view.mouse_position

    def reset_keys(self):
        """Reset all key states to prevent lingering inputs."""
        for key in self.key_down:
            self.key_down[key] = False
        self.left_mouse_pressed = False
        print("[INPUT] All keys reset for new map") 