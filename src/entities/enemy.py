import arcade
from pyglet.math import Vec2, clamp
import math
import json
import os
from src.entities.entity import Entity, EntityState
from src.entities.player import Player
from src.debug import Debug
from src.constants import *
from src.entities.entity import (
    load_texture_with_anchor,
    process_loaded_texture_data,
)

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


class Enemy(Entity):
    """Base class for all enemies (zombies, monsters)"""

    def __init__(
        self,
        image_path,
        scale,
        friction=PLAYER_FRICTION,
        speed=int(PLAYER_MOVEMENT_SPEED * 0.5),
        enemy_type="Army_zombie",
        player_ref: Player | None = None,
    ):
        super().__init__(
            image_path, scale=scale, friction=friction, speed=speed
        )

        self.enemy_type = enemy_type
        self.player = player_ref
        self.attack_range = 50

        # Load enemy configuration
        self.enemy_config = load_character_config(ZOMBIE_CONFIG_FILE)

        # Load animations
        self._is_loading = False

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
                textures.append(raw_texture_data)
                total_frames += 1

            if animation_name == "Walk" and textures:
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
                            texture, offset = process_loaded_texture_data(
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
                        texture, offset = process_loaded_texture_data(raw_frame_data)
                        self.processed_textures[frame_path] = (texture, offset)
                    except Exception as e:
                        print(f"Error processing and storing idle texture {frame_path}: {e}")

        self._is_loading = False

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
        if self.state == EntityState.DYING:
            return

        if self.state == EntityState.ATTACKING:
            if self.player:
                dx = self.player.position[0] - self.position[0]
                dy = self.player.position[1] - self.position[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > self.attack_range + 20:
                    self.state = EntityState.IDLE
                    self.set_animation_for_state()
                    return

        velocity_magnitude = math.sqrt(self.velocity.x**2 + self.velocity.y**2)

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