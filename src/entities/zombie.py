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
        self.detection_range = 500
        self.engage_range = 150
        self.attack_range = 50
        self.physics_range = 10000
        self.damage = 10 
        self.change_state(EntityState.IDLE)
        self.random_move_timer = random.random() * ZOMBIE_RANDOM_MOVE_INTERVAL
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
            walk_random = False

            def engage_player(offset: True):
                self.goto_point(player_pos_vec + offset * Vec2(random.randint(-200, 200), random.randint(-200, 200)))
                look_at_point = self.path[0] if self.path else player_pos_vec
                self.look_at(look_at_point)
                
            if distance < self.attack_range:
                self.move(Vec2(0, 0))
                self.attack()
                self.look_at(player_pos_vec)
                return
            elif distance < self.detection_range:
                self.random_move_point = player_pos_vec
                engage_player(False)
                
                if self.path and len(self.path) > 1:
                    return
                else:
                    engage_player(True)
                    if not(self.path and len(self.path) > 1):
                        walk_random = True

            elif distance < self.physics_range:
                walk_random = True
            
            if walk_random:
                self.goto_point(self.random_move_point)
                self.look_at(self.random_move_point)
                self.random_move_timer += delta_time
                diff = self.random_move_point - enemy_pos_vec
                if self.random_move_timer >= ZOMBIE_RANDOM_MOVE_INTERVAL or diff.length() < 50:
                    self.pathfind_delay_timer = 0
                    self.random_move_timer = 0 
                    diff = player_pos_vec - enemy_pos_vec
                    self.random_move_point = enemy_pos_vec+diff.normalize()*150 + Vec2(random.randint(-100, 100), random.randint(-100, 100))
            else:
                self.move(Vec2(0, 0))
                self.change_state(EntityState.IDLE)

    def draw(self):
        super().draw()
        if self.random_move_point and ENABLE_DEBUG:
            arcade.draw_line_strip(
                self.transform_path([self.position, self.random_move_point]),
                arcade.color.RED,
                2,
            )

    def update_state(self, delta_time: float):
        # super().update_state(delta_time)
        if not self.state == EntityState.DYING:
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




    