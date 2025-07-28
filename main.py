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


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()

        Debug._initialize()

        self.window.background_color = arcade.color.AMAZON

        # Camera for scrolling
        self.camera = arcade.Camera2D()
        self.camera_bounds = self.window.rect
        self.target_zoom = 1.0

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = arcade.Camera2D()

        self.scene = self.create_scene()

        # Create a sprite list for health bars
        self.bar_list = arcade.SpriteList()

        # Set up the player info
        self.player = Player(
            game_view=self,
            scale=CHARACTER_SCALING,
            speed=PLAYER_MOVEMENT_SPEED,
            sound_set={
                "gun_shot": "resources/sound/weapon/gun/Isolated/5.56/WAV/556 Single Isolated WAV.wav"
            }
        )

        # Enemy list
        self.enemies = arcade.SpriteList()

        # Track the current state of what key is pressed
        self.key_down = {
            LEFT_KEY: False,
            RIGHT_KEY: False,
            UP_KEY: False,
            DOWN_KEY: False,
            A_KEY: False,
            D_KEY: False,
            W_KEY: False,
            S_KEY: False,
        }

        # Mouse position tracking
        self.mouse_offset = Vec2(0, 0)
        self.mouse_position = Vec2(0, 0)
        self.left_mouse_pressed = False

        self.gun_shot_sound = arcade.load_sound(
            "resources/sound/weapon/Desert Eagle/gun_rifle_pistol.wav"
        )
        self.bullet_list = arcade.SpriteList()
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        self.reset()

    def reset(self):
        self.scene = self.create_scene()

        self.enemies.clear()
        self.bullet_list.clear()
        self.scene.add_sprite_list("Enemies", self.enemies)

        self.player.reset()
        self.scene.add_sprite("Player", self.player)

        

        # Add a test zombie
        for i in range(10):
            zombie = Zombie(
                game_view=self,
                zombie_type="Army_zombie",
                player_ref=self.player,
            )

            zombie.spawn_random_position()
            # zombie.position = (1000, 500)

        self.player.current_health = self.player.max_health
        self.player.health_bar.fullness = 1.0


    def create_scene(self) -> arcade.Scene:
        """Set up the game and initialize the variables."""
        scene = arcade.Scene()

        # Load the Tiled map
        map_name = "resources/maps/Map1.tmx"
        self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        # Add the ground layers to the scene (in drawing order from bottom to top)
        scene.add_sprite_list(
            "Dirt", sprite_list=self.tile_map.sprite_lists["Dirt"]
        )
        scene.add_sprite_list(
            "Grass", sprite_list=self.tile_map.sprite_lists["Grass"]
        )
        scene.add_sprite_list(
            "Road", sprite_list=self.tile_map.sprite_lists["Road"]
        )
        self.wall_list = self.tile_map.sprite_lists["Walls"]
        # Add the walls layer to the scene for collision
        scene.add_sprite_list(
            "Walls", sprite_list=self.wall_list
        )

        self.camera_bounds = arcade.LRBT(
            self.window.width/2.0,
            self.tile_map.width * TILE_SIZE * TILE_SCALING - self.window.width/2.0,
            self.window.height/2.0,
            self.tile_map.height * TILE_SIZE * TILE_SCALING
        )

        # Add sprite lists for Player and Enemies (drawn on top)
        scene.add_sprite_list("Enemies")
        scene.add_sprite_list("Player")

        return scene

    def on_draw(self):
        """Render the screen."""

        # Disable CRT filter - render directly to window
        self.clear()

        with self.camera.activate():
            self.scene.draw()
            self.bullet_list.draw()
            self.bar_list.draw()

        with self.camera_gui.activate():
            Debug.render(10, 10)

        for enemy in self.enemies:
            enemy.draw()
        

    def update_player_speed(self):
        # Calculate speed based on the keys pressed

        movement_x = 0
        movement_y = 0
        
        if self.key_down.get(LEFT_KEY) or self.key_down.get(A_KEY):
            movement_x += -1
        if self.key_down.get(RIGHT_KEY) or self.key_down.get(D_KEY):
            movement_x += 1
            
        if self.key_down.get(UP_KEY) or self.key_down.get(W_KEY):
            movement_y += 1
        if self.key_down.get(DOWN_KEY) or self.key_down.get(S_KEY):
            movement_y += -1

        self.player.move(Vec2(movement_x, movement_y))

    def switch_weapon(self, key):
        match key:
            case arcade.key.KEY_1:
                self.player.set_weapon(WeaponType.GUN)
            case arcade.key.KEY_2:
                self.player.set_weapon(WeaponType.BAT)
            case arcade.key.KEY_3:
                self.player.set_weapon(WeaponType.KNIFE)
            case arcade.key.KEY_4:
                self.player.set_weapon(WeaponType.RIFLE)
            case arcade.key.KEY_5:
                self.player.set_weapon(WeaponType.FLAMETHROWER)

    def on_key_press(self, key, modifiers):
        self.key_down[key] = True

        # Toggle fullscreen with F11
        if key == FULLSCREEN_KEY:
            self.window.set_fullscreen(not self.window.fullscreen)
            # Update camera when toggling fullscreen
            self.on_resize(self.window.width, self.window.height)

        # Weapon switching with number keys
        self.switch_weapon(key)

        # Attack with space
        if key == arcade.key.SPACE:
            self.player.attack()

        # Death animation with K (for testing)
        if key == arcade.key.K:
            self.player.die()

        # Reset game with R key
        if key == arcade.key.R:
            self.reset()

        # Zoom functionality with LCTRL
        if key == arcade.key.LCTRL:
            self.target_zoom = MIN_ZOOM

    def on_key_release(self, key, modifiers):
        self.key_down[key] = False

        if key == ZOOM_KEY:
            self.target_zoom = 1.0

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement"""
        # Convert screen coordinates to world coordinates
        offset_x = (x - WINDOW_WIDTH / 2) / self.camera.zoom
        offset_y = (y - WINDOW_HEIGHT / 2) / self.camera.zoom
        self.mouse_offset = (offset_x, offset_y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = True
            self.player.attack()

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = False

    def center_camera_to_player(self, delta_time):
        current_camera_position = Vec2(
            self.camera.position[0], self.camera.position[1]
        )
        player_position_vec = Vec2(
            self.player.position[0], self.player.position[1]
        )

        new_camera_position_vec = arcade.math.smerp_2d(
            current_camera_position,
            player_position_vec,
            delta_time,
            FOLLOW_DECAY_CONST,
        )
        self.camera.position = (
            new_camera_position_vec.x,
            new_camera_position_vec.y,
        )

        # Constrain the camera's position to the camera bounds.
        self.camera.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )

    def on_update(self, delta_time):
        self.center_camera_to_player(delta_time)
        

        # debug deltatime
        self.mouse_position = (
            self.mouse_offset[0] + self.camera.position[0],
            self.mouse_offset[1] + self.camera.position[1],
        )
        self.player.mouse_position = self.mouse_position

        self.update_player_speed()

        self.player.update(delta_time)
        Debug.update("Delta Time", f"{delta_time:.2f}")

        self.enemies.update(delta_time)

        if abs(self.camera.zoom - self.target_zoom) > 0.001:
            self.camera.zoom = arcade.math.lerp(
                self.camera.zoom, self.target_zoom, 5 * delta_time
            )
            Debug.update("Camera Zoom", f"{self.camera.zoom:.2f}")


        self.bullet_list.update(
            delta_time, [self.scene.get_sprite_list("Enemies")], [self.wall_list]
        )

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        self.camera.match_window()
        self.camera_gui.match_window(position=True)

        display_width, display_height = arcade.get_display_size()

        if width == display_width and height == display_height:
            self.window.set_fullscreen(True)
        elif self.window.fullscreen and (
            width < display_width or height < display_height
        ):
            self.window.set_fullscreen(False)


class Window(arcade.Window):

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        self.camera.match_window()
        self.camera_gui.match_window(position=True)
        print(f"Window resized to {width}x{height}")

def main():
    """Main function"""
    window = Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE,
        update_rate=WINDOW_RATE,
        draw_rate=WINDOW_RATE,
        resizable=True,
    )
    game = GameView()
    window.camera = game.camera
    window.camera_gui = game.camera_gui

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
