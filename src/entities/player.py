import arcade
from pyglet.math import Vec2
from src.entities.entity import *
from src.extended import to_vector
from src.sprites.indicator_bar import IndicatorBar
from src.debug import Debug
from enum import Enum
from src.constants import *
from src.sprites.bullet import Bullet


class WeaponType(Enum):
    BAT = "Bat"
    GUN = "Gun"
    KNIFE = "Knife"
    RIFLE = "Riffle"
    FLAMETHROWER = "FlameThrower"


class Player(Entity):
    """Player class representing the user-controlled character"""

    def __init__(
        self,
        game_view: arcade.View,
        player_preset="Man",
        config_file=PLAYER_CONFIG_FILE,
        scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        shoot_cooldown=SHOOT_COOLDOWN,
        reset_on_death=True,
        spawn_position=SPAWN_POSITION,
        sound_set={},
    ):
        super().__init__(
            scale=scale,
            friction=friction,
            speed=speed,
            character_config=config_file,
            character_preset=player_preset,
            game_view=game_view,
        )

        self.game_view = game_view

        self.reset_on_death = reset_on_death
        self.spawn_position = spawn_position

        self.load_animations(player_preset, config_file, game_view)

        # Player-specific properties

        self.mouse_position = (0.0, 0.0)

        # Weapon handling
        self.current_weapon = WeaponType.GUN

        self.current_health = self.max_health

        self.shoot_cooldown = shoot_cooldown
        self.shoot_cooldown_timer = 0

        self.sound_set = sound_set
        self.load_sounds(sound_set)

        # Get wall_list from MapManager if available, otherwise use empty list
        wall_list = []
        if (
            hasattr(self.game_view, "map_manager")
            and self.game_view.map_manager
        ):
            wall_list = [self.game_view.map_manager.get_wall_list()]
        elif hasattr(self.game_view, "wall_list") and self.game_view.wall_list:
            wall_list = [self.game_view.wall_list]

        self.physics_engine = arcade.PhysicsEngineSimple(
            self,
            wall_list,
        )

        # Store reference to update physics engine later
        self._wall_list = wall_list

        # Track position changes
        self._last_position = self.position

        # Update physics engine immediately if MapManager is available
        self.update_physics_engine()

    def set_weapon(self, weapon_type: WeaponType):
        """Set the current weapon"""
        self.current_weapon = weapon_type
        self.set_animation_for_state()

    def _find_and_set_prefixed_animation(
        self, prefix: str, weapon_name: str, fallback_prefix: str
    ):
        """Find and set animations with prefix and fallbacks."""
        # Try specific weapon animation
        specific_anim = f"{prefix}{weapon_name.lower()}"
        if self._try_set_animation(specific_anim):
            return

        # Try alternative cases for weapon name
        for anim_name in Entity.loaded_animations[self.character_preset]:
            if (
                anim_name.startswith(prefix)
                and weapon_name.lower() in anim_name.lower()
            ):
                if self._try_set_animation(anim_name):
                    return

        # Fallback to any animation with the prefix
        for anim_name in Entity.loaded_animations[self.character_preset]:
            if anim_name.startswith(fallback_prefix):
                if self._try_set_animation(anim_name):
                    return

        # Last resort - use any available animation
        for anim_name in Entity.loaded_animations[self.character_preset]:
            if self._try_set_animation(anim_name):
                print("Cannot find animation, using fallback", anim_name)
                return

    def change_state(self, new_state: EntityState):
        if super().change_state(new_state):
            # print("change state", new_state)
            pass

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state and weapon"""
        weapon_name = self.current_weapon.value

        Debug.update(
            "Animation allow overwrite", self.animation_allow_overwrite
        )

        match self.state:
            case EntityState.WALKING | EntityState.IDLE:
                if self.animation_allow_overwrite:

                    self._find_and_set_prefixed_animation(
                        "Walk_", weapon_name, "Walk_"
                    )

            case EntityState.ATTACKING:
                if self.current_weapon == WeaponType.GUN:
                    shoot_anim = "Gun_Shot"
                    self._try_set_animation(shoot_anim)
                    self.restart_animation()
                else:
                    if self._try_set_animation(weapon_name):
                        pass
                    else:
                        print("Cannot find attack animation, using fallback")
                        # Fallback to any attack animation (if not weapon_name specific)
                        for anim_name in Entity.loaded_animations[
                            self.character_preset
                        ]:
                            if anim_name in [
                                "Bat",
                                "FlameThrower",
                                "Knife",
                                "Riffle",
                            ]:
                                if self._try_set_animation(anim_name):
                                    break

            case EntityState.DYING:
                if self._try_set_animation("Death"):
                    return

        # Debug.update(
        #     "Selected Animation",
        #     str(self.current_animation) if self.current_animation else "None",
        # )

    def look_at(self, mouse_pos: Vec2):
        """Update facing direction based on mouse position"""
        self.mouse_position = mouse_pos
        super().look_at(mouse_pos)
        # Debug.update("Player Angle (internal)", f"{self.angle:.2f}")

    def attack(self):
        """Trigger an attack animation based on current weapon"""
        if self.state != EntityState.DYING:
            if self.current_weapon == WeaponType.GUN:
                self.shoot()
            else:
                self.attack_with_weapon()

    def shoot(self):
        """Trigger a shoot animation based on current weapon"""
        if (
            self.state != EntityState.DYING
            and self.shoot_cooldown_timer >= self.shoot_cooldown
        ):
            self.change_state(EntityState.ATTACKING)
            bullet = Bullet(
                self.position, self.mouse_position, bullet_damage=BULLET_DAMAGE
            )
            self.game_view.bullet_list.append(bullet)
            self.shoot_cooldown_timer = 0
            # Only play sound if sound_set exists and has gun_shot
            if self.sound_set and "gun_shot" in self.sound_set:
                self.play_sound(self.sound_set["gun_shot"])

    def attack_with_weapon(self):
        """Trigger an attack animation based on current weapon"""
        if self.state != EntityState.DYING:
            hit_list = arcade.check_for_collision_with_list(
                self, self.game_view.scene.get_sprite_list("Enemies")
            )
            self.change_state(EntityState.ATTACKING)
            for enemy in hit_list:
                enemy.take_damage(BULLET_DAMAGE)

    def die(self):
        """Trigger death animation"""
        if self.reset_on_death:
            self.reset()
        else:
            self.change_state(EntityState.DYING)

    def update(self, delta_time: float):
        super().update(delta_time)

        # Update physics engine with current wall list
        self.update_physics_engine()

        self.physics_engine.update()
        self.shoot_cooldown_timer += delta_time
        self.look_at(self.mouse_position)

        Debug.update("Player State", f"{self.state.value}")
        Debug.update(
            "Player Position",
            f"{self.position[0]:.0f}, {self.position[1]:.0f}",
        )
        Debug.update(
            "Player Velocity",
            f"{self.velocity[0]/delta_time:.2f}, {\
                self.velocity[1]/delta_time:.2f}",
        )

        Debug.update("Player Health", self.current_health)

        Debug.update("Current Animation", self.current_animation)

        Debug.update("Animation type", self.current_animation_type)

        Debug.update("Animation state", self.state)

    def reset_position(self):
        """Reset player position without recreation."""
        self.position = self.spawn_position
        self.velocity = Vec2(0.0, 0.0)
        self.change_x = 0.0
        self.change_y = 0.0
        # Debug logging removed to prevent infinite loops

    def update_spawn_position(self, new_position):
        """Update the spawn position for the current map."""
        self.spawn_position = new_position
        print(f"[PLAYER] Spawn position updated to: {new_position}")

    def reset_health(self):
        """Reset player health without recreation."""
        self.current_health = self.max_health
        if hasattr(self, "health_bar") and self.health_bar:
            self.health_bar.fullness = 1.0

    def reset(self):
        """Reset the player to initial state"""
        self.reset_health()
        self.state = EntityState.IDLE
        self.current_weapon = WeaponType.GUN
        self.reset_position()

    def update_physics_engine(self):
        """Update the physics engine with the current wall list from MapManager."""
        if (
            hasattr(self.game_view, "map_manager")
            and self.game_view.map_manager
        ):
            wall_list = self.game_view.map_manager.get_wall_list()
            if wall_list and wall_list != self._wall_list:
                self._wall_list = wall_list
                self.physics_engine = arcade.PhysicsEngineSimple(
                    self,
                    [wall_list],
                )
