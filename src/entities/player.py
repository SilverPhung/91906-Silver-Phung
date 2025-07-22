import arcade
from pyglet.math import Vec2
from src.entities.entity import *
from src.extended import to_vector
from src.sprites.indicator_bar import IndicatorBar
from src.debug import Debug
from enum import Enum
from src.constants import *


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
        scale,
        friction=PLAYER_FRICTION,
        speed=PLAYER_MOVEMENT_SPEED,
        player_preset="Man",
        show_health_indicator: arcade.SpriteList = None,
    ):
        super().__init__(
            scale=scale,
            friction=friction,
            speed=speed,
            character_config=load_character_config(PLAYER_CONFIG_FILE),
            character_preset=player_preset,
        )
        # Player-specific properties

        self.mouse_position = (0.0, 0.0)

        # Weapon handling
        self.current_weapon = WeaponType.GUN

        self.current_health = self.max_health

    def set_weapon(self, weapon_type: WeaponType):
        """Set the current weapon"""
        self.current_weapon = weapon_type
        self.set_animation_for_state()

    def _find_and_set_prefixed_animation(
        self, prefix: str, weapon_name: str, fallback_prefix: str
    ):
        """Helper to find and set animations with a given prefix, with specific and generic fallbacks."""
        # Try specific weapon animation
        specific_anim = f"{prefix}{weapon_name.lower()}"
        if self._try_set_animation(specific_anim):
            return

        # Try alternative cases for weapon name
        for anim_name in self.animations:
            if (
                anim_name.startswith(prefix)
                and weapon_name.lower() in anim_name.lower()
            ):
                if self._try_set_animation(anim_name):
                    return

        # Fallback to any animation with the prefix
        for anim_name in self.animations:
            if anim_name.startswith(fallback_prefix):
                if self._try_set_animation(anim_name):
                    return

        # Last resort - use any available animation
        for anim_name in self.animations:
            if self._try_set_animation(anim_name):
                print("Cannot find animation, using fallback", anim_name)
                return

    def change_state(self, new_state: EntityState):
        if super().change_state(new_state, self.set_animation_for_state):
            print("change state", new_state)

    def set_animation_for_state(self):
        """Set the appropriate animation based on current state and weapon"""
        weapon_name = self.current_weapon.value

        match self.state:
            case EntityState.WALKING | EntityState.IDLE:
                self._find_and_set_prefixed_animation(
                    "Walk_", weapon_name, "Walk_"
                )

            case EntityState.ATTACKING:

                if self.current_weapon == WeaponType.GUN:
                    shoot_anim = "Gun_Shot"
                    self._try_set_animation(shoot_anim)
                else:
                    if (
                        self.current_animation != weapon_name
                        or self.current_animation == weapon_name
                        and self.current_animation_frame
                        == len(self.animations[weapon_name]["frames"]) - 1
                    ):
                        self._try_set_animation(weapon_name)
                    else:
                        print("Cannot find attack animation, using fallback")
                        # Fallback to any attack animation (if not weapon_name specific)
                        for anim_name in self.animations:
                            if anim_name in [
                                "Bat",
                                "FlameThrower",
                                "Knife",
                                "Riffle",
                            ]:
                                if self._try_set_animation(anim_name):
                                    break

            case EntityState.DYING:
                if self._animation_exists_and_has_frames("Death"):
                    self.set_animation("Death")

        Debug.update(
            "Selected Animation",
            str(self.current_animation) if self.current_animation else "None",
        )

    def update_state(self, delta_time: float):
        """Update player state based on velocity and other factors"""
        Debug.update(
            "Animation allow overwrite", self.animation_allow_overwrite
        )
        # print("player state", self.state, self.current_animation_type)

        # Allow shooting/attacking animation to finish before switching state
        # if (
        #     self.current_animation_type == AnimationType.ACTION
        #     and not self.animation_allow_overwrite
        # ):
        #     return

        velocity_magnitude = to_vector((self.change_x, self.change_y)).length()

        if velocity_magnitude > DEAD_ZONE:
            self.change_state(EntityState.WALKING)
        else:
            self.change_state(EntityState.IDLE)

    def look_at(self, mouse_pos: Vec2):
        """Update facing direction based on mouse position"""
        self.mouse_position = mouse_pos
        super().look_at(mouse_pos)
        Debug.update("Player Angle (internal)", f"{self.angle:.2f}")

    def attack(self):
        """Trigger an attack animation based on current weapon"""
        if self.state != EntityState.DYING:
            self.change_state(EntityState.ATTACKING)

    def die(self):
        """Trigger death animation"""
        self.change_state(EntityState.DYING)
