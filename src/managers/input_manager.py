import arcade
from pyglet.math import Vec2
from src.constants import (
    LEFT_KEY, RIGHT_KEY, UP_KEY, DOWN_KEY,
    A_KEY, D_KEY, W_KEY, S_KEY,
    FULLSCREEN_KEY, MIN_ZOOM, ENABLE_TESTING
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
            # arcade.key.R: self._reset,  # Temporarily disabled for testing
            arcade.key.E: self._handle_interaction,
            arcade.key.P: self._add_test_car_part,
            arcade.key.LCTRL: self._zoom_in,
        }
        
        # Testing key actions (only when testing is enabled)
        if ENABLE_TESTING:
            self.testing_key_actions = {
                arcade.key.F1: self._run_movement_tests,
                arcade.key.F2: self._run_combat_tests,
                arcade.key.F3: self._run_car_tests,
                arcade.key.F4: self._run_health_tests,
                arcade.key.F5: self._run_all_tests,
                arcade.key.F6: self._show_test_results,
                arcade.key.R: self._run_all_tests,  # R key for running all tests
            }
        else:
            self.testing_key_actions = {}
        
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
        
        # Debug: Log all key presses
        print(f"[INPUT] Key pressed: {key} (E key is {arcade.key.E})")

        # Execute testing action if key is mapped and testing is enabled
        if key in self.testing_key_actions:
            print(f"[INPUT] Executing testing action for key {key}")
            self.testing_key_actions[key]()
        # Execute regular action if key is mapped
        elif key in self.key_actions:
            print(f"[INPUT] Executing regular action for key {key}")
            self.key_actions[key]()
        else:
            # Handle weapon switching
            self._switch_weapon(key)

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        self.key_down[key] = False
        
        if key == arcade.key.Z:
            self.game_view.camera_manager.set_target_zoom(1.0)
        elif key == arcade.key.LCTRL:
            self.game_view.camera_manager.set_target_zoom(1.0)

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement."""
        from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
        
        # Convert screen coordinates to world coordinates
        camera = self.game_view.camera_manager.get_camera()
        offset_x = (x - WINDOW_WIDTH / 2) / camera.zoom
        offset_y = (y - WINDOW_HEIGHT / 2) / camera.zoom
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
        print("[INPUT] Reset triggered - this should be disabled for testing")
        self.game_view.reset()

    def _handle_car_interaction(self):
        """Handle car interaction."""
        self.game_view.handle_car_interaction()

    def _handle_interaction(self):
        """
        Handle interaction with E key - prioritizes car over chest.
        
        Car interaction takes precedence over chest interaction.
        """
        print("[INPUT] ===== E KEY PRESSED =====")
        print(f"[INPUT] Car manager near_car: {self.game_view.car_manager.near_car}")
        print(f"[INPUT] Chest manager near_chest: {self.game_view.chest_manager.near_chest}")
        
        # First try car interaction
        if self.game_view.car_manager.near_car:
            print("[INPUT] Car nearby - handling car interaction")
            self.game_view.handle_car_interaction()
        # If no car nearby, try chest interaction
        elif self.game_view.chest_manager.near_chest:
            print("[INPUT] Chest nearby - handling chest interaction")
            self.game_view.handle_chest_interaction()
        else:
            print("[INPUT] No interactable objects nearby")
            print(f"[INPUT] Total chests: {len(self.game_view.chest_manager.chests_with_parts) + len(self.game_view.chest_manager.chests_without_parts)}")
        print("[INPUT] =========================")

    def _add_test_car_part(self):
        """Add a car part for testing purposes."""
        self.game_view.car_manager.add_test_car_part()

    def _zoom_in(self):
        """Zoom in with left control."""
        self.game_view.camera_manager.set_target_zoom(MIN_ZOOM)

    def update_mouse_position(self):
        """Update mouse position for the game view."""
        camera = self.game_view.camera_manager.get_camera()
        self.game_view.mouse_position = (
            self.mouse_offset[0] + camera.position[0],
            self.mouse_offset[1] + camera.position[1],
        )
        self.game_view.player.mouse_position = self.game_view.mouse_position

    def reset_keys(self):
        """Reset all key states to prevent lingering inputs."""
        for key in self.key_down:
            self.key_down[key] = False
        self.left_mouse_pressed = False
        print("[INPUT] All keys reset for new map")
    
    # === Testing Methods ===
    
    def _run_movement_tests(self):
        """Run movement tests."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F1 pressed - running movement tests")
            results = self.game_view.run_tests_for_objective("movement")
            if results:
                print(f"[TESTING] Movement tests completed: {results}")
    
    def _run_combat_tests(self):
        """Run combat tests."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F2 pressed - running combat tests")
            results = self.game_view.run_tests_for_objective("combat")
            if results:
                print(f"[TESTING] Combat tests completed: {results}")
    
    def _run_car_tests(self):
        """Run car interaction tests."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F3 pressed - running car interaction tests")
            results = self.game_view.run_tests_for_objective("car_interaction")
            if results:
                print(f"[TESTING] Car interaction tests completed: {results}")
    
    def _run_health_tests(self):
        """Run health system tests."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F4 pressed - running health system tests")
            results = self.game_view.run_tests_for_objective("health_system")
            if results:
                print(f"[TESTING] Health system tests completed: {results}")
    
    def _run_all_tests(self):
        """Run all tests."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F5 pressed - running all tests")
            results = self.game_view.run_all_tests()
            if results:
                print(f"[TESTING] All tests completed: {results}")
    
    def _show_test_results(self):
        """Show current test results."""
        if ENABLE_TESTING and hasattr(self.game_view, 'test_runner'):
            print("[TESTING] F6 pressed - showing test results")
            results = self.game_view.get_test_results()
            if results:
                print(f"[TESTING] Current test results: {results}")
            else:
                print("[TESTING] No test results available") 