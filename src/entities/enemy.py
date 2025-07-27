import random
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

    pathfind_barrier = None

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

        if Enemy.pathfind_barrier is None:
            Enemy.pathfind_barrier = arcade.AStarBarrierList(
                moving_sprite=self,
                blocking_sprites=self.game_view.wall_list,
                grid_size=30,
                left=0,
                right=MAP_WIDTH_PIXEL,
                bottom=0,
                top=MAP_HEIGHT_PIXEL,
            )

        self.pathfind_delay = 1
        self.pathfind_delay_timer = random.random()
        self.path = None

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
        enemy_pos_vec = Vec2(self.center_x, self.center_y)

        self.pathfind_delay_timer += self.delta_time
        if self.pathfind_delay_timer >= self.pathfind_delay:
            self.pathfind_delay_timer = 0
            new_path = arcade.astar_calculate_path(
                enemy_pos_vec, point, self.pathfind_barrier, diagonal_movement=True
            )
            if new_path and len(new_path) > 1:
                self.path = new_path
                self.path.append(point)
            
            # print(self.path)

        if self.path and len(self.path) > 1:
            # goto_point = point if arcade.has_line_of_sight(self.position, point, self.game_view.wall_list, check_resolution=30) else self.path[0]
            
            goto_point = self.path[0]
            diff = goto_point - enemy_pos_vec
            distance = diff.length()
            if distance < Enemy.pathfind_barrier.grid_size:
                self.path.pop(0)
                return
            self.move(diff.normalize())
            self.change_state(EntityState.WALKING)
        else:
            self.move(Vec2(0, 0))
            self.change_state(EntityState.IDLE)
    def transform_path(self, path: list[Vec2]):
        return list(map(
            lambda point: (
                (point[0] - self.game_view.camera.position[0]) * self.game_view.camera.zoom
                + WINDOW_WIDTH / 2,
                (point[1] - self.game_view.camera.position[1]) * self.game_view.camera.zoom
                + WINDOW_HEIGHT / 2,
            ),
            path
        ))
    def draw(self):
        if self.path:
            arcade.draw_line_strip(
                self.transform_path(self.path),
                arcade.color.BLUE,
                2,
            )
        pass

    def attack(self):
        """Trigger attack animation"""
        if self.state != EntityState.DYING:
            self.change_state(EntityState.ATTACKING)
            self.player.take_damage(self.damage)

    def die(self):
        """Trigger death animation"""
        self.change_state(EntityState.DYING)

    def update(self, delta_time: float):
        update_physics = True
        if self.state == EntityState.IDLE:
            update_physics = False
        super().update(delta_time, update_physics=update_physics)
