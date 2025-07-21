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
from enum import Enum
import math
import json
import concurrent.futures # Import for ThreadPoolExecutor


# Health bar constants
HEALTHBAR_WIDTH = 25
HEALTHBAR_HEIGHT = 4
HEALTHBAR_OFFSET_Y = 10

# Constants for bullet properties
BULLET_SPEED = 50 # Reduced for testing
BULLET_LIFE = 0.5  # Seconds until bullet disappears

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_RATE = 1 / 144  # 144hz

# Constants
CHARACTER_SCALING = 0.3
TILE_SCALING = 2
COLLECTABLE_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player Movement
PLAYER_MOVEMENT_SPEED = 500
PLAYER_FRICTION = 0.9999

# Camera constants
FOLLOW_DECAY_CONST = (
    0.3  # get within 1% of the target position within 2 seconds
)

VIEWPORT_MARGIN = 250
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN

# Key constants
LEFT_KEY = arcade.key.LEFT
RIGHT_KEY = arcade.key.RIGHT
UP_KEY = arcade.key.UP
DOWN_KEY = arcade.key.DOWN
# WASD keys
W_KEY = arcade.key.W
A_KEY = arcade.key.A
S_KEY = arcade.key.S
D_KEY = arcade.key.D
# Fullscreen toggle
FULLSCREEN_KEY = arcade.key.F11

# Camera zoom constants
ZOOM_STEP = 0.1
MAX_ZOOM = 2.0
MIN_ZOOM = 0.5

# Asset directories
PLAYER_ASSETS_DIR = "resources/Players"
ZOMBIE_ASSETS_DIR = "resources/Zombies"

# Configuration files
PLAYER_CONFIG_FILE = "resources/animation_config/players_config.json"
ZOMBIE_CONFIG_FILE = "resources/animation_config/zombies_config.json"

DEAD_ZONE = 0.1  # Minimum velocity to consider as moving


class EntityState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DYING = "dying"


class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    SHOOTING = "shooting"
    ATTACKING = "attacking"
    DYING = "dying"


class WeaponType(Enum):
    BAT = "Bat"
    GUN = "Gun"
    KNIFE = "Knife"
    RIFLE = "Riffle"
    FLAMETHROWER = "FlameThrower"


def load_character_config(config_file: str) -> dict:
    """Load character configuration from JSON file."""
    try:
        with open(config_file, "r") as f:
            config_data = json.load(f)
            return config_data
    except FileNotFoundError:
        print(f"Configuration file not found: {config_file}")
        print(
            "Please run character_analyzer.py first to generate configuration files"
        )
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {config_file}: {e}")
        return {}


def load_texture_with_anchor(
    frame_path: str, animation_config: dict
) -> tuple[str, float, float, float, float]: # Return raw image data and properties
    """Load raw image data and return properties from animation configuration."""
    try:
        # No longer loading arcade.Texture here, just returning path and properties
        # This ensures image loading is decoupled from OpenGL texture creation
        print(f"DEBUG: load_texture_with_anchor - frame_path: {frame_path}, animation_config keys: {animation_config.keys()}") # Debugging

        image_width = animation_config.get("width", 128)
        image_height = animation_config.get("height", 128)
        anchor_x = animation_config.get("anchor_x", image_width / 2)
        anchor_y = animation_config.get("anchor_y", image_height / 2)

        return frame_path, image_width, image_height, anchor_x, anchor_y

    except Exception as e:
        print(f"Error processing image path {frame_path}: {e}")
        return "", 0, 0, 0, 0 # Return empty data on error

def to_vector(point: tuple[float, float] | arcade.types.Point2 | Vec2) -> Vec2:
    return Vec2(point[0], point[1])

def process_loaded_texture_data(raw_texture_data: tuple[str, float, float, float, float]) -> tuple[arcade.Texture, tuple[float, float]]:
    """Loads arcade.Texture from raw image data on the main thread."""
    frame_path, image_width, image_height, anchor_x, anchor_y = raw_texture_data
    # print(f"Processing loaded texture data for: {frame_path}")
    
    if not frame_path:
        # Handle the error case from load_texture_with_anchor
        fallback_texture = arcade.make_soft_square_texture(
            64, arcade.color.RED, name="fallback"
        )
        return fallback_texture, (0, 0)
    else:
        try:
            texture = arcade.load_texture(frame_path)
            texture = texture.flip_vertically()
        except Exception as e:
            print(f"ERROR: Failed to load arcade.Texture for {frame_path}: {e}")
            fallback_texture = arcade.make_soft_square_texture(
                64, arcade.color.MAGENTA, name="fallback_load_err"
            )
            return fallback_texture, (0, 0)

    # Calculate offset from image center to desired center of mass
    image_center_x = image_width / 2
    image_center_y = image_height / 2

    # Calculate offset (how much to move sprite from its current center)
    offset_x = image_center_x - anchor_x
    offset_y = image_center_y - anchor_y

    return texture, (offset_x, offset_y)

class Bullet(arcade.Sprite):
    """Bullet class for ray casting visual."""

    def __init__(self, start_position: tuple[float, float], end_position: tuple[float, float], **kwargs):
        # Initialize with a texture. Adjust path and scale as needed.
        super().__init__(":resources:images/space_shooter/laserBlue01.png", scale=0.5, **kwargs)
        self.position = start_position
        self.target_position = end_position
        
        # Calculate direction and speed
        direction_x = end_position[0] - start_position[0]
        direction_y = end_position[1] - start_position[1]
        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        
        if magnitude > 0:
            normalized_direction_x = direction_x / magnitude
            normalized_direction_y = direction_y / magnitude
        else:
            normalized_direction_x = 0.0
            normalized_direction_y = 0.0

        self.velocity = (normalized_direction_x * BULLET_SPEED, normalized_direction_y * BULLET_SPEED)

        self.lifetime = BULLET_LIFE
        # self.speed = BULLET_SPEED # No longer needed, as velocity is set directly

    def on_update(self, delta_time: float):
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        self.center_x += self.velocity[0] * delta_time
        self.center_y += self.velocity[1] * delta_time

    def draw(self):
        # No longer drawing a line, as it's a sprite now
        pass


class Debug:
    debug_dict = {}
    text_objects = [] # Change to a list for pre-initialized objects
    initialized = False # Flag to ensure initialization only happens once

    @staticmethod
    def _initialize():
        if Debug.initialized:
            return

        # Pre-create a fixed number of Text objects
        # Adjust MAX_DEBUG_LINES based on expected debug output
        MAX_DEBUG_LINES = 20 # Increased to accommodate more debug lines
        for i in range(MAX_DEBUG_LINES):
            Debug.text_objects.append(
                arcade.Text(
                    "", # Empty text initially
                    0, # placeholder x
                    0, # placeholder y
                    arcade.csscolor.WHITE,
                    18,
                )
            )
        Debug.initialized = True

    @staticmethod
    def update(key: str, text: str):
        Debug.debug_dict[key] = text

    @staticmethod
    def render(x: float, y: float):
        # Ensure initialization has happened
        if not Debug.initialized:
            print("Debug.render called before Debug._initialize. Skipping render.")
            return

        # Use an index to assign pre-created text objects
        text_object_index = 0
        for key, text_value in Debug.debug_dict.items():
            if text_object_index < len(Debug.text_objects):
                text_object = Debug.text_objects[text_object_index]
                text_object.text = f"{key}: {text_value}"
                text_object.x = x
                text_object.y = y
                text_object.draw()
                y += 20
                text_object_index += 1
            else:
                # This case means we have more debug lines than pre-allocated text objects
                # You might want to increase MAX_DEBUG_LINES or handle this case
                print(f"Warning: Ran out of pre-allocated debug text objects for key: {key}")

        # Clear any remaining text objects if the number of debug lines decreased
        while text_object_index < len(Debug.text_objects):
            Debug.text_objects[text_object_index].text = "" # Clear text
            text_object_index += 1

PLAYER_ANIMATION_STRUCTURE = {
    "Bat": 12,
    "Death": 6,
    "FlameThrower": 9,
    "Gun_Shot": 5,
    "Gun_Idle": 1,  # Custom idle animation
    "Knife": 8,
    "Riffle": 9,
    "Walk_bat": 6,
    "Walk_FireThrhrower": 6,
    "Walk_gun": 6,
    "Walk_knife": 6,
    "Walk_riffle": 6,
}


class Entity(arcade.Sprite):
    """Base class for all entities in the game (players, enemies)"""

    def __init__(
        self,
        image_path,
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
    ):
        super().__init__(image_path, scale=scale)

        self.speed = speed
        self.position: Vec2 = Vec2(0, 0) # Changed to Vec2
        self.velocity: Vec2 = Vec2(0, 0) # Changed to Vec2
        self.friction = clamp(friction, 0, 1)
        self.delta_time = WINDOW_RATE

        # Animation properties moved from Character_Display_Sprite
        self.animations = {}
        self.processed_textures = {} # New dictionary to hold processed arcade.Texture objects
        self.current_animation = None
        self.current_animation_frame = 0
        self.current_animation_time = 0
        self.animation_fps = 10
        self.frame_duration = 1.0 / self.animation_fps

        # Base state
        self.state = EntityState.IDLE
        self.facing_direction = 0
        self._is_loading = False # New attribute to track loading status

        # Health attributes
        self.max_health = 100
        self.current_health = 100
        # self.health_bar = None # Will hold an instance of IndicatorBar

    def draw(self):
        """Draw the entity, including its health bar."""
        super().draw()

        # Draw health bar
        if self.current_health < self.max_health:
            # Calculate health bar position
            health_x = self.center_x
            health_y = self.center_y + self.height / 2 + HEALTHBAR_OFFSET_Y

            # Draw background box
            arcade.draw_rectangle_filled(
                health_x,
                health_y,
                HEALTHBAR_WIDTH,
                HEALTHBAR_HEIGHT,
                arcade.color.BLACK,
            )

            # Draw health amount
            health_percentage = self.current_health / self.max_health
            arcade.draw_rectangle_filled(
                health_x - HEALTHBAR_WIDTH / 2 * (1 - health_percentage),
                health_y,
                HEALTHBAR_WIDTH * health_percentage,
                HEALTHBAR_HEIGHT,
                arcade.color.RED,
            )

    def take_damage(self, damage_amount: float):
        """Reduce entity health and handle death."""
        self.current_health -= damage_amount
        if self.current_health <= 0:
            self.current_health = 0
            self.die() # Trigger death animation or removal
        # if self.health_bar:
        #     self.health_bar.fullness = self.current_health / self.max_health

    class AnimationType(Enum):
        MOVEMENT = "Movement"
        ATTACK = "Attack"
        DEATH = "Death"

    def _apply_texture_and_offset(
        self, texture: arcade.Texture, offset: tuple[float, float]
    ):
        """Helper to set texture and apply offset to center_x, center_y"""
        self.texture = texture
        self.sync_hit_box_to_texture()
        # self.center_x = self.center_x + offset[0] * self.scale_x
        # self.center_y = self.center_y + offset[1] * self.scale_y

    def load_animation_sequence(
        self,
        name: str,
        animation_type: AnimationType,
        raw_animation_sequence: list[tuple[str, float, float, float, float]], # Accepts raw data
        raw_idle_texture: tuple[str, float, float, float, float] | None,
    ):
        self.animations[name] = {
            "type": animation_type,
            "sequence": [], # This will now store raw data
            "idle": None,
        }

        self.animations[name]["sequence"] = raw_animation_sequence
        self.animations[name]["idle"] = raw_idle_texture

        # Initial animation setting logic is moved to on_update after processing

    def animate(self, delta_time: float):
        """Update animation based on delta time"""
        if self.current_animation is None:
            return

        self.current_animation_time += delta_time

        # Check if it's time to advance to the next frame
        if self.current_animation_time >= self.frame_duration:
            self.current_animation_time = 0

            # Get the current animation frames
            if self.current_animation in self.animations:
                animation_data = self.animations[self.current_animation]
                animation_frames = animation_data.get("sequence", [])

                if animation_frames:
                    # Advance to next frame
                    self.current_animation_frame = (
                        self.current_animation_frame + 1
                    ) % len(animation_frames)

                    # Check if animation has completed a full loop (for non-looping animations)
                    is_attack_animation = (
                        animation_data.get("type")
                        == Entity.AnimationType.ATTACK
                    )
                    is_last_frame = (
                        self.current_animation_frame == 0
                    )  # Back to first frame means a loop completed

                    # Removed state change from Entity.animate, handled in update_state of subclasses
                    # if is_attack_animation and is_last_frame and len(animation_frames) > 1:
                    #     self.state = EntityState.IDLE
                    #     self.set_animation_for_state()

                    # Update the sprite's texture and apply offset
                    # Lookup processed texture
                    current_frame_raw_data = animation_frames[self.current_animation_frame]
                    current_frame_key = current_frame_raw_data[0] # Use path as key
                    if current_frame_key in self.processed_textures:
                        texture, offset = self.processed_textures[current_frame_key]
                        self._apply_texture_and_offset(texture, offset)
                    else:
                        # Use a fallback texture if the processed texture is not yet available
                        print(f"DEBUG: {self.__class__.__name__} processed_textures keys: {self.processed_textures.keys()}") # Debug keys
                        fallback_texture = arcade.make_soft_square_texture(
                            32, arcade.color.MAGENTA, name="fallback_anim"
                        )
                        self._apply_texture_and_offset(fallback_texture, (0, 0))
                        print(f"Warning: Processed texture for {current_frame_key} not found during animation. Using fallback.")

    def set_animation(self, animation_name: str):
        """Set the current animation by name"""
        if animation_name in self.animations and self.animations[
            animation_name
        ].get("sequence"):
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            # Set the first frame immediately
            animation_data = self.animations[animation_name]
            # Lookup processed texture
            first_frame_raw_data = animation_data["sequence"][0]
            first_frame_key = first_frame_raw_data[0] # Use path as key
            if first_frame_key in self.processed_textures:
                first_frame_texture, first_frame_offset = self.processed_textures[first_frame_key]
                self._apply_texture_and_offset(
                    first_frame_texture, first_frame_offset
                )
            else:
                # Use a fallback texture if the processed texture is not yet available
                print(f"DEBUG: {self.__class__.__name__} processed_textures keys in set_animation: {self.processed_textures.keys()}") # Debug keys
                fallback_texture = arcade.make_soft_square_texture(
                    32, arcade.color.MAGENTA, name="fallback_setanim"
                )
                self._apply_texture_and_offset(fallback_texture, (0, 0))
                print(f"Warning: Processed texture for {first_frame_key} not found. Using fallback.")
        elif animation_name in self.animations and self.animations[
            animation_name
        ].get("idle"):
            # If it's an idle animation, it might only have an "idle" texture and no sequence
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            # Lookup processed idle texture
            idle_raw_data = self.animations[animation_name]["idle"]
            idle_key = idle_raw_data[0] # Use path as key
            if idle_key in self.processed_textures:
                idle_texture, idle_offset = self.processed_textures[idle_key]
                self._apply_texture_and_offset(idle_texture, idle_offset)
            else:
                # Use a fallback texture if the processed texture is not yet available
                fallback_texture = arcade.make_soft_square_texture(
                    32, arcade.color.BLUE, name="fallback_setanim_idle"
                )
                self._apply_texture_and_offset(fallback_texture, (0, 0))
                print(f"Warning: Processed idle texture for {idle_key} not found. Using fallback.")
        else:
            print(
                f"Warning: Animation '{animation_name}' not found or has no frames."
            )

    def move(self, direction: Vec2):
        """Move the entity in the given direction"""
        if direction.length() > 0:
            self.velocity = direction * self.speed * self.delta_time

        self.update_physics()
    
    def look_at(self, target_pos: Vec2):
        """Update facing direction to look at target"""
        # Calculate angle between enemy and target
        dx = target_pos[0] - self.center_x # Access .x and .y
        dy = target_pos[1] - self.center_y # Access .x and .y
        angle = math.atan2(dx, dy) * 180 / math.pi
        self.angle = angle

        # Set facing based on angle
        self.facing_direction = angle

    def update_physics(self):
        """Update physics calculations"""
        # Apply friction directly to change_x and change_y
        # friction
        friction_factor = (1 - self.friction) ** (
            self.delta_time
        )
        self.velocity *= friction_factor

        # Clamp the velocity (change_x, change_y) to the max speed
        velocity_length = math.sqrt(self.velocity.x**2 + self.velocity.y**2)

        if velocity_length > self.speed:
            normalized_x = self.velocity.x / velocity_length
            normalized_y = self.velocity.y / velocity_length
            self.velocity = Vec2(normalized_x * self.speed, normalized_y * self.speed)

    def update_state(self, delta_time: float):
        """Update entity state based on velocity and other factors - to be overridden by child classes"""
        pass

    def die(self):
        """Trigger death animation"""
        self.state = EntityState.DYING


class Player(Entity):
    """Player class representing the user-controlled character"""

    def __init__(
        self,
        image_path,
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        player_preset="Man",
    ):
        super().__init__(
            image_path, scale=scale, friction=friction, speed=speed
        )

        self.player_preset = player_preset

        # Player-specific properties
        self.state = PlayerState.IDLE
        self.mouse_position = (0.0, 0.0)

        # Weapon handling
        self.current_weapon = WeaponType.GUN

        # Load character configuration
        self.character_config = load_character_config(PLAYER_CONFIG_FILE)

        # Loading will be managed externally via thread pool
        self._is_loading = False # No longer loading asynchronously

    def load_animations(self):
        """Synchronous method to load player animations from configuration file"""
        if (
            not self.character_config
            or self.player_preset not in self.character_config
        ):
            print(
                f"No configuration found for player preset: {self.player_preset}"
            )
            self._is_loading = False # Mark as not loading if config not found
            return

        character_data = self.character_config[self.player_preset]
        animation_dict = {}
        total_frames = 0

        # Load animations from configuration
        for animation_name, animation_config in character_data.items():
            textures = []

            # Get the list of frame paths from the animation config
            frame_paths = animation_config.get("frames", [])

            for frame_path in frame_paths:
                raw_texture_data = load_texture_with_anchor(
                    frame_path, animation_config
                )
                textures.append(
                    raw_texture_data # Store raw data, not loaded texture
                )  # Store texture and offset as a tuple
                total_frames += 1

            animation_dict[animation_name] = textures

            # Create idle animations from first frame of walk animations
            if animation_name.startswith("Walk_"):
                weapon_type = animation_name[5:]  # Remove "Walk_" prefix
                idle_key = f"Idle_{weapon_type}"
                if textures:
                    # Pass the name, type, sequence, and idle texture to the Entity's animation system
                    self.load_animation_sequence(
                        animation_name,
                        Entity.AnimationType.MOVEMENT,
                        textures,
                        textures[0],
                    )

                    # Store a specific idle animation as well
                    self.load_animation_sequence(
                        idle_key,
                        Entity.AnimationType.MOVEMENT,
                        [textures[0]],
                        textures[0],
                    )
                total_frames += 1
            else:
                # Load other animations (Attack, Death) directly into the Entity's animation system
                if animation_name == "Death":
                    self.load_animation_sequence(
                        animation_name,
                        Entity.AnimationType.DEATH,
                        textures,
                        textures[0] if textures else None,
                    )
                elif animation_name in [
                    "Bat",
                    "FlameThrower",
                    "Gun_Shot",
                    "Knife",
                    "Riffle",
                ]:  # Attack animations
                    self.load_animation_sequence(
                        animation_name,
                        Entity.AnimationType.ATTACK,
                        textures,
                        textures[0] if textures else None,
                    )
                else:
                    self.load_animation_sequence(
                        animation_name,
                        Entity.AnimationType.MOVEMENT,
                        textures,
                        textures[0] if textures else None,
                    )

        # Add summary debug info
        Debug.update(
            f"{self.player_preset} Animations",
            f"{len(self.animations)} types, {total_frames} frames",
        )
        Debug.update(f"Current Weapon", f"{self.current_weapon.name}")

        # Process loaded textures into arcade.Texture objects
        for anim_name, animation_info in self.animations.items():
            if "sequence" in animation_info and animation_info["sequence"]:
                for raw_frame_data in animation_info["sequence"]:
                    frame_path = raw_frame_data[0]
                    if frame_path not in self.processed_textures:
                        try:
                            texture, offset = process_loaded_texture_data(raw_frame_data)
                            self.processed_textures[frame_path] = (texture, offset)
                        except Exception as e:
                            print(f"Error processing and storing texture {frame_path}: {e}")
            if "idle" in animation_info and animation_info["idle"]:
                raw_frame_data = animation_info["idle"]
                frame_path = raw_frame_data[0]
                if frame_path not in self.processed_textures:
                    try:
                        texture, offset = process_loaded_texture_data(raw_frame_data)
                        self.processed_textures[frame_path] = (texture, offset)
                    except Exception as e:
                        print(f"Error processing and storing idle texture {frame_path}: {e}")

        self._is_loading = False # Mark as not loading after processing

    def set_weapon(self, weapon_type: WeaponType):
        """Set the current weapon"""
        self.current_weapon = weapon_type
        self.set_animation_for_state()

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state and weapon"""
        weapon_name = self.current_weapon.value

        if self.state == PlayerState.IDLE:
            # Try to use the specific idle animation for this weapon
            idle_anim = f"Idle_{weapon_name.lower()}"
            Debug.update("Trying Idle Animation", idle_anim)

            if idle_anim in self.animations and (
                self.animations[idle_anim].get("sequence")
                or self.animations[idle_anim].get("idle")
            ):
                self.set_animation(idle_anim)
            else:
                # If specific idle animation not found, try generic weapon idle
                # Check for matching weapon types with different case formats
                found = False
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Idle_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        self.set_animation(anim_name)
                        found = True
                        break

                # If still not found, use any available idle animation as last resort
                if not found:
                    Debug.update(
                        "Fallback Animation", "Using first available idle"
                    )
                    weapon_priority = [
                        self.current_weapon.value
                    ]  # Try current weapon first
                    for weapon in WeaponType:
                        if weapon != self.current_weapon:
                            weapon_priority.append(weapon.value)

                    for weapon_type in weapon_priority:
                        idle_check = f"Idle_{weapon_type.lower()}"
                        if idle_check in self.animations and (
                            self.animations[idle_check].get("sequence")
                            or self.animations[idle_check].get("idle")
                        ):
                            self.set_animation(idle_check)
                            found = True
                            break

                    # Last resort - use any idle animation
                    if not found:
                        for anim_name in self.animations:
                            if anim_name.startswith("Idle_"):
                                self.set_animation(anim_name)
                                break

        elif self.state == PlayerState.WALKING:
            # Try exact match first
            walk_anim = f"Walk_{weapon_name.lower()}"

            # Then try alternative cases
            if not (
                walk_anim in self.animations
                and (
                    self.animations[walk_anim].get("sequence")
                    or self.animations[walk_anim].get("idle")
                )
            ):
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Walk_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        walk_anim = anim_name
                        break

            if walk_anim in self.animations and (
                self.animations[walk_anim].get("sequence")
                or self.animations[walk_anim].get("idle")
            ):
                self.set_animation(walk_anim)
            else:
                # Fallback to any walk animation
                for anim_name in self.animations:
                    if anim_name.startswith("Walk_"):
                        self.set_animation(anim_name)
                        break

        elif self.state == PlayerState.SHOOTING:
            shoot_anim = "Gun_Shot"
            if shoot_anim in self.animations and (
                self.animations[shoot_anim].get("sequence")
                or self.animations[shoot_anim].get("idle")
            ):
                # Only set animation if not already shooting or if current animation is not the full shooting cycle
                if self.current_animation != shoot_anim or \
                    (self.current_animation == shoot_anim and self.current_animation_frame == len(self.animations[shoot_anim]['sequence']) - 1):
                    self.set_animation(shoot_anim)

        elif self.state == PlayerState.ATTACKING:
            # Try to use the specific attack animation for this weapon
            if weapon_name in self.animations and (
                self.animations[weapon_name].get("sequence")
                or self.animations[weapon_name].get("idle")
            ):
                # Only set animation if not already attacking or if current animation is not the full attack cycle
                if self.current_animation != weapon_name or \
                    (self.current_animation == weapon_name and self.current_animation_frame == len(self.animations[weapon_name]['sequence']) - 1):
                    self.set_animation(weapon_name)
            else:
                # Try to find a matching attack animation
                for anim_name in self.animations:
                    if (
                        anim_name.startswith("Walk_")
                        and weapon_name.lower() in anim_name.lower()
                    ):
                        walk_anim = anim_name
                        break

            if walk_anim in self.animations and (
                self.animations[walk_anim].get("sequence")
                or self.animations[walk_anim].get("idle")
            ):
                self.set_animation(walk_anim)
            else:
                # Fallback to any walk animation
                for anim_name in self.animations:
                    if anim_name.startswith("Walk_"):
                        self.set_animation(anim_name)
                        break

        elif self.state == PlayerState.DYING:
            if "Death" in self.animations and (
                self.animations["Death"].get("sequence")
                or self.animations["Death"].get("idle")
            ):
                self.set_animation("Death")

        Debug.update(
            "Selected Animation",
            str(self.current_animation) if self.current_animation else "None",
        )

    def update_state(self, delta_time: float):
        """Update player state based on velocity and other factors"""
        # Allow shooting/attacking animation to finish before switching state
        if self.state in [PlayerState.SHOOTING, PlayerState.ATTACKING]:
            current_anim_data = self.animations.get(self.current_animation)
            if current_anim_data and self.current_animation_frame == len(current_anim_data['sequence']) - 1:
                # Animation finished, transition to idle/walking
                velocity_magnitude = math.sqrt(self.velocity.x**2 + self.velocity.y**2) # Use change_x/y
                if velocity_magnitude > DEAD_ZONE:
                    self.state = PlayerState.WALKING
                else:
                    self.state = PlayerState.IDLE
                self.set_animation_for_state()
            return

        # Skip state update if in the middle of a death animation
        if self.state == PlayerState.DYING:
            return

        # Check if player is moving
        velocity_magnitude = math.sqrt(self.velocity.x**2 + self.velocity.y**2) # Use change_x/y

        if velocity_magnitude > DEAD_ZONE:
            if self.state != PlayerState.WALKING:
                self.state = PlayerState.WALKING
                self.set_animation_for_state()
        else:
            if self.state != PlayerState.IDLE:
                self.state = PlayerState.IDLE
                self.set_animation_for_state()

    def look_at(self, mouse_pos: Vec2):
        """Update facing direction based on mouse position"""
        self.mouse_position = mouse_pos
        super().look_at(mouse_pos)
        Debug.update("Player Angle (internal)", f"{self.angle:.2f}") # Add debug for player angle

    def attack(self):
        """Trigger an attack animation based on current weapon"""
        if self.state not in [
            PlayerState.ATTACKING,
            PlayerState.SHOOTING,
            PlayerState.DYING,
        ]:
            if self.current_weapon == WeaponType.GUN:
                self.state = PlayerState.SHOOTING
            else:
                self.state = PlayerState.ATTACKING
            self.set_animation_for_state()

    def die(self):
        """Trigger death animation"""
        self.state = PlayerState.DYING
        self.set_animation_for_state()


class Enemy(Entity):
    """Base class for all enemies (zombies, monsters)"""

    def __init__(
        self,
        image_path,
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=int(PLAYER_MOVEMENT_SPEED * 0.5),
        enemy_type="Army_zombie",
        player_ref: Player | None = None,
    ):
        super().__init__(
            image_path, scale=scale, friction=friction, speed=speed
        )

        self.enemy_type = enemy_type
        self.player = player_ref  # Store player reference
        self.attack_range = 50  # Initialize attack_range in base Enemy class

        # Load enemy configuration
        self.enemy_config = load_character_config(ZOMBIE_CONFIG_FILE)

        # Load animations
        self._is_loading = False # No longer loading asynchronously

    def load_animations(self):
        """Synchronous method to load enemy animations from configuration file"""
        if not self.enemy_config or self.enemy_type not in self.enemy_config:
            print(f"No configuration found for enemy type: {self.enemy_type}")
            return

        enemy_data = self.enemy_config[self.enemy_type]
        animation_dict = {}
        total_frames = 0

        # Load animations from configuration
        for animation_name, animation_config in enemy_data.items():
            textures = []

            # Get the list of frame paths from the animation config
            frame_paths = animation_config.get("frames", [])

            for frame_path in frame_paths:
                raw_texture_data = load_texture_with_anchor(
                    frame_path, animation_config
                )
                textures.append(
                    raw_texture_data # Store raw data, not loaded texture
                )  # Store texture and offset as a tuple
                total_frames += 1

            # Create idle animation from first frame of walk animation
            if animation_name == "Walk" and textures:
                # Pass the name, type, sequence, and idle texture to the Entity's animation system
                self.load_animation_sequence(
                    animation_name,
                    Entity.AnimationType.MOVEMENT,
                    textures,
                    textures[0],
                )
                self.load_animation_sequence(
                    "Idle",
                    Entity.AnimationType.MOVEMENT,
                    [textures[0]],
                    textures[0],
                )
            elif animation_name == "Attack":
                self.load_animation_sequence(
                    animation_name,
                    Entity.AnimationType.ATTACK,
                    textures,
                    textures[0] if textures else None,
                )
            elif animation_name == "Death":
                self.load_animation_sequence(
                    animation_name,
                    Entity.AnimationType.DEATH,
                    textures,
                    textures[0] if textures else None,
                )
            else:
                self.load_animation_sequence(
                    animation_name,
                    Entity.AnimationType.MOVEMENT,
                    textures,
                    textures[0] if textures else None,
                )

        Debug.update(
            f"{self.enemy_type} Animations",
            f"{len(self.animations)} types, {total_frames} frames",
        )

        # Process loaded textures into arcade.Texture objects
        for anim_name, animation_info in self.animations.items():
            if "sequence" in animation_info and animation_info["sequence"]:
                for raw_frame_data in animation_info["sequence"]:
                    frame_path = raw_frame_data[0]
                    if frame_path not in self.processed_textures:
                        try:
                            texture, offset = process_loaded_texture_data(raw_frame_data)
                            self.processed_textures[frame_path] = (texture, offset)
                        except Exception as e:
                            print(f"Error processing and storing texture {frame_path}: {e}")
            if "idle" in animation_info and animation_info["idle"]:
                raw_frame_data = animation_info["idle"]
                frame_path = raw_frame_data[0]
                if frame_path not in self.processed_textures:
                    try:
                        texture, offset = process_loaded_texture_data(raw_frame_data)
                        self.processed_textures[frame_path] = (texture, offset)
                    except Exception as e:
                        print(f"Error processing and storing idle texture {frame_path}: {e}")

        self._is_loading = False # Unset loading flag - MOVED TO MAIN THREAD

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state"""
        if self.state == EntityState.IDLE:
            if "Idle" in self.animations and (
                self.animations["Idle"].get("sequence")
                or self.animations["Idle"].get("idle")
            ):
                self.set_animation("Idle")

        elif self.state == EntityState.WALKING:
            if "Walk" in self.animations and (
                self.animations["Walk"].get("sequence")
                or self.animations["Walk"].get("idle")
            ):
                self.set_animation("Walk")

        elif self.state == EntityState.ATTACKING:
            if "Attack" in self.animations and (
                self.animations["Attack"].get("sequence")
                or self.animations["Attack"].get("idle")
            ):
                self.set_animation("Attack")

        elif self.state == EntityState.DYING:
            if "Death" in self.animations and (
                self.animations["Death"].get("sequence")
                or self.animations["Death"].get("idle")
            ):
                self.set_animation("Death")

    def update_state(self, delta_time: float):
        """Update enemy state based on velocity and other factors"""
        # Skip state update if in the middle of death animation
        if self.state == EntityState.DYING:
            return

        # Check if enemy is currently attacking
        if self.state == EntityState.ATTACKING:
            # If the animation has completed a cycle (handled in animate), it will already reset state.
            # Otherwise, check if player is out of range to stop attacking
            if (
                self.player
            ):  # Ensure player exists before accessing its position
                dx = self.player.position[0] - self.position[0] # Access .x and .y
                dy = self.player.position[1] - self.position[1] # Access .x and .y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > self.attack_range + 20:  # Add a small buffer
                    # Player moved out of range, stop attacking
                    self.state = EntityState.IDLE
                    self.set_animation_for_state()
                    return

        # If not attacking or dying, check for movement
        velocity_magnitude = math.sqrt(self.velocity.x**2 + self.velocity.y**2) # Use change_x/y

        if velocity_magnitude > DEAD_ZONE:
            if self.state != EntityState.WALKING:
                self.state = EntityState.WALKING
                self.set_animation_for_state()
        else:
            if self.state != EntityState.IDLE:
                self.state = EntityState.IDLE
                self.set_animation_for_state()

    def attack(self):
        """Trigger attack animation"""
        if self.state not in [EntityState.ATTACKING, EntityState.DYING]:
            self.state = EntityState.ATTACKING
            self.set_animation_for_state()

    def look_at(self, target_pos: Vec2):
        """Update facing direction to look at target"""
        super().look_at(target_pos)



class Zombie(Enemy):
    """Specific implementation for zombie enemies"""

    def __init__(
        self,
        image_path,
        zombie_type="Army_zombie",
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=int(PLAYER_MOVEMENT_SPEED * 0.4),
        player_ref: Player | None = None,
    ):
        super().__init__(
            image_path,
            scale=scale,
            friction=friction,
            speed=speed,
            enemy_type=zombie_type,
            player_ref=player_ref,
        )

        self.player = player_ref

        # Zombie-specific properties
        self.detection_range = 300
        self.attack_range = 50
        self.damage = 10


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()

        Debug._initialize() # Initialize the Debug system here
        self.loading_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4) # Initialize thread pool
        self.loading_futures = [] # List to hold Futures for loading tasks

        self.window.background_color = arcade.color.AMAZON

        # Camera for scrolling
        self.camera = arcade.Camera2D()
        self.camera_bounds = self.window.rect
        self.target_zoom = 1.0 # Initial normal zoom

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = arcade.Camera2D()

        self.scene = self.create_scene()

        # Set up the player info
        self.player = Player(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            speed=PLAYER_MOVEMENT_SPEED,
        )
        self.player.load_animations() # Call sync method directly

        # Enemy list and physics engines - initialize before spawning enemies
        self.enemies = []
        self.enemy_physics_engines = []

        # Add a test zombie
        self.spawn_zombie(
            "Army_zombie", x=400, y=350, player_ref=self.player
        )  # Pass player reference

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
        self.left_mouse_pressed = (
            False  # New attribute to track mouse button state
        )

        self.gun_shot_sound = arcade.load_sound("resources/sound/weapon/Desert Eagle/gun_rifle_pistol.wav")
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
        zombie = self.spawn_zombie("Army_zombie", x=400, y=350, player_ref=self.player) # Store zombie instance

        # Physics engine for player
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Walls"), # Update to use "Walls" for collision
        )
        
        # Create physics engine for this enemy (after adding to scene)
        enemy_physics_engine = arcade.PhysicsEngineSimple(
            zombie,
            self.scene.get_sprite_list("Walls"),
        )
        self.enemy_physics_engines.append(enemy_physics_engine)

        # Clear and re-add loading futures on reset
        self.loading_futures = []
        self.player._is_loading = False # No longer loading asynchronously
        self.player_loading_future = self.loading_executor.submit(self.player.load_animations)
        self.loading_futures.append((self.player_loading_future, self.player))
        
        # Add initial enemy loading futures (for the newly spawned zombie)
        if zombie:
            zombie._is_loading = False # No longer loading asynchronously
            self.loading_futures.append((self.loading_executor.submit(zombie.load_animations), zombie))

        # Initialize player state - state system will handle animations
        # self.player.state = PlayerState.IDLE
        # self.player.set_animation_for_state()

    def spawn_zombie(
        self,
        zombie_type,
        x,
        y,
        player_ref: Player | None = None,
    ):
        """Spawn a zombie at the specified position"""
        # Use a placeholder image initially - it will be replaced by the animation system
        placeholder_image = os.path.join(
            ZOMBIE_ASSETS_DIR, zombie_type, "Walk", "walk_000.png"
        )
        if not os.path.exists(placeholder_image):
            print(f"ERROR: Placeholder image path does not exist: {placeholder_image}") # Debugging
            placeholder_image = (
                ":resources:images/animated_characters/zombie/zombie_idle.png"
            )

        zombie = Zombie(
            placeholder_image, zombie_type=zombie_type, player_ref=self.player
        )
        zombie.position = (float(x), float(y))
        zombie.load_animations() # Call sync method directly

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
        scene.add_sprite_list("Dirt", sprite_list=self.tile_map.sprite_lists["Dirt"])
        scene.add_sprite_list("Grass", sprite_list=self.tile_map.sprite_lists["Grass"])
        scene.add_sprite_list("Road", sprite_list=self.tile_map.sprite_lists["Road"])
        
        # Add the walls layer to the scene for collision
        scene.add_sprite_list("Walls", sprite_list=self.tile_map.sprite_lists["Walls"])
        
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
            self.bullet_list.draw() # Draw bullets after scene is drawn

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

        self.player.velocity = Vec2(movement_direction_x, movement_direction_y) * self.player.speed * self.player.delta_time

    def update_enemies(self, delta_time):
        """Update all enemies in the game"""
        for i, enemy in enumerate(self.enemies):
            # Update enemy delta time
            enemy.delta_time = delta_time

            # Simple AI: move towards player if within detection range
            dx = self.player.position[0] - enemy.position[0] # Access .x and .y
            dy = self.player.position[1] - enemy.position[1] # Access .x and .y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < enemy.detection_range:
                # Move towards player
                direction_x = dx
                direction_y = dy
                direction_magnitude = math.sqrt(direction_x**2 + direction_y**2)
                if direction_magnitude > 0:
                    normalized_dir_x = direction_x / direction_magnitude
                    normalized_dir_y = direction_y / direction_magnitude
                    enemy.velocity = Vec2(normalized_dir_x, normalized_dir_y) * enemy.speed * enemy.delta_time
                else:
                    enemy.velocity = Vec2(0.0, 0.0)

                # Attack if close enough
                if (
                    distance < enemy.attack_range and random.random() < 0.01
                ):  # Small chance to attack each frame
                    enemy.attack()
                    # Check for collision with player when attacking
                    if arcade.check_for_collision(enemy, self.player):
                        self.player.take_damage(enemy.damage) # Apply zombie\'s damage to player
                        Debug.update("Player Health", self.player.current_health) # Debug player health

            else:
                # Random movement when player not detected
                if random.random() < 0.01:  # Change direction occasionally
                    direction_x = random.uniform(-1, 1)
                    direction_y = random.uniform(-1, 1)
                    direction_magnitude = math.sqrt(direction_x**2 + direction_y**2)
                    if direction_magnitude > 0:
                        normalized_dir_x = direction_x / direction_magnitude
                        normalized_dir_y = direction_y / direction_magnitude
                        enemy.velocity = Vec2(normalized_dir_x, normalized_dir_y) * enemy.speed * enemy.delta_time
                    else:
                        enemy.velocity = Vec2(0.0, 0.0)
                else:
                    # Continue current movement
                    enemy.velocity = Vec2(0.0, 0.0) # This will apply friction but not add new velocity

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
        if key == arcade.key.KEY_1:
            self.player.set_weapon(WeaponType.GUN)
        elif key == arcade.key.KEY_2:
            self.player.set_weapon(WeaponType.BAT)
        elif key == arcade.key.KEY_3:
            self.player.set_weapon(WeaponType.KNIFE)
        elif key == arcade.key.KEY_4:
            self.player.set_weapon(WeaponType.RIFLE)
        elif key == arcade.key.KEY_5:
            self.player.set_weapon(WeaponType.FLAMETHROWER)

        # Attack with space
        if key == arcade.key.SPACE:
            self.player.attack()
            if self.player.current_weapon == WeaponType.GUN:
                self.shoot_ray() # Call shoot_ray when space is pressed and gun is equipped

        # Death animation with K (for testing)
        if key == arcade.key.K:
            self.player.die()

        # Spawn different zombies with Z key (for testing)
        if key == arcade.key.LCTRL:
            # Removed zombie spawning here, replaced with zoom functionality
            # zombie_types = ["Army_zombie", "Cop_Zombie", "Zombie1_female", 
            #                "Zombie2_female", "Zombie3_male", "Zombie4_male"]
            # zombie_type = random.choice(zombie_types)
            # x = self.player.position[0] + random.randint(-300, 300)
            # y = self.player.position[1] + random.randint(-300, 300)
            # self.spawn_zombie(zombie_type, x, y, self.player) # Pass player reference
            
            # Zoom out by increasing camera zoom
            # self.camera.zoom = clamp(self.camera.zoom + ZOOM_STEP, MIN_ZOOM, MAX_ZOOM)
            # Debug.update("Camera Zoom", f"{self.camera.zoom:.2f}")
            
            # Set target zoom for smooth transition
            self.target_zoom = MIN_ZOOM # Zoom out

    def on_key_release(self, key, modifiers):
        self.key_down[key] = False
        
        if key == arcade.key.LCTRL:
            self.target_zoom = 1.0 # Return to normal zoom

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
            # If player was shooting, transition back to idle/walking is now handled by animation completion
            # if self.player.state == PlayerState.SHOOTING:
            #     # Check if player is moving to set state correctly
            #     velocity_magnitude = math.sqrt(self.player.velocity[0]**2 + self.player.velocity[1]**2)
            #     if velocity_magnitude > DEAD_ZONE:
            #         self.player.state = PlayerState.WALKING
            #     else:
            #         self.player.state = PlayerState.IDLE
            #     self.player.set_animation_for_state()

    def shoot_ray(self):
        """Performs ray casting for shooting."""
        if self.player.current_weapon == WeaponType.GUN:
            arcade.play_sound(self.gun_shot_sound)
            start_x, start_y = self.player.position
            
            # Calculate the direction vector from player's facing angle
            angle_radians = math.radians(self.player.angle)
            # This is correct, sin for x and cos for y since 0 degrees is to the right
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
            ray_length = max(WINDOW_WIDTH, WINDOW_HEIGHT) * 1.5 # Extend beyond screen

            # Calculate the end point of the ray
            end_x = start_x + normalized_dir_x * ray_length
            end_y = start_y + normalized_dir_y * ray_length

            # Create a temporary sprite for the ray for collision detection
            # Make it a thin rectangle extending from player to ray_length
            ray_sprite = arcade.SpriteSolidColor(
                1,  # width
                ray_length,  # height
                arcade.color.YELLOW  # color - doesn't really matter as it's removed
            )
            ray_sprite.center_x = start_x + normalized_dir_x * ray_length / 2
            ray_sprite.center_y = start_y + normalized_dir_y * ray_length / 2
            ray_sprite.angle = math.degrees(math.atan2(normalized_dir_y, normalized_dir_x))

            # Perform collision check
            hit_sprites = arcade.check_for_collision_with_list(
                ray_sprite,
                self.scene.get_sprite_list("Enemies")
            )

            # # Remove the temporary ray sprite immediately
            # ray_sprite.remove_from_sprite_lists()

            if hit_sprites:
                # Find the closest hit enemy
                closest_enemy = None
                min_distance = float('inf')
                for enemy in hit_sprites:
                    distance = arcade.math.get_distance(start_x, start_y, enemy.center_x, enemy.center_y)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy

                if closest_enemy:
                    closest_enemy.take_damage(10) # Apply damage to the enemy
                    Debug.update("Hit Enemy", closest_enemy.enemy_type)
                    # Adjust end_x, end_y to the hit point for the bullet visual
                    end_x, end_y = closest_enemy.position
                else:
                    Debug.update("Hit Enemy", "None")
            else:
                Debug.update("Hit Enemy", "None")

            # Create a bullet sprite to visualize the ray
            bullet = Bullet((start_x, start_y), (end_x, end_y))
            bullet.angle = math.degrees(math.atan2(normalized_dir_x, normalized_dir_y))-90
            self.bullet_list.append(bullet)

    def center_camera_to_player(self, delta_time):
        # Move the camera to center on the player
        # arcade.math.smerp_2d expects Vec2, so convert player.position
        current_camera_position = Vec2(self.camera.position[0], self.camera.position[1])
        player_position_vec = Vec2(self.player.position[0], self.player.position[1])

        new_camera_position_vec = arcade.math.smerp_2d(
            current_camera_position,
            player_position_vec,
            delta_time,
            FOLLOW_DECAY_CONST,
        )
        self.camera.position = (new_camera_position_vec.x, new_camera_position_vec.y)

    def on_update(self, delta_time):
        self.center_camera_to_player(delta_time)

        # Debug info for current animation, state, and position (always update)
        Debug.update("Current Animation", f"{self.player.current_animation}")
        Debug.update("Player State", f"{self.player.state.value}")
        Debug.update("Player Position", f"{self.player.position[0]:.0f}, {self.player.position[1]:.0f}")
        # Log player velocity
        Debug.update("Player Velocity", f"{self.player.velocity[0]:.2f}, {self.player.velocity[1]:.2f}")

        # Only proceed with game logic if player and initial enemies are no longer loading
        # if self.player._is_loading or any(enemy._is_loading for enemy in self.enemies):
        #     return

        self.mouse_position = (self.mouse_offset[0] + self.camera.position[0], self.mouse_offset[1] + self.camera.position[1])
        self.player.look_at(self.mouse_position)
        
        # Smoothly interpolate camera zoom towards target zoom
        if abs(self.camera.zoom - self.target_zoom) > 0.001: # Check for a small difference to avoid constant updates
            self.camera.zoom = arcade.math.lerp(self.camera.zoom, self.target_zoom, 5 * delta_time) # Increased interpolation speed
            Debug.update("Camera Zoom", f"{self.camera.zoom:.2f}")
        
        # Update player
        self.player.delta_time = delta_time
        self.update_player_speed()
        self.physics_engine.update()

        # Update player state based on movement
        self.player.update_state(delta_time)

        # Update player animation
        self.player.animate(delta_time)

        # Update all enemies
        self.update_enemies(delta_time)

        # Update bullets
        self.bullet_list.update(delta_time)

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        # Update the cameras to match the new window size
        self.camera.match_window()
        # The position argument keeps `0, 0` in the bottom left corner.
        self.camera_gui.match_window(position=True)

        # Handle fullscreen detection - check if window dimensions match display dimensions
        display_width, display_height = arcade.get_display_size()

        # Handle fullscreen detection
        if width == display_width and height == display_height:
            # We\'re in fullscreen or maximized
            self.window.set_fullscreen(True)
        elif self.window.fullscreen and (
            width < display_width or height < display_height
        ):
            # We were in fullscreen but now in a smaller window
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
