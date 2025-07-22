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
from src.debug import Debug

# path, width, height, anchor_x, anchor_y
RawTextureData = tuple[str, tuple[float, float], tuple[float, float]]  # Define the type alias

# texture, offset
TextureData = tuple[arcade.Texture, tuple[float, float]]  # Define the type alias


class EntityState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DYING = "dying"


class AnimationType(Enum):
    IDLE = "Idle"
    MOVEMENT = "Movement"
    ACTION = "Action"


class Entity(arcade.Sprite):
    """Base class for all entities in the game (players, enemies)"""

    def __init__(
        self,
        scale,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        character_config: dict = None,
        character_preset: str = None,
        show_health_indicator: arcade.SpriteList = None,
    ):
        super().__init__(scale=scale)

        self.speed = speed
        self.position: tuple[float, float] = (0, 0)
        self.velocity: tuple[float, float] = (0, 0)
        self.friction = clamp(friction, 0, 1)
        self.delta_time = WINDOW_RATE

        # Animation properties moved from Character_Display_Sprite
        self.animations = {}
        self.current_animation = None
        self.current_animation_type = None
        self.current_animation_frame = 0
        self.current_animation_time = 0
        self.animation_allow_overwrite = True
        self.animation_fps = 10
        self.frame_duration = 1.0 / self.animation_fps

        # Base state
        self.state = EntityState.IDLE
        self.facing_direction = 0
        self._is_loading = False  # New attribute to track loading status

        # Health attributes
        self.max_health = MAX_HEALTH
        self.current_health = self.max_health
        self.health_bar = None
        if show_health_indicator:
            self.health_bar = IndicatorBar(
                self,
                show_health_indicator,
                (self.center_x, self.center_y),
                width=HEALTHBAR_WIDTH,
                height=HEALTHBAR_HEIGHT,
            )

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

    def _apply_texture_and_offset(self, texture: TextureData):
        """Helper to set texture and apply offset to center_x, center_y"""
        self.texture = texture[0]
        self.sync_hit_box_to_texture()

    def load_animation_sequence(
        self, name: str, animation_data: dict
    ):

        self.animations[name] = {
            "type": animation_data["animation_type"],
            "width": animation_data["width"],
            "height": animation_data["height"],
            "anchor_x": animation_data["anchor_x"],
            "anchor_y": animation_data["anchor_y"],
            "frames": [],
        }

        # Process the raw animation sequence
        processed_sequence = []
        for frame_path in animation_data["frames"]:
            processed_frame = process_loaded_texture_data(
                RawTextureData((
                    frame_path,
                    (animation_data["width"],
                    animation_data["height"]),
                    (animation_data["anchor_x"], animation_data["anchor_y"]))
                )
            )
            processed_sequence.append(processed_frame)

        self.animations[name]["frames"] = processed_sequence

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

        # Load animations from configuration
        for animation_name, animation_config in character_data.items():
            self.load_animation_sequence(animation_name, animation_config)


        self._is_loading = False

    def _animation_exists_and_has_frames(self, anim_name: str) -> bool:
        """Helper to check if an animation exists and has a sequence or idle texture."""
        return anim_name in self.animations and (
            self.animations[anim_name].get("frames")
        )

    def _try_set_animation(self, anim_name: str) -> bool:
        """Helper to attempt setting an animation if it exists and has frames. Returns True if set, False otherwise."""
        if self._animation_exists_and_has_frames(anim_name):
            self.set_animation(anim_name)
            return True
        return False

    def animate(self, delta_time: float):
        """Update animation based on delta time"""
        if self.current_animation is None:
            return

        self.current_animation_time += delta_time
        animation_frames = None

        Debug.update("Current Animation frame", self.current_animation_frame)

        # Check if it's time to advance to the next frame
        if self.current_animation_time >= self.frame_duration:
            self.current_animation_time = 0

            # Get the current animation frames
            if self.current_animation in self.animations:
                animation_data = self.animations[self.current_animation]
                animation_frames = animation_data["frames"]
            else:
                print(
                    f"Warning: Animation '{self.current_animation}' not found."
                )
                return
            

            if animation_frames:
                if self.state == EntityState.IDLE:
                    self.current_animation_frame = 0
                    self.animation_allow_overwrite = True
                else:
                    self.current_animation_type = AnimationType(animation_data["type"])
                    print("process Current Animation Type", self.current_animation_type)
                    Debug.update("Current Animation type", self.current_animation_type)
                    match self.current_animation_type:
                        case AnimationType.MOVEMENT:
                            self.current_animation_frame = (
                                self.current_animation_frame + 1
                            ) % len(animation_frames)
                            self.animation_allow_overwrite = True
                        case AnimationType.ACTION:
                            self.animation_allow_overwrite = self.current_animation_frame == len(animation_frames) - 1
                            if not self.animation_allow_overwrite:
                                self.current_animation_frame += 1

                    self._apply_texture_and_offset(animation_frames[self.current_animation_frame])


    def set_animation(self, animation_name: str):
        """Set the current animation by name"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            animation_data = self.animations[animation_name]
            self.current_animation_type = AnimationType(animation_data["type"])
            self._apply_texture_and_offset(animation_data["frames"][0])
            
            if self.current_animation_type == AnimationType.ACTION:
                self.animation_allow_overwrite = False

    def change_state(self, new_state: EntityState, set_animation) -> bool:
        if self.state != new_state:
            self.state = new_state
            set_animation()
            return True
        return False

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state"""
        pass

    def look_at(self, target_pos: Vec2):
        """Update facing direction to look at target"""
        # Calculate angle between enemy and target
        dx = target_pos[0] - self.center_x
        dy = target_pos[1] - self.center_y
        angle = math.atan2(dx, dy) * 180 / math.pi
        self.angle = angle

        # Set facing based on angle
        self.facing_direction = angle

    def move(self, direction: Vec2):
        """Move the entity in the given direction"""
        if direction.length() > 0:
            self.velocity = direction * self.speed * self.delta_time

        self.update_physics()

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
        if self.velocity.length() > DEAD_ZONE:
            self.state = EntityState.WALKING
        else:
            self.state = EntityState.IDLE

    def die(self):
        """Trigger death animation"""
        self.state = EntityState.DYING


def process_loaded_texture_data(
    raw_texture_data: RawTextureData,  # Use the type alias
) -> TextureData:
    """Loads arcade.Texture from raw image data on the main thread."""
    frame_path, (image_width, image_height), (anchor_x, anchor_y) = (
        raw_texture_data
    )

    def return_fallback_texture():
        fallback_texture = arcade.make_soft_square_texture(
            64, arcade.color.RED, name="fallback"
        )
        return TextureData(fallback_texture, (0, 0))

    if not frame_path:
        return return_fallback_texture()
    else:
        try:
            texture = arcade.load_texture(frame_path)
            texture = texture.flip_vertically()
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

    return TextureData((texture, (offset_x, offset_y)))

def process_raw_texture_data(
    raw_texture_data: RawTextureData,
) -> TextureData:
    return process_loaded_texture_data(raw_texture_data)

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