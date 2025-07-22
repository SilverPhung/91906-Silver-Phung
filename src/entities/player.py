import arcade
from pyglet.math import Vec2
from src.entities.entity import Entity, EntityState
from src.sprites.indicator_bar import IndicatorBar
from src.debug import Debug
import math
import json
import os
from enum import Enum
from src.constants import *

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


class Player(Entity):
    """Player class representing the user-controlled character"""

    def __init__(
        self,
        image_path,
        scale,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        player_preset="Man",
        bar_list: arcade.SpriteList = None,
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
        self._is_loading = False

        self.current_health = self.max_health
        if bar_list:
            self.health_bar = IndicatorBar(
                self,
                bar_list,
                (self.center_x, self.center_y),
                width=HEALTHBAR_WIDTH,
                height=HEALTHBAR_HEIGHT,
            )

    def load_animations(self):
        """Synchronous method to load player animations from configuration file"""
        if (
            not self.character_config
            or self.player_preset not in self.character_config
        ):
            print(
                f"No configuration found for player preset: {self.player_preset}"
            )
            self._is_loading = False
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
                raw_texture_data = super().load_texture_with_anchor(
                    frame_path, animation_config
                )
                textures.append(raw_texture_data)
                total_frames += 1

            animation_dict[animation_name] = textures

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
                            texture, offset = super().process_loaded_texture_data(
                                raw_frame_data
                            )
                            self.processed_textures[frame_path] = (texture, offset)
                        except Exception as e:
                            print(f"Error processing and storing texture {frame_path}: {e}")
            if "idle" in animation_info and animation_info["idle"]:
                raw_frame_data = animation_info["idle"]
                frame_path = raw_frame_data[0]
                if frame_path not in self.processed_textures:
                    try:
                        texture, offset = super().process_loaded_texture_data(raw_frame_data)
                        self.processed_textures[frame_path] = (texture, offset)
                    except Exception as e:
                        print(f"Error processing and storing idle texture {frame_path}: {e}")

        self._is_loading = False

    def set_weapon(self, weapon_type: WeaponType):
        """Set the current weapon"""
        self.current_weapon = weapon_type
        self.set_animation_for_state()

    def _animation_exists_and_has_frames(self, anim_name: str) -> bool:
        """Helper to check if an animation exists and has a sequence or idle texture."""
        return anim_name in self.animations and (
            self.animations[anim_name].get("sequence")
            or self.animations[anim_name].get("idle")
        )

    def _try_set_animation(self, anim_name: str) -> bool:
        """Helper to attempt setting an animation if it exists and has frames. Returns True if set, False otherwise."""
        if self._animation_exists_and_has_frames(anim_name):
            self.set_animation(anim_name)
            return True
        return False

    def _find_and_set_prefixed_animation(
        self, prefix: str, weapon_name: str, fallback_prefix: str
    ):
        """Helper to find and set animations with a given prefix, with specific and generic fallbacks."""
        # Try specific weapon animation
        specific_anim = f"{prefix}{weapon_name.lower()}"
        if self._try_set_animation(specific_anim):
            return

        # Try alternative cases for weapon name
        for anim_name in self.animations:
            if anim_name.startswith(prefix) and weapon_name.lower() in anim_name.lower():
                if self._try_set_animation(anim_name):
                    return

        # Fallback to any animation with the prefix
        for anim_name in self.animations:
            if anim_name.startswith(fallback_prefix):
                if self._try_set_animation(anim_name):
                    return

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state and weapon"""
        weapon_name = self.current_weapon.value

        match self.state:
            case PlayerState.IDLE:
                Debug.update("Trying Idle Animation", f"Idle_{weapon_name.lower()}")
                self._find_and_set_prefixed_animation("Idle_", weapon_name, "Idle_")
                if not self.current_animation:  # If no idle animation was set yet
                    # Last resort - use any available idle animation
                    for anim_name in self.animations:
                        if anim_name.startswith("Idle_"):
                            self.set_animation(anim_name)
                            break

            case PlayerState.WALKING:
                self._find_and_set_prefixed_animation("Walk_", weapon_name, "Walk_")
                if not self.current_animation:  # If no walk animation was set yet
                    # Fallback to any walk animation
                    for anim_name in self.animations:
                        if anim_name.startswith("Walk_"):
                            self.set_animation(anim_name)
                            break

            case PlayerState.SHOOTING:
                shoot_anim = "Gun_Shot"
                if self._animation_exists_and_has_frames(shoot_anim):
                    if (
                        self.current_animation != shoot_anim
                        or self.current_animation == shoot_anim
                        and self.current_animation_frame
                        == len(self.animations[shoot_anim]["sequence"]) - 1
                    ):
                        self.set_animation(shoot_anim)

            case PlayerState.ATTACKING:
                # Try to use the specific attack animation for this weapon
                if self._animation_exists_and_has_frames(weapon_name):
                    if (
                        self.current_animation != weapon_name
                        or self.current_animation == weapon_name
                        and self.current_animation_frame
                        == len(self.animations[weapon_name]["sequence"]) - 1
                    ):
                        self.set_animation(weapon_name)
                else:
                    # Fallback to any attack animation (if not weapon_name specific)
                    for anim_name in self.animations:
                        if anim_name in [
                            "Bat",
                            "FlameThrower",
                            "Knife",
                            "Riffle",
                        ]:
                            if self._try_set_animation(anim_name):
                                break

            case PlayerState.DYING:
                if self._animation_exists_and_has_frames("Death"):
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
            if (
                current_anim_data
                and self.current_animation_frame
                == len(current_anim_data["sequence"]) - 1
            ):
                # Animation finished, transition to idle/walking
                velocity_magnitude = math.sqrt(self.velocity.x**2 + self.velocity.y**2)
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
        velocity_magnitude = math.sqrt(self.change_x**2 + self.change_y**2)

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
        Debug.update("Player Angle (internal)", f"{self.angle:.2f}")

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