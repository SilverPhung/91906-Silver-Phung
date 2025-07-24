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
        game_view: arcade.View,
        scale,
        friction=PLAYER_FRICTION,
        speed=ZOMBIE_MOVEMENT_SPEED,
        character_preset="Army_zombie",
        character_config=ZOMBIE_CONFIG_FILE,
        player_ref: Player | None = None,
    ):
        super().__init__(
            game_view=game_view,
            scale=scale,
            friction=friction,
            speed=speed,
            character_config=character_config,
            character_preset=character_preset,
        )

        self.load_animations(character_preset, character_config)

        self.player = player_ref
        self.attack_range = 50
        self.detection_range = 300
        self.change_state(EntityState.IDLE)

        self.health_bar = IndicatorBar(
            self,
            game_view.bar_list,
            (self.center_x, self.center_y),
            width=HEALTHBAR_WIDTH,
            height=HEALTHBAR_HEIGHT,
        )
        self.current_health = self.max_health
        self.health_bar.fullness = 1.0

    def change_state(self, new_state: EntityState):
        super().change_state(new_state)

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state"""
        if self.animation_allow_overwrite:
            match self.state:
                case EntityState.WALKING | EntityState.IDLE:
                    if self._try_set_animation("Walk"):
                        return

                case EntityState.ATTACKING:
                    if self._try_set_animation("Attack"):
                        self.current_animation_frame = 0
                        return

                case EntityState.DYING:
                    if self._try_set_animation("Death"):
                        return
    
    def goto_point(self, point: Vec2):
        enemy_pos_vec = Vec2(self.position[0], self.position[1])
        diff = point - enemy_pos_vec
        distance = diff.length()
        if distance < 1:
            self.move(Vec2(0, 0))
            self.change_state(EntityState.IDLE)
            return
        self.move(diff.normalize())
        self.change_state(EntityState.WALKING)

    def attack(self):
        """Trigger attack animation"""
        if self.state != EntityState.DYING:
            self.change_state(EntityState.ATTACKING)

    def die(self):
        """Trigger death animation"""
        self.change_state(EntityState.DYING)

    def update(self, delta_time: float):
        check_physics = True
        if self.state == EntityState.IDLE or self.state == EntityState.DYING:
            check_physics = False

        super().update(delta_time, check_physics)
