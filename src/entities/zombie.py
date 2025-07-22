from src.entities.enemy import Enemy
from src.entities.player import Player
from src.constants import *


class Zombie(Enemy):
    """Specific implementation for zombie enemies"""

    def __init__(
        self,
        zombie_type="Army_zombie",
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=int(PLAYER_MOVEMENT_SPEED * 0.4),
        player_ref: Player | None = None,
    ):
        super().__init__(
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