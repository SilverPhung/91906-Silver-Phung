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
        self.loading_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4
        )
        self.loading_futures = []

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
            scale=CHARACTER_SCALING,
            speed=PLAYER_MOVEMENT_SPEED,
            show_health_indicator=self.bar_list,
        )
        self.player.load_animations()

        # Enemy list and physics engines - initialize before spawning enemies
        self.enemies = []
        self.enemy_physics_engines = []

        # Add a test zombie
        self.spawn_zombie("Army_zombie", x=400, y=350, player_ref=self.player)

        # Physics engines - one for player and one for each enemy
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Walls"),
        )

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

        self.reset()

    def reset(self):
        self.scene = self.create_scene()

        self.player.position = Vec2(50, 350)
        self.scene.add_sprite("Player", self.player)

        # Clear and recreate enemy lists
        self.enemies = []
        self.enemy_physics_engines = []

        # Add a test zombie
        zombie = self.spawn_zombie(
            "Army_zombie", x=400, y=350, player_ref=self.player
        )

        # Physics engine for player
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Walls"),
        )

        # Create physics engine for this enemy (after adding to scene)
        enemy_physics_engine = arcade.PhysicsEngineSimple(
            zombie,
            self.scene.get_sprite_list("Walls"),
        )
        self.enemy_physics_engines.append(enemy_physics_engine)

        # Clear and re-add loading futures on reset
        self.loading_futures = []
        self.player_loading_future = self.loading_executor.submit(
            self.player.load_animations
        )
        self.loading_futures.append((self.player_loading_future, self.player))

        # Add initial enemy loading futures (for the newly spawned zombie)
        if zombie:
            zombie._is_loading = False
            self.loading_futures.append(
                (self.loading_executor.submit(zombie.load_animations), zombie)
            )

        # Re-initialize player's health bar on reset
        self.player.health_bar = IndicatorBar(
            self.player,
            self.bar_list,
            (self.player.center_x, self.player.center_y),
            width=HEALTHBAR_WIDTH,
            height=HEALTHBAR_HEIGHT,
        )
        self.player.current_health = self.player.max_health
        self.player.health_bar.fullness = 1.0

    def spawn_zombie(
        self,
        zombie_type,
        x,
        y,
        player_ref: Player | None = None,
    ):
        """Spawn a zombie at the specified position"""

        zombie = Zombie(zombie_type=zombie_type, player_ref=self.player)
        zombie.position = (float(x), float(y))
        zombie.load_animations()

        self.enemies.append(zombie)
        self.scene.add_sprite("Enemies", zombie)

        # Create physics engine for this enemy
        physics_engine = arcade.PhysicsEngineSimple(
            zombie,
            self.scene.get_sprite_list("Walls"),
        )
        self.enemy_physics_engines.append(physics_engine)

        return zombie

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

        # Add the walls layer to the scene for collision
        scene.add_sprite_list(
            "Walls", sprite_list=self.tile_map.sprite_lists["Walls"]
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

    def update_player_speed(self):
        # Calculate speed based on the keys pressed

        movement_direction_x = 0
        movement_direction_y = 0
        has_movement = False
        # Handle left/right movement (Left/Right arrows or A/D)
        if (self.key_down[LEFT_KEY] or self.key_down[A_KEY]) and not (
            self.key_down[RIGHT_KEY] or self.key_down[D_KEY]
        ):
            has_movement = True
            movement_direction_x = -1
        elif (self.key_down[RIGHT_KEY] or self.key_down[D_KEY]) and not (
            self.key_down[LEFT_KEY] or self.key_down[A_KEY]
        ):
            has_movement = True
            movement_direction_x = 1

        # Handle up/down movement (Up/Down arrows or W/S)
        if (self.key_down[UP_KEY] or self.key_down[W_KEY]) and not (
            self.key_down[DOWN_KEY] or self.key_down[S_KEY]
        ):
            has_movement = True
            movement_direction_y = 1
        elif (self.key_down[DOWN_KEY] or self.key_down[S_KEY]) and not (
            self.key_down[UP_KEY] or self.key_down[W_KEY]
        ):
            has_movement = True
            movement_direction_y = -1

        self.player.velocity = (
            Vec2(movement_direction_x, movement_direction_y)
            * self.player.speed
            * self.player.delta_time
        )

    def update_enemies(self, delta_time):
        """Update all enemies in the game"""
        for i, enemy in enumerate(self.enemies):
            # Update enemy delta time
            enemy.delta_time = delta_time

            # Simple AI: move towards player if within detection range
            dx = self.player.position[0] - enemy.position[0]
            dy = self.player.position[1] - enemy.position[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < enemy.detection_range:
                # Move towards player
                direction_x = dx
                direction_y = dy
                direction_magnitude = math.sqrt(
                    direction_x**2 + direction_y**2
                )
                if direction_magnitude > 0:
                    normalized_dir_x = direction_x / direction_magnitude
                    normalized_dir_y = direction_y / direction_magnitude
                    enemy.velocity = (
                        Vec2(normalized_dir_x, normalized_dir_y)
                        * enemy.speed
                        * enemy.delta_time
                    )
                else:
                    enemy.velocity = Vec2(0.0, 0.0)

                # Attack if close enough
                if distance < enemy.attack_range and random.random() < 0.01:
                    enemy.attack()
                    # Check for collision with player when attacking
                    if arcade.check_for_collision(enemy, self.player):
                        self.player.take_damage(enemy.damage)
                        Debug.update(
                            "Player Health", self.player.current_health
                        )

            else:
                # Random movement when player not detected
                if random.random() < 0.01:
                    direction_x = random.uniform(-1, 1)
                    direction_y = random.uniform(-1, 1)
                    direction_magnitude = math.sqrt(
                        direction_x**2 + direction_y**2
                    )
                    if direction_magnitude > 0:
                        normalized_dir_x = direction_x / direction_magnitude
                        normalized_dir_y = direction_y / direction_magnitude
                        enemy.velocity = (
                            Vec2(normalized_dir_x, normalized_dir_y)
                            * enemy.speed
                            * enemy.delta_time
                        )
                    else:
                        enemy.velocity = Vec2(0.0, 0.0)
                else:
                    enemy.velocity = Vec2(0.0, 0.0)

            # Update the enemy facing direction to look at player
            enemy.look_at(self.player.position)

            # Update animation state
            enemy.update_state(delta_time)
            enemy.animate(delta_time)

            # Update physics
            if i < len(self.enemy_physics_engines):
                self.enemy_physics_engines[i].update()

    def on_key_press(self, key, modifiers):
        self.key_down[key] = True

        # Toggle fullscreen with F11
        if key == FULLSCREEN_KEY:
            self.window.set_fullscreen(not self.window.fullscreen)
            # Update camera when toggling fullscreen
            self.on_resize(self.window.width, self.window.height)

        # Weapon switching with number keys
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

        # Attack with space
        if key == arcade.key.SPACE:
            self.player.attack()
            if self.player.current_weapon == WeaponType.GUN:
                self.shoot_ray()

        # Death animation with K (for testing)
        if key == arcade.key.K:
            self.player.die()

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
            if self.player.current_weapon == WeaponType.GUN:
                self.shoot_ray()

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_pressed = False

    def shoot_ray(self):
        """Performs ray casting for shooting."""
        if self.player.current_weapon == WeaponType.GUN:
            arcade.play_sound(self.gun_shot_sound)
            start_x, start_y = self.player.position

            # Calculate the direction vector from player's facing angle
            angle_radians = math.radians(self.player.angle)
            dir_x = math.sin(angle_radians)
            dir_y = math.cos(angle_radians)

            # Normalize direction vector
            direction_magnitude = math.sqrt(dir_x**2 + dir_y**2)
            if direction_magnitude > 0:
                normalized_dir_x = dir_x / direction_magnitude
                normalized_dir_y = dir_y / direction_magnitude
            else:
                normalized_dir_x = 0.0
                normalized_dir_y = 0.0

            # Define the length of the ray (e.g., screen diagonal or further)
            ray_length = max(WINDOW_WIDTH, WINDOW_HEIGHT) * 1.5

            # Calculate the end point of the ray
            end_x = start_x + normalized_dir_x * ray_length
            end_y = start_y + normalized_dir_y * ray_length

            # Create a temporary sprite for the ray for collision detection
            ray_sprite = arcade.SpriteSolidColor(
                1, ray_length, arcade.color.YELLOW
            )
            ray_sprite.center_x = start_x + normalized_dir_x * ray_length / 2
            ray_sprite.center_y = start_y + normalized_dir_y * ray_length / 2
            ray_sprite.angle = math.degrees(
                math.atan2(normalized_dir_y, normalized_dir_x)
            )

            # Perform collision check
            hit_sprites = arcade.check_for_collision_with_list(
                ray_sprite, self.scene.get_sprite_list("Enemies")
            )

            if hit_sprites:
                # Find the closest hit enemy
                closest_enemy = None
                min_distance = float("inf")
                for enemy in hit_sprites:
                    distance = arcade.math.get_distance(
                        start_x, start_y, enemy.center_x, enemy.center_y
                    )
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy

                if closest_enemy:
                    closest_enemy.take_damage(10)
                    Debug.update("Hit Enemy", closest_enemy.enemy_type)
                    # Adjust end_x, end_y to the hit point for the bullet visual
                    end_x, end_y = closest_enemy.position
                else:
                    Debug.update("Hit Enemy", "None")
            else:
                Debug.update("Hit Enemy", "None")

            # Create a bullet sprite to visualize the ray
            bullet = Bullet((start_x, start_y), (end_x, end_y))
            self.bullet_list.append(bullet)

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

    def on_update(self, delta_time):
        self.center_camera_to_player(delta_time)

        Debug.update("Player State", f"{self.player.state.value}")
        Debug.update(
            "Player Position",
            f"{self.player.position[0]:.0f}, {self.player.position[1]:.0f}",
        )
        Debug.update(
            "Player Velocity",
            f"{self.player.velocity[0]:.2f}, {self.player.velocity[1]:.2f}",
        )

        self.mouse_position = (
            self.mouse_offset[0] + self.camera.position[0],
            self.mouse_offset[1] + self.camera.position[1],
        )
        self.player.look_at(self.mouse_position)

        if self.player.health_bar:
            self.player.health_bar.position = (
                self.player.center_x,
                self.player.center_y + INDICATOR_BAR_OFFSET,
            )
            
        self.player.update_state(delta_time)
        self.player.animate(delta_time)

        if abs(self.camera.zoom - self.target_zoom) > 0.001:
            self.camera.zoom = arcade.math.lerp(
                self.camera.zoom, self.target_zoom, 5 * delta_time
            )
            Debug.update("Camera Zoom", f"{self.camera.zoom:.2f}")

        self.player.delta_time = delta_time
        self.update_player_speed()
        self.physics_engine.update()



        self.update_enemies(delta_time)

        self.bullet_list.update(delta_time)

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


def main():
    """Main function"""
    window = arcade.Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE,
        update_rate=WINDOW_RATE,
        draw_rate=WINDOW_RATE,
        resizable=True,
    )
    game = GameView()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
