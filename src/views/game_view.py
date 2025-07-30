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
from src.sprites.car import Car
from src.debug import Debug
from src.entities.entity import Entity, EntityState
from src.sprites.bullet import Bullet
from src.sprites.indicator_bar import IndicatorBar
from src.entities.player import Player, WeaponType
from src.entities.zombie import Zombie
from src.managers.manager_factory import ManagerFactory
import threading
# Import constants
from src.constants import *

from src.constants import WINDOW_HEIGHT, WINDOW_WIDTH
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

        self.current_map_index = 1

        # Initialize managers using factory
        managers = ManagerFactory.create_managers(self)
        ManagerFactory.setup_managers(managers, self)

        self.gun_shot_sound = arcade.load_sound(
            "resources/sound/weapon/Desert Eagle/gun_rifle_pistol.wav"
        )
        self.bullet_list = arcade.SpriteList()
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        self.game_paused = True

        self.pathfind_barrier = None
        self.pathfind_barrier_thread_lock = threading.Lock()

        self.preload_resources()
        self.create_scene(self.scene)
        
        # Reset input keys for initial setup
        self.input_manager.reset_keys()
        self.ui_manager.reset_ui()

    def preload_resources(self):
        Entity.load_animations(character_preset="Man", character_config_path=PLAYER_CONFIG_FILE, game_view=self)
        Entity.load_animations(character_preset="Army_zombie", character_config_path=ZOMBIE_CONFIG_FILE, game_view=self)

    def reset(self):
        self.enemies.clear()
        self.bullet_list.clear()
        if "Enemies" not in self.scene._name_mapping:
            self.scene.add_sprite_list("Enemies", self.enemies)
        else:
            self.scene.get_sprite_list("Enemies").clear()
            self.scene.get_sprite_list("Enemies").extend(self.enemies)
        
        self.player.reset()
        self.scene.add_sprite("Player", self.player)

        # Spawn zombies
        for _ in range(10):
            zombie = Zombie(
                game_view=self,
                zombie_type="Army_zombie",
                player_ref=self.player,
            )
            zombie.spawn_random_position()

        self.player.current_health = self.player.max_health
        if self.player.health_bar:
            self.player.health_bar.fullness = 1.0

    def setup(self):
        self.reset()
        for thread in self.threads:
            thread.join()

        self.game_paused = False

    def create_scene(self, scene: arcade.Scene):
        """Set up the game and initialize the variables."""

        # Load the Tiled map
        map_name = f"resources/maps/map{self.current_map_index}.tmx"

        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        # Add the ground layers to the scene (in drawing order from bottom to top)
        
        for layer_name in ("Dirt", "Grass", "Road"):
            scene.add_sprite_list(layer_name, sprite_list=self.tile_map.sprite_lists[layer_name])
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        # Add the walls layer to the scene for collision
        scene.add_sprite_list(
            "Walls", sprite_list=self.wall_list
        )
        
        self.camera_manager.setup_camera_bounds(self.tile_map)

        # Set up the player info
        self.player = Player(
            game_view=self,
            scale=CHARACTER_SCALING,
            speed=PLAYER_MOVEMENT_SPEED,
            sound_set={
                "gun_shot": "resources/sound/weapon/gun/Isolated/5.56/WAV/556 Single Isolated WAV.wav"
            }
        )

        def create_pathfind_barrier():
            with self.pathfind_barrier_thread_lock:
                if self.pathfind_barrier is None:
                    self.pathfind_barrier = arcade.AStarBarrierList(
                        moving_sprite=self.player,
                        blocking_sprites=self.wall_list,
                        grid_size=30,
                        left=0,
                        right=MAP_WIDTH_PIXEL,
                        bottom=0,
                        top=MAP_HEIGHT_PIXEL,
                    )
        
        self._start_thread(create_pathfind_barrier)

        # Add sprite lists for Player and Enemies (drawn on top)
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("CarsLayer")
        
        # Load car positions from Tiled map
        self.car_manager.load_cars_from_map()

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
        self.car_manager.handle_car_interaction()

    def transition_to_next_map(self):
        """Transition to the next map"""
        self.current_map_index += 1
        
        if self.current_map_index > 3:
            from src.views.end_view import EndView
            end_view = EndView()
            self.window.show_view(end_view)
            return
            
        # Show transition screen
        from src.views.transition_view import TransitionView
        transition_view = TransitionView(self.current_map_index, 3, previous_game_view=self)
        self.window.show_view(transition_view)
        
    def load_map(self, map_index):
        """Load a specific map by index"""
        print(f"[MAP] ===== LOAD_MAP CALLED with map_index: {map_index} =====")
        map_name = f"resources/maps/map{map_index}.tmx"
        print(f"[MAP] Map file: {map_name}")
        
        # Clear health bars from previous map
        print(f"[MAP] Clearing {len(self.bar_list)} health bars")
        self.bar_list.clear()
        
        # Load new tile map
        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)
        print(f"[MAP] Tilemap loaded successfully")
        
        # Create new scene
        self.scene = arcade.Scene()
        print(f"[MAP] New scene created")
        
        # Recreate scene with new map
        self.create_scene(self.scene)
        print(f"[MAP] Scene recreated with new map")
        
        # Reset player using built-in reset function
        self.player.reset()
        print(f"[MAP] Player reset")
        
        # Clear and respawn enemies
        print(f"[MAP] Clearing {len(self.enemies)} enemies")
        for enemy in self.enemies:
            enemy.cleanup()
        self.enemies.clear()
        self.reset()

        # Reset player position to old car position
        self.car_manager.position_player_at_old_car()
        print(f"[MAP] Enemies cleared and respawned")
        
        # Reset car parts for new level
        self.car_manager.reset_car_parts()
        
        # Reset input keys to prevent lingering inputs
        self.input_manager.reset_keys()
        
        # Reset UI elements for new map
        self.ui_manager.reset_ui()
        
        print(f"[MAP] Map {map_index} loaded successfully")

    def draw_ui(self):
        """Draw UI elements including car interaction prompts."""
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

        super().on_update(delta_time) # Call FadingView's on_update

        self.center_camera_to_player(delta_time)

        # Update mouse position
        self.input_manager.update_mouse_position()

        self.update_player_speed()

        self.player.update(delta_time)
        Debug.update("Delta Time", f"{delta_time:.2f}")

        self.enemies.update(delta_time)

        # Check car interactions
        self.check_car_interactions()

        self.camera_manager.update_zoom(delta_time)

        self.bullet_list.update(
            delta_time, [self.scene.get_sprite_list("Enemies")], [self.wall_list]
        )

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