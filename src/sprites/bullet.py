import arcade
import math
from pyglet.math import Vec2
from src.constants import *


class Bullet(arcade.Sprite):
    """Bullet class for ray casting visual."""

    def __init__(
        self,
        start_position: tuple[float, float],
        end_position: tuple[float, float],
        bullet_speed: float = BULLET_SPEED,
        bullet_lifetime: float = BULLET_LIFE,
        **kwargs,
    ):
        # Create a yellow rectangle texture for the bullet
        bullet_texture = arcade.make_soft_square_texture(
            20, arcade.color.YELLOW, name="bullet"
        )
        super().__init__(path_or_texture=bullet_texture, scale=(0.5, 10), **kwargs)
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

        self.angle = math.degrees(math.atan2(normalized_direction_x, normalized_direction_y))
        self.velocity = (
            normalized_direction_x * bullet_speed,
            normalized_direction_y * bullet_speed,
        )

        self.lifetime = bullet_lifetime

    def on_update(self, delta_time: float):
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        self.center_x += self.velocity[0] * delta_time
        self.center_y += self.velocity[1] * delta_time

    def draw(self):
        # No longer drawing a line, as it's a sprite now
        pass 