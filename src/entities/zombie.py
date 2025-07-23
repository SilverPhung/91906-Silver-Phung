from src.entities.enemy import *
from src.entities.player import Player
from src.constants import *


class Zombie(Enemy):
    """Specific implementation for zombie enemies"""

    def __init__(
        self,
        game_view: arcade.View,
        zombie_type="Army_zombie",
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=int(PLAYER_MOVEMENT_SPEED * 0.4),
        player_ref: Player | None = None,
        config_file=ZOMBIE_CONFIG_FILE,
    ):
        super().__init__(
            game_view=game_view,
            scale=scale,
            friction=friction,
            speed=speed,
            character_config=config_file,
            character_preset=zombie_type
        )

        self.player = player_ref

        # Zombie-specific properties
        self.detection_range = 300
        self.attack_range = 50
        self.damage = 10 
        self.change_state(EntityState.IDLE)

        # Add health bar to zombie
        self.health_bar = IndicatorBar(
            self,
            game_view.bar_list,
            (self.center_x, self.center_y),
            width=HEALTHBAR_WIDTH,
            height=HEALTHBAR_HEIGHT,
        )
        self.current_health = self.max_health
        self.health_bar.fullness = 1.0

        # Add zombie to game view lists and create physics engine
        game_view.enemies.append(self)
        game_view.scene.add_sprite("Enemies", self)

        physics_engine = arcade.PhysicsEngineSimple(
            self,
            game_view.scene.get_sprite_list("Walls"),
        )
        game_view.enemy_physics_engines.append(physics_engine)
    
    