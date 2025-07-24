import random
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
        speed=int(PLAYER_MOVEMENT_SPEED * 0.8),
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
        self.detection_range = 700
        self.attack_range = 100
        self.physics_range = 1000
        self.damage = 10 
        self.change_state(EntityState.IDLE)
        self.random_move_timer = ZOMBIE_RANDOM_MOVE_INTERVAL
        self.random_move_point = Vec2(0, 0)


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


    def hunt_player(self, delta_time: float):
        if self.player and self.animation_allow_overwrite:
            player_pos_vec = Vec2(self.player.position[0], self.player.position[1])
            enemy_pos_vec = Vec2(self.position[0], self.position[1])
            diff = player_pos_vec - enemy_pos_vec
            distance = diff.length()
            if distance < self.attack_range:
                self.move(Vec2(0, 0))
                self.attack()
                self.look_at(player_pos_vec)
            elif distance < self.detection_range:
                self.goto_point(player_pos_vec)
                self.look_at(player_pos_vec)
            elif distance < self.physics_range:
                self.goto_point(self.random_move_point)
                self.look_at(self.random_move_point)
                self.random_move_timer += delta_time
                if self.random_move_timer >= ZOMBIE_RANDOM_MOVE_INTERVAL:
                    self.random_move_timer = 0
                    self.random_move_point = self.position + Vec2(random.randint(-1000, 1000), random.randint(-1000, 1000))
            else:
                self.change_state(EntityState.IDLE)

    def update_state(self, delta_time: float):
        # super().update_state(delta_time)
        self.hunt_player(delta_time)

        # animation debug
        Debug.update(
            "Zombie Animation type", self.current_animation_type
        )
        Debug.update(
            "Zombie Animation state", self.state
        )
        Debug.update(
            "Zombie Animation frame", self.current_animation_frame
        )
        Debug.update(
            "Zombie Animation allow overwrite", self.animation_allow_overwrite
        )




    