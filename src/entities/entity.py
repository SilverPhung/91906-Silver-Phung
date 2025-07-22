import arcade
from arcade.math import rotate_point
from arcade.types import Point2List
from pyglet.math import Vec2, clamp
import math
import json
import os
from enum import Enum
from src.sprites.indicator_bar import IndicatorBar
from src.constants import *

# path, width, height, anchor_x, anchor_y
ImageData = tuple[str, float, float, float, float]  # Define the type alias


class EntityState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DYING = "dying"


class AnimationData(Enum):
    MOVEMENT = "Movement"
    ACTION = "Action"


class Entity(arcade.Sprite):
    """Base class for all entities in the game (players, enemies)"""

    def __init__(
        self,
        image_path,
        scale,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        character_config: dict = None,
        character_preset: str = None,
    ):
        super().__init__(image_path, scale=scale)

        self.speed = speed
        self.position: tuple[float, float] = (0, 0)
        self.velocity: tuple[float, float] = (0, 0)
        self.friction = clamp(friction, 0, 1)
        self.delta_time = WINDOW_RATE

        # Animation properties moved from Character_Display_Sprite
        self.animations = {}
        self.processed_textures = (
            {}
        )  # New dictionary to hold processed arcade.Texture objects
        self.current_animation = None
        self.current_animation_frame = 0
        self.current_animation_time = 0
        self.animation_fps = 10
        self.frame_duration = 1.0 / self.animation_fps

        # Base state
        self.state = EntityState.IDLE
        self.facing_direction = 0
        self._is_loading = False  # New attribute to track loading status

        # Health attributes
        self.max_health = 100
        self.current_health = 100
        self.health_bar = None  # Will hold an instance of IndicatorBar

        self.character_config = character_config
        self.character_preset = character_preset

    def draw(self):
        """Draw the entity, including its health bar."""
        super().draw()

    def take_damage(self, damage_amount: float):
        """Reduce entity health and handle death."""
        self.current_health -= damage_amount
        if self.current_health <= 0:
            self.current_health = 0
            self.die()  # Trigger death animation or removal
        if self.health_bar:
            self.health_bar.fullness = self.current_health / self.max_health

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

    def load_animation_sequence(
        self, name: str, animation_data: dict, animation_type: AnimationType
    ):
        self.animations[name] = {
            "type": animation_data["type"],
            "width": animation_data["width"],
            "height": animation_data["height"],
            "anchor_x": animation_data["anchor_x"],
            "anchor_y": animation_data["anchor_y"],
            "sequence": [],
            "idle": arcade.Texture,
        }

        # Process the raw animation sequence
        processed_sequence = []
        for frame_path in animation_data["frames"]:
            processed_frame = process_loaded_texture_data(
                ImageData(
                    frame_path,
                    animation_data["width"],
                    animation_data["height"],
                    animation_data["anchor_x"],
                    animation_data["anchor_y"],
                )
            )
            processed_sequence.append(processed_frame)

        self.animations[name]["sequence"] = processed_sequence
        self.animations[name]["idle"] = processed_sequence[0]

    def load_animations(self):
        """Synchronous method to load player animations from configuration file"""
        if (
            not self.character_config
            or self.character_preset not in self.character_config
        ):
            print(
                f"No configuration found for player preset: {self.character_preset}"
            )
            self._is_loading = False
            return

        character_data = self.character_config[self.character_preset]
        animation_dict = {}
        total_frames = 0

        # Load animations from configuration
        for animation_name, animation_config in character_data.items():

            self.load_animation_sequence(animation_name, animation_config)

            # Create idle animations from first frame of walk animations
            if animation_name.startswith("Walk_"):
                weapon_type = animation_name[5:]
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
                ]:
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

        # Process loaded textures into arcade.Texture objects
        for anim_name, animation_info in self.animations.items():
            if "sequence" in animation_info and animation_info["sequence"]:
                for raw_frame_data in animation_info["sequence"]:
                    frame_path = raw_frame_data[0]
                    if frame_path not in self.processed_textures:
                        try:
                            (
                                texture,
                                offset,
                            ) = super().process_loaded_texture_data(
                                raw_frame_data
                            )
                            self.processed_textures[frame_path] = (
                                texture,
                                offset,
                            )
                        except Exception as e:
                            print(
                                f"Error processing and storing texture {frame_path}: {e}"
                            )
            if "idle" in animation_info and animation_info["idle"]:
                raw_frame_data = animation_info["idle"]
                frame_path = raw_frame_data[0]
                if frame_path not in self.processed_textures:
                    try:
                        texture, offset = super().process_loaded_texture_data(
                            raw_frame_data
                        )
                        self.processed_textures[frame_path] = (texture, offset)
                    except Exception as e:
                        print(
                            f"Error processing and storing idle texture {frame_path}: {e}"
                        )

        self._is_loading = False

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

                    # Update the sprite's texture and apply offset
                    # Lookup processed texture
                    current_frame_raw_data = animation_frames[
                        self.current_animation_frame
                    ]
                    current_frame_key = current_frame_raw_data[
                        0
                    ]  # Use path as key
                    if current_frame_key in self.processed_textures:
                        texture, offset = self.processed_textures[
                            current_frame_key
                        ]
                        self._apply_texture_and_offset(texture, offset)
                    else:
                        # Use a fallback texture if the processed texture is not yet available
                        print(
                            f"DEBUG: {self.__class__.__name__} processed_textures keys: {self.processed_textures.keys()}"
                        )
                        fallback_texture = arcade.make_soft_square_texture(
                            32,
                            arcade.color.MAGENTA,
                            name="fallback_anim",
                        )
                        self._apply_texture_and_offset(
                            fallback_texture, (0, 0)
                        )
                        print(
                            f"Warning: Processed texture for {current_frame_key} not found during animation. Using fallback."
                        )

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
            first_frame_key = first_frame_raw_data[0]  # Use path as key
            if first_frame_key in self.processed_textures:
                first_frame_texture, first_frame_offset = (
                    self.processed_textures[first_frame_key]
                )
                self._apply_texture_and_offset(
                    first_frame_texture, first_frame_offset
                )
            else:
                # Use a fallback texture if the processed texture is not yet available
                print(
                    f"DEBUG: {self.__class__.__name__} processed_textures keys in set_animation: {self.processed_textures.keys()}"
                )
                fallback_texture = arcade.make_soft_square_texture(
                    32,
                    arcade.color.MAGENTA,
                    name="fallback_setanim",
                )
                self._apply_texture_and_offset(fallback_texture, (0, 0))
                print(
                    f"Warning: Processed texture for {first_frame_key} not found. Using fallback."
                )
        elif animation_name in self.animations and self.animations[
            animation_name
        ].get("idle"):
            # If it's an idle animation, it might only have an "idle" texture and no sequence
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            # Lookup processed idle texture
            idle_raw_data = self.animations[animation_name]["idle"]
            idle_key = idle_raw_data[0]  # Use path as key
            if idle_key in self.processed_textures:
                idle_texture, idle_offset = self.processed_textures[idle_key]
                self._apply_texture_and_offset(idle_texture, idle_offset)
            else:
                # Use a fallback texture if the processed texture is not yet available
                fallback_texture = arcade.make_soft_square_texture(
                    32, arcade.color.BLUE, name="fallback_setanim_idle"
                )
                self._apply_texture_and_offset(fallback_texture, (0, 0))
                print(
                    f"Warning: Processed idle texture for {idle_key} not found. Using fallback."
                )
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
        dx = target_pos[0] - self.center_x
        dy = target_pos[1] - self.center_y
        angle = math.atan2(dx, dy) * 180 / math.pi
        self.angle = angle

        # Set facing based on angle
        self.facing_direction = angle

    def update_physics(self):
        """Update physics calculations"""
        # Apply friction directly to change_x and change_y
        # friction
        friction_factor = (1 - self.friction) ** (self.delta_time)
        self.velocity *= friction_factor

        # Clamp the velocity (change_x, change_y) to the max speed
        velocity_length = math.sqrt(self.velocity.x**2 + self.velocity.y**2)

        if velocity_length > self.speed:
            normalized_x = self.velocity.x / velocity_length
            normalized_y = self.velocity.y / velocity_length
            self.velocity = Vec2(
                normalized_x * self.speed, normalized_y * self.speed
            )

    def update_state(self, delta_time: float):
        """Update entity state based on velocity and other factors - to be overridden by child classes"""
        pass

    def die(self):
        """Trigger death animation"""
        self.state = EntityState.DYING


def load_texture_with_anchor(
    frame_path: str, animation_config: dict
) -> ImageData:  # Use the type alias for return
    """Load raw image data and return properties from animation configuration."""
    try:
        image_width = animation_config.get("width", 128)
        image_height = animation_config.get("height", 128)
        anchor_x = animation_config.get("anchor_x", image_width / 2)
        anchor_y = animation_config.get("anchor_y", image_height / 2)

        return frame_path, image_width, image_height, anchor_x, anchor_y

    except Exception as e:
        print(f"Error processing image path {frame_path}: {e}")
        return "", 0, 0, 0, 0  # Return empty data on error


def process_loaded_texture_data(
    raw_texture_data: ImageData,  # Use the type alias
) -> tuple[arcade.Texture, tuple[float, float]]:
    """Loads arcade.Texture from raw image data on the main thread."""
    frame_path, image_width, image_height, anchor_x, anchor_y = (
        raw_texture_data
    )

    def return_fallback_texture():
        fallback_texture = arcade.make_soft_square_texture(
            64, arcade.color.RED, name="fallback"
        )
        return fallback_texture, (0, 0)

    if not frame_path:
        # Handle the error case from load_texture_with_anchor
        return return_fallback_texture()
    else:
        try:
            texture = arcade.load_texture(frame_path)
            texture = (
                texture.flip_vertically()
            )  # Flip vertically since the characters are pointed down
        except Exception as e:
            print(
                f"ERROR: Failed to load arcade.Texture for {frame_path}: {e}"
            )
            return return_fallback_texture()

    # Calculate offset from image center to desired center of mass
    image_center_x = image_width / 2
    image_center_y = image_height / 2

    # Calculate offset (how much to move sprite from its current center)
    offset_x = image_center_x - anchor_x
    offset_y = image_center_y - anchor_y

    return texture, (offset_x, offset_y)
