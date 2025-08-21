import arcade
from typing import Dict, Any

#  Import refactored classes
from src.debug import Debug
from src.entities.entity import Entity
from src.entities.player import Player
from src.managers.manager_factory import ManagerFactory
from src.managers.reset_coordinator import ResetCoordinator
import threading

# Import constants
from src.constants import (
    CHARACTER_SCALING,
    PLAYER_CONFIG_FILE,
    PLAYER_FRICTION,
    PLAYER_MOVEMENT_SPEED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    ZOMBIE_CONFIG_FILE,
)
from src.views.fading_view import FadingView


class GameView(FadingView):
    """Main application class."""

    def __init__(self):
        super().__init__()
        Debug._initialize()

        self.window.background_color = arcade.color.AMAZON
        self.threads = []

        # Camera is now managed by CameraManager
        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = arcade.Camera2D()
        self.scene = arcade.Scene()

        # Create a sprite list for health bars
        self.bar_list = arcade.SpriteList()

        # Enemy list
        self.enemies = arcade.SpriteList()

        # Initialize managers using factory
        managers = ManagerFactory.create_managers(self)
        ManagerFactory.setup_managers(managers, self)

        # Initialize testing manager
        from src.managers.testing_manager import TestingManager

        self.testing_manager = TestingManager()

        sound_path = "resources/sound/weapon/Desert Eagle/gun_rifle_pistol.wav"
        self.gun_shot_sound = arcade.load_sound(sound_path)
        self.bullet_list = arcade.SpriteList()
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        self.game_paused = True

        self.pathfind_barrier = None
        self.pathfind_barrier_thread_lock = threading.Lock()

        self.preload_resources()

        # Initialize reset coordinator BEFORE creating initial scene
        self.reset_coordinator = ResetCoordinator(self)
        self._register_resetable_components()

        self.create_initial_scene()

        # Reset input keys for initial setup
        self.input_manager.reset_keys()
        self.ui_manager.reset_ui()

    def preload_resources(self):
        Entity.load_animations(
            character_preset="Man",
            character_config_path=PLAYER_CONFIG_FILE,
            game_view=self,
        )
        Entity.load_animations(
            character_preset="Army_zombie",
            character_config_path=ZOMBIE_CONFIG_FILE,
            game_view=self,
        )

    def _register_resetable_components(self):
        """Register all resetable components with the coordinator."""

        # Register map-specific components
        if hasattr(self, "car_manager"):
            self.reset_coordinator.register_component(self.car_manager, "map")
        if hasattr(self, "chest_manager"):
            self.reset_coordinator.register_component(
                self.chest_manager, "map"
            )
        if hasattr(self, "input_manager"):
            self.reset_coordinator.register_component(
                self.input_manager, "map"
            )
        if hasattr(self, "ui_manager"):
            self.reset_coordinator.register_component(self.ui_manager, "map")
        if hasattr(self, "game_state_manager"):
            self.reset_coordinator.register_component(
                self.game_state_manager, "game"
            )

    def reset(self):
        """Reset the game state for the current map."""
        # Completely recreate scene
        self.scene = None
        self.scene = self.map_manager.create_scene()

        # Use new player reset methods for better asset optimization
        self.player.reset_position()
        self.player.reset_health()

        # Reset input keys to prevent lingering movement
        self.input_manager.reset_keys()
        print("[GAME_VIEW] Input keys reset")

        # Add player to scene first
        self.scene.add_sprite("Player", self.player)
        print(
            f"[GAME_VIEW] Player added to scene at "
            f"({self.player.center_x:.1f}, {self.player.center_y:.1f})"
        )

        # Don't run reset coordinator here - entities are already loaded by
        # MapManager
        # The reset coordinator was clearing entities that were just loaded
        print(
            "[GAME_VIEW] Skipping reset coordinator to preserve loaded "
            "entities"
        )

        # Debug: Final scene verification
        print("[GAME_VIEW] Final scene verification after reset:")
        for layer_name in ["Player", "CarsLayer", "ChestsLayer", "Enemies"]:
            sprite_list = self.scene.get_sprite_list(layer_name)
            if sprite_list:
                print(
                    f"[GAME_VIEW]   {layer_name}: {len(sprite_list)} sprites"
                )
            else:
                print(f"[GAME_VIEW]   {layer_name}: No sprite list found!")

    def setup(self):
        # Don't reset here - only reset when actually changing maps
        # self.reset()
        for thread in self.threads:
            thread.join()

        self.game_paused = False

    def reset_scene(self):
        """Reset the scene for the current map."""
        self.scene = None
        self.scene = self.map_manager.create_scene()

        self.bar_list.clear()

    def create_initial_scene(self):
        """Create the initial scene for the game."""

        # Load initial map
        if not self.map_manager.load_map(self.map_manager.current_map_index):
            return

        # Create scene
        self.scene = self.map_manager.create_scene()

        # Create player
        sound_set = {
            "gun_shot": (
                "resources/sound/weapon/gun/Isolated/5.56/WAV/"
                "556 Single Isolated WAV.wav"
            )
        }

        self.player = Player(
            game_view=self,
            player_preset="Man",
            config_file=PLAYER_CONFIG_FILE,
            scale=CHARACTER_SCALING,
            friction=PLAYER_FRICTION,
            speed=PLAYER_MOVEMENT_SPEED,
            sound_set=sound_set,
        )

        # Set up camera bounds
        self.map_manager.setup_camera_bounds()

        # Create pathfinding barrier
        self.map_manager.create_pathfinding_barrier()

        # Set up managers for initial scene (this will position the player)
        self.map_manager.setup_managers_for_map()

        # Add player to scene
        self.scene.add_sprite("Player", self.player)
        print(
            f"[GAME_VIEW] Player added to scene at "
            f"({self.player.center_x:.1f}, {self.player.center_y:.1f})"
        )

        # Spawn zombies for initial scene
        self.map_manager.spawn_enemies_for_map()
        print("[GAME_VIEW] Zombies spawned for initial scene")

        # Don't run reset here - entities are already loaded properly
        # The reset was causing infinite loops and clearing entities
        print("[GAME_VIEW] Skipping initial reset to preserve loaded entities")

    def _start_thread(self, target_func):
        """Start a thread and add it to the threads list."""
        thread = threading.Thread(target=target_func)
        thread.start()
        self.threads.append(thread)

    def check_car_interactions(self):
        """Check if player is near any car and update interaction state"""
        self.car_manager.check_car_interactions()

    def handle_car_interaction(self):
        """Handle car interaction when E key is pressed"""
        print("[INTERACTION] Car interaction attempted")
        self.car_manager.handle_car_interaction()

    def check_chest_interactions(self):
        """Check if player is near any chest and update interaction state"""
        self.chest_manager.check_chest_interactions()

    def handle_chest_interaction(self):
        """Handle chest interaction when E key is pressed"""
        print("[INTERACTION] Chest interaction attempted")
        self.chest_manager.handle_chest_interaction()

    def transition_to_next_map(self):
        """Transition to the next map"""
        next_view = self.map_manager.transition_to_next_map()

        if next_view == "EndView":
            from src.views.end_view import EndView

            end_view = EndView()
            self.window.show_view(end_view)
            return
        elif next_view == "TransitionView":
            # Show transition screen
            from src.views.transition_view import TransitionView

            transition_view = TransitionView(
                self.map_manager.current_map_index, 3, previous_game_view=self
            )
            self.window.show_view(transition_view)

    def load_map(self, map_index):
        """Load a specific map by index using the MapManager"""
        print(f"[GAME_VIEW] Loading map {map_index} using MapManager...")

        # Use MapManager to load the complete map
        success = self.map_manager.load_complete_map(map_index)

        if success:
            # Update GameView references to use MapManager
            self.scene = self.map_manager.get_scene()
            self.tile_map = self.map_manager.get_tile_map()
            self.wall_list = self.map_manager.get_wall_list()

        return success

    def draw_ui(self):
        """Draw UI elements including car and chest interaction prompts."""
        self.ui_manager.draw_ui()

    def on_draw(self):
        """Render the screen."""

        # Disable CRT filter - render directly to window
        self.clear()

        with self.camera_manager.activate():
            self.scene.draw()
            self.bullet_list.draw()
            self.bar_list.draw()

        with self.camera_gui.activate():
            Debug.render(10, 10)
            self.draw_ui()

        for enemy in self.enemies:
            enemy.draw()

    def update_player_speed(self):
        """Calculate movement based on pressed keys."""
        self.input_manager.update_player_speed()

    def switch_weapon(self, key):
        """Switch weapon based on number key pressed."""
        self.input_manager._switch_weapon(key)

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        self.input_manager.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.input_manager.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement"""
        self.input_manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        self.input_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        self.input_manager.on_mouse_release(x, y, button, modifiers)

    def center_camera_to_player(self, delta_time):
        """Center camera on player - delegated to CameraManager."""
        self.camera_manager.center_camera_to_player(delta_time)

    def on_update(self, delta_time):
        if self.game_paused:
            return

        super().on_update(delta_time)  # Call FadingView's on_update

        self.center_camera_to_player(delta_time)

        # Update mouse position
        self.input_manager.update_mouse_position()

        self.update_player_speed()

        self.player.update(delta_time)
        Debug.update("Delta Time", f"{delta_time:.2f}")

        # Track player progression for testing
        if (
            hasattr(self, "testing_manager")
            and self.testing_manager.current_objective
        ):
            print(
                f"[PROGRESS] Player position: "
                f"({self.player.center_x:.1f}, {self.player.center_y:.1f})"
            )
            print(
                f"[PROGRESS] Player health: "
                f"{self.player.current_health}/{self.player.max_health}"
            )
            print(f"[PROGRESS] Enemies remaining: {len(self.enemies)}")

        self.enemies.update(delta_time)

        # Check car and chest interactions
        self.check_car_interactions()
        self.check_chest_interactions()

        self.camera_manager.update_zoom(delta_time)
        Debug.update(
            "Camera Zoom", f"{self.camera_manager.get_camera().zoom:.2f}"
        )

        # Get wall_list from MapManager
        wall_list = (
            self.map_manager.get_wall_list()
            if hasattr(self, "map_manager")
            else self.wall_list
        )
        self.bullet_list.update(
            delta_time, [self.scene.get_sprite_list("Enemies")], [wall_list]
        )

    def run_tests_for_objective(self, objective: str) -> Dict[str, Any]:
        """Run tests for a specific objective."""
        if hasattr(self, "testing_manager"):
            self.testing_manager.set_objective(objective)
            return self.testing_manager.run_all_tests(self)
        return {}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests."""
        if hasattr(self, "testing_manager"):
            return self.testing_manager.run_all_tests(self)
        return {}

    def get_test_results(self) -> Dict[str, Any]:
        """Get current test results."""
        if hasattr(self, "testing_manager"):
            return self.testing_manager.test_results
        return {}

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        self.camera_manager.match_window()
        self.camera_gui.match_window(position=True)

        display_width, display_height = arcade.get_display_size()

        if width == display_width and height == display_height:
            self.window.set_fullscreen(True)
        elif self.window.fullscreen and (
            width < display_width or height < display_height
        ):
            self.window.set_fullscreen(False)
