import arcade
from pyglet.math import Vec2
from src.entities.entity import *
from src.entities.player import Player
from src.extended import to_vector
from src.sprites.indicator_bar import IndicatorBar
from src.debug import Debug
import math
from src.constants import *


class Enemy(Entity):
    """Base class for all enemies (zombies, monsters)"""

    def __init__(
        self,
        scale,
        friction=PLAYER_FRICTION,
        speed=ZOMBIE_MOVEMENT_SPEED,
        enemy_type="Army_zombie",
        player_ref: Player | None = None,
    ):
        super().__init__(
            scale=scale,
            friction=friction,
            speed=speed,
            character_config=load_character_config(ENEMY_CONFIG_FILE),
            character_preset=enemy_type,
        )

        self.state = EntityState.IDLE
        self.enemy_type = enemy_type
        self.player = player_ref
        self.attack_range = 50

    def change_state(self, new_state: EntityState):
        super().change_state(new_state, self.set_animation_for_state)

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state"""
        match self.state:
            case EntityState.IDLE:
                if self._try_set_animation("Idle"):
                    return

            case EntityState.WALKING:
                if self._try_set_animation("Walk"):
                    return

            case EntityState.ATTACKING:
                if self._try_set_animation("Attack"):
                    return

            case EntityState.DYING:
                if self._try_set_animation("Death"):
                    return

    def update_state(self, delta_time: float):
        """Update enemy state based on velocity and other factors"""
        # Allow action animation (e.g., attacking, dying) to finish before switching state
        if (
            self.current_animation_type == AnimationType.ACTION
            and not self.animation_allow_overwrite
        ):
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

        velocity_magnitude = to_vector((self.change_x, self.change_y)).length()

        if velocity_magnitude > DEAD_ZONE:
            self.change_state(EntityState.WALKING)
        else:
            self.change_state(EntityState.IDLE)

    def attack(self):
        """Trigger attack animation"""
        if self.state != EntityState.DYING:
            self.change_state(EntityState.ATTACKING)

    def die(self):
        """Trigger death animation"""
        self.change_state(EntityState.DYING)
