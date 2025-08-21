from typing import cast
import arcade
import math
from pyglet.math import Vec2
from src.entities.entity import Entity
from src.constants import (
    BULLET_DAMAGE,
    BULLET_LIFE,
    BULLET_SPEED,
)


class Bullet(arcade.Sprite):
    """Bullet class for ray casting visual."""

    def __init__(
        self,
        start_position: tuple[float, float],
        end_position: tuple[float, float],
        bullet_speed: float = BULLET_SPEED,
        bullet_lifetime: float = BULLET_LIFE,
        bullet_damage: float = BULLET_DAMAGE,
        **kwargs,
    ):
        # Create a yellow rectangle texture for the bullet
        bullet_texture = arcade.make_soft_square_texture(
            20, arcade.color.YELLOW, name="bullet"
        )
        super().__init__(path_or_texture=bullet_texture, scale=(0.2, 5), **kwargs)
        diff = Vec2(
            end_position[0] - start_position[0], end_position[1] - start_position[1]
        )
        self.position = start_position + diff.normalize() * 5
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

        self.angle = math.degrees(
            math.atan2(normalized_direction_x, normalized_direction_y)
        )
        self.velocity = (
            normalized_direction_x * bullet_speed,
            normalized_direction_y * bullet_speed,
        )

        self.lifetime = bullet_lifetime
        self.damage = bullet_damage

    def update(
        self,
        delta_time: float,
        sprite_lists: list[arcade.SpriteList],
        wall_list: list[arcade.SpriteList],
    ):
        self._check_collision(sprite_lists)
        self._check_collision_with_walls(wall_list)
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        super().update(delta_time)

    def _check_collision(self, sprite_lists: list[arcade.SpriteList]):
        for sprite_list in sprite_lists:
            collisions = self.collides_with_list(sprite_list)
            for sprite in collisions:
                entity = cast(Entity, sprite)
                if entity.current_health > 0:
                    entity.take_damage(self.damage)
                    self.remove_from_sprite_lists()
                    return True
        return False

    def _check_collision_with_walls(self, wall_list: list[arcade.SpriteList]):
        for wall in wall_list:
            if self.collides_with_list(wall):
                self.remove_from_sprite_lists()
                return True
        return False

    def draw(self):
        # No longer drawing a line, as it's a sprite now
        pass
