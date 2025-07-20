import arcade
from arcade.experimental.crt_filter import CRTFilter
from arcade.math import rotate_point
from arcade.texture.transforms import Rotate180Transform, Transform, VertexOrder
from arcade.types import Point2List
import random
from pyglet.math import Vec2, clamp
import time
import os
import asyncio
from enum import Enum
import math
import json

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_RATE = 1 / 144  # 144hz

# Constants
CHARACTER_SCALING = 0.3
TILE_SCALING = 0.5
COLLECTABLE_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player Movement
PLAYER_MOVEMENT_SPEED = 1000
PLAYER_FRICTION = 0.99999

# Camera constants
FOLLOW_DECAY_CONST = (
    0.3  # get within 1% of the target position within 2 seconds
)

VIEWPORT_MARGIN = 250
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN

# Key constants
LEFT_KEY = arcade.key.LEFT
RIGHT_KEY = arcade.key.RIGHT
UP_KEY = arcade.key.UP
DOWN_KEY = arcade.key.DOWN
# WASD keys
W_KEY = arcade.key.W
A_KEY = arcade.key.A
S_KEY = arcade.key.S
D_KEY = arcade.key.D
# Fullscreen toggle
FULLSCREEN_KEY = arcade.key.F11

# Asset directories
PLAYER_ASSETS_DIR = "resources/Players"
ZOMBIE_ASSETS_DIR = "resources/Zombies"

# Configuration files
PLAYER_CONFIG_FILE = "resources/animation_config/players_config.json"
ZOMBIE_CONFIG_FILE = "resources/animation_config/zombies_config.json"

DEAD_ZONE = 0.1  # Minimum velocity to consider as moving

class EntityState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    DYING = "dying"

class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    SHOOTING = "shooting"
    ATTACKING = "attacking"
    DYING = "dying"

class WeaponType(Enum):
    BAT = "Bat"
    GUN = "Gun"
    KNIFE = "Knife"
    RIFLE = "Riffle"
    FLAMETHROWER = "FlameThrower"

def load_character_config(config_file: str) -> dict:
    """Load character configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_file}")
        print("Please run character_analyzer.py first to generate configuration files")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {config_file}: {e}")
        return {}



def load_texture_with_anchor(frame_path: str, animation_config: dict) -> tuple[arcade.Texture, tuple[float, float]]:
    """Load a texture and return both texture and center offset from animation configuration."""
    try:
        # Load texture normally (without anchor parameters which aren't supported)
        texture = arcade.load_texture(frame_path)

        # Calculate offset from image center to desired center of mass
        image_center_x = animation_config.get("width", 128) / 2
        image_center_y = animation_config.get("height", 128) / 2
        
        # Get desired center of mass from config (default to center if not specified)
        anchor_x = animation_config.get("anchor_x", image_center_x)
        anchor_y = animation_config.get("anchor_y", image_center_y)
        # print(f"Anchor: {anchor_x}, {anchor_y}")
        
        # Calculate offset (how much to move sprite from its current center)
        offset_x = image_center_x - anchor_x
        offset_y = image_center_y - anchor_y
        
        return texture, (offset_x, offset_y)
        
    except Exception as e:
        print(f"Error loading texture {frame_path}: {e}")
        # Return a fallback texture with no offset
        fallback_texture = arcade.make_soft_square_texture(32, arcade.color.RED, name="fallback")
        return fallback_texture, (0, 0)

def to_vector(point: tuple[float, float] | arcade.types.Point2 | Vec2) -> Vec2:
    return Vec2(point[0], point[1])


class Debug:
    debug_dict = {}
    text_objects = {}

    @staticmethod
    def update(key: str, text: str):
        Debug.debug_dict[key] = text
        if key in Debug.text_objects:
            Debug.text_objects[key].text = f"{key}: {text}"
        else:
            # Create a new Text object if it doesn't exist
            # Position will be set in render, but it needs an initial position
            Debug.text_objects[key] = arcade.Text(
                f"{key}: {text}",
                0, # placeholder x
                0, # placeholder y
                arcade.csscolor.WHITE,
                18,
            )

    @staticmethod
    def render(x: float, y: float):

        for key, text_object in Debug.text_objects.items():
            text_object.x = x
            text_object.y = y
            text_object.draw()
            y += 20

PLAYER_ANIMATION_STRUCTURE = {
    "Bat": 12,
    "Death": 6,
    "FlameThrower": 9,
    "Gun_Shot": 5,
    "Gun_Idle": 1,  # Custom idle animation
    "Knife": 8,
    "Riffle": 9,
    "Walk_bat": 6,
    "Walk_FireThrhrower": 6,
    "Walk_gun": 6,
    "Walk_knife": 6,
    "Walk_riffle": 6
}

class Character_Display_Sprite(arcade.Sprite):
    class AnimationType(Enum):
        MOVEMENT = "Movement"
        ATTACK = "Attack"
        DEATH = "Death"
        

    def __init__(self, image_path, scale=CHARACTER_SCALING, pivot_point: Vec2 = Vec2(0, 0)):
        super().__init__(image_path, scale=scale)
        self.position: Vec2 = Vec2(0, 0)
        self.pivot_point = pivot_point
        self.animations = {}

        # Basic animation properties
        self.animation = {}
        self.current_animation = None
        self.current_animation_frame = 0
        self.current_animation_time = 0
        self.animation_fps = 10
        self.frame_duration = 1.0 / self.animation_fps
        
        # Base state
        self.state = EntityState.IDLE
        self.facing_direction = 0

    def load_animation_sequence(self, name:str, animation_type: AnimationType, animation_sequence: list[tuple[str, Vec2]], idle_texture: str):
        # animation_sequence is a list of tuples, each containing a texture and a pivot point
        # Load a sequence of textures, and save it to the animation dictionary
        """
        "animations":{
            "Gun":{
                "type": "Movement",
                "Sequence":[Texture...],
                "Idle": Texture
            },
            ...
        }
        """

class Entity(arcade.Sprite):
    """Base class for all entities in the game (players, enemies)"""
    
    def __init__(
        self, image_path, scale=CHARACTER_SCALING, friction=PLAYER_FRICTION, speed=PLAYER_MOVEMENT_SPEED
    ):
        super().__init__(image_path, scale=scale)

        self.speed = speed
        self.position: Vec2 = Vec2(0, 0)
        self.velocity: Vec2 = Vec2(0, 0)
        self.friction = clamp(friction, 0, 1)
        self.delta_time = WINDOW_RATE

        self.display_sprite = Character_Display_Sprite(image_path, scale=scale)
        
        

    def move(self, direction: Vec2):
        """Move the entity in the given direction"""
        if direction.length() > 0:
            self.velocity = direction * self.speed * self.delta_time

        self.update_physics()

    def update_physics(self):
        """Update physics calculations"""
        # friction
        self.velocity = to_vector(self.velocity) * (1 - self.friction) ** (
            self.delta_time
        )

        # Clamp the velocity to the max speed
        velocity_length = self.velocity.length()

        self.velocity = self.velocity.normalize() * clamp(
            velocity_length, 0, self.speed
        )

    def animate(self, delta_time: float):
        """Update animation based on delta time"""
        if self.current_animation is None:
            return

        self.current_animation_time += delta_time

        # Check if it's time to advance to the next frame
        if self.current_animation_time >= self.frame_duration:
            self.current_animation_time = 0
            
            # Get the current animation frames
            if self.current_animation in self.animation:
                animation_frames = self.animation[self.current_animation]
                
                if animation_frames:
                    # Advance to next frame
                    self.current_animation_frame = (self.current_animation_frame + 1) % len(animation_frames)
                    
                    # Update the sprite's texture
                    self.texture = animation_frames[self.current_animation_frame][0]

    def set_animation(self, animation_name: str):
        """Set the current animation by name"""
        if animation_name in self.animation and self.animation[animation_name]:
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            # Set the first frame immediately
            self.texture = self.animation[animation_name][0][0]
    
    def update_state(self, delta_time: float):
        """Update entity state based on velocity and other factors - to be overridden by child classes"""
        pass
    
    def die(self):
        """Trigger death animation"""
        self.state = EntityState.DYING
        
class Player(Entity):
    """Player class representing the user-controlled character"""
    
    def __init__(
        self, image_path, scale=CHARACTER_SCALING, friction=PLAYER_FRICTION, speed=PLAYER_MOVEMENT_SPEED, player_preset="Girl"
    ):
        super().__init__(image_path, scale=scale, friction=friction, speed=speed)
        
        self.player_preset = player_preset
        
        # Player-specific properties
        self.state = PlayerState.IDLE
        self.mouse_position = Vec2(0, 0)
        
        # Weapon handling
        self.current_weapon = WeaponType.GUN
        
        # Load character configuration
        self.character_config = load_character_config(PLAYER_CONFIG_FILE)
        
        # Load animations
        asyncio.run(self.load_animation())
    
    async def load_animation(self):
        """Load player animations from configuration file"""
        if not self.character_config or self.player_preset not in self.character_config:
            print(f"No configuration found for player preset: {self.player_preset}")
            return
        
        character_data = self.character_config[self.player_preset]
        animation_dict = {}
        total_frames = 0
        
        # Load animations from configuration
        for animation_name, animation_config in character_data.items():
            textures = []
            
            # Get the list of frame paths from the animation config
            frame_paths = animation_config.get("frames", [])
            
            for frame_path in frame_paths:
                texture, offset = load_texture_with_anchor(frame_path, animation_config)
                textures.append((texture, offset)) # Store texture and offset as a tuple
                total_frames += 1
            
            animation_dict[animation_name] = textures
            
            # Create idle animations from first frame of walk animations
            if animation_name.startswith("Walk_"):
                weapon_type = animation_name[5:]  # Remove "Walk_" prefix
                idle_key = f"Idle_{weapon_type}"
                if textures:
                    animation_dict[idle_key] = [textures[0]] # Store texture and offset as a tuple for idle
                    total_frames += 1
        
        self.animation = animation_dict
        # Add summary debug info
        Debug.update(f"{self.player_preset} Animations", f"{len(animation_dict)} types, {total_frames} frames")
        Debug.update(f"Current Weapon", f"{self.current_weapon.name}")
    
    def set_weapon(self, weapon_type: WeaponType):
        """Set the current weapon"""
        self.current_weapon = weapon_type
        self.set_animation_for_state()
    
    def set_animation_for_state(self):
        """Set the appropriate animation based on current state and weapon"""
        weapon_name = self.current_weapon.value
        
        if self.state == PlayerState.IDLE:
            # Try to use the specific idle animation for this weapon
            idle_anim = f"Idle_{weapon_name.lower()}"
            Debug.update("Trying Idle Animation", idle_anim)
            
            if idle_anim in self.animation and self.animation[idle_anim]:
                self.set_animation(idle_anim)
            else:
                # If specific idle animation not found, try generic weapon idle
                # Check for matching weapon types with different case formats
                found = False
                for anim_name in self.animation:
                    if anim_name.startswith("Idle_") and weapon_name.lower() in anim_name.lower():
                        self.set_animation(anim_name)
                        found = True
                        break
                
                # If still not found, use any available idle animation as last resort
                if not found:
                    Debug.update("Fallback Animation", "Using first available idle")
                    weapon_priority = [self.current_weapon.value]  # Try current weapon first
                    for weapon in WeaponType:
                        if weapon != self.current_weapon:
                            weapon_priority.append(weapon.value)
                    
                    for weapon_type in weapon_priority:
                        idle_check = f"Idle_{weapon_type.lower()}"
                        if idle_check in self.animation and self.animation[idle_check]:
                            self.set_animation(idle_check)
                            found = True
                            break
                            
                    # Last resort - use any idle animation
                    if not found:
                        for anim_name in self.animation:
                            if anim_name.startswith("Idle_"):
                                self.set_animation(anim_name)
                                break
        
        elif self.state == PlayerState.WALKING:
            # Try exact match first
            walk_anim = f"Walk_{weapon_name.lower()}"
            
            # Then try alternative cases
            if not (walk_anim in self.animation and self.animation[walk_anim]):
                for anim_name in self.animation:
                    if anim_name.startswith("Walk_") and weapon_name.lower() in anim_name.lower():
                        walk_anim = anim_name
                        break
            
            if walk_anim in self.animation and self.animation[walk_anim]:
                self.set_animation(walk_anim)
            else:
                # Fallback to any walk animation
                for anim_name in self.animation:
                    if anim_name.startswith("Walk_"):
                        self.set_animation(anim_name)
                        break
        
        elif self.state == PlayerState.SHOOTING:
            shoot_anim = "Gun_Shot"
            if shoot_anim in self.animation and self.animation[shoot_anim]:
                self.set_animation(shoot_anim)
                
        elif self.state == PlayerState.ATTACKING:
            # Try to use the specific attack animation for this weapon
            if weapon_name in self.animation and self.animation[weapon_name]:
                self.set_animation(weapon_name)
            else:
                # Try to find a matching attack animation
                for anim_name in self.animation:
                    if weapon_name.lower() in anim_name.lower() and not anim_name.startswith("Walk_") and not anim_name.startswith("Idle_"):
                        self.set_animation(anim_name)
                        break
        
        elif self.state == PlayerState.DYING:
            if "Death" in self.animation and self.animation["Death"]:
                self.set_animation("Death")
                
        Debug.update("Selected Animation", str(self.current_animation) if self.current_animation else "None")
    
    def update_state(self, delta_time: float):
        """Update player state based on velocity and other factors"""
        # Skip state update if in the middle of an attack or death animation
        if self.state in [PlayerState.SHOOTING, PlayerState.ATTACKING, PlayerState.DYING]:
            return
            
        # Check if player is moving
        velocity_magnitude = to_vector(self.velocity).length()
        
        if velocity_magnitude > DEAD_ZONE:
            if self.state != PlayerState.WALKING:
                self.state = PlayerState.WALKING
                self.set_animation_for_state()
        else:
            if self.state != PlayerState.IDLE:
                self.state = PlayerState.IDLE
                self.set_animation_for_state()
    
    def update_facing_direction(self, mouse_pos: Vec2):
        """Update facing direction based on mouse position"""
        self.mouse_position = mouse_pos

        # Calculate angle between player and mouse position
        dx = self.mouse_position.x - self.position[0]
        dy = self.mouse_position.y - self.position[1]
        angle = math.atan2(dx, dy) * 180 / math.pi+180
        self.angle = angle
    
    def attack(self):
        """Trigger an attack animation based on current weapon"""
        if self.state not in [PlayerState.ATTACKING, PlayerState.SHOOTING, PlayerState.DYING]:
            if self.current_weapon == WeaponType.GUN:
                self.state = PlayerState.SHOOTING
            else:
                self.state = PlayerState.ATTACKING
            self.set_animation_for_state()
    
    def die(self):
        """Trigger death animation"""
        self.state = PlayerState.DYING
        self.set_animation_for_state()

class Enemy(Entity):
    """Base class for all enemies (zombies, monsters)"""
    
    def __init__(
        self, image_path, scale=CHARACTER_SCALING, friction=PLAYER_FRICTION, 
        speed=int(PLAYER_MOVEMENT_SPEED * 0.5), enemy_type="Army_zombie"
    ):
        super().__init__(image_path, scale=scale, friction=friction, speed=speed)
        
        self.enemy_type = enemy_type
        
        # Load enemy configuration
        self.enemy_config = load_character_config(ZOMBIE_CONFIG_FILE)
        
        # Load animations
        asyncio.run(self.load_animation())
        
        # Set initial animation
        self.set_animation_for_state()
    
    async def load_animation(self):
        """Load enemy animations from configuration file"""
        if not self.enemy_config or self.enemy_type not in self.enemy_config:
            print(f"No configuration found for enemy type: {self.enemy_type}")
            return
        
        enemy_data = self.enemy_config[self.enemy_type]
        animation_dict = {}
        total_frames = 0
        
        # Load animations from configuration
        for animation_name, animation_config in enemy_data.items():
            textures = []
            
            # Get the list of frame paths from the animation config
            frame_paths = animation_config.get("frames", [])
            
            for frame_path in frame_paths:
                texture, offset = load_texture_with_anchor(frame_path, animation_config)
                textures.append((texture, offset)) # Store texture and offset as a tuple
                total_frames += 1
            
            animation_dict[animation_name] = textures
            
            # Create idle animation from first frame of walk animation
            if animation_name == "Walk" and textures:
                animation_dict["Idle"] = [textures[0]] # Store texture and offset as a tuple for idle
                total_frames += 1
        
        self.animation = animation_dict
        Debug.update(f"{self.enemy_type} Animations", f"{len(animation_dict)} types, {total_frames} frames")
    
    def set_animation_for_state(self):
        """Set the appropriate animation based on current state"""
        if self.state == EntityState.IDLE:
            if "Idle" in self.animation and self.animation["Idle"]:
                self.set_animation("Idle")
        
        elif self.state == EntityState.WALKING:
            if "Walk" in self.animation and self.animation["Walk"]:
                self.set_animation("Walk")
        
        elif self.state == EntityState.ATTACKING:
            if "Attack" in self.animation and self.animation["Attack"]:
                self.set_animation("Attack")
        
        elif self.state == EntityState.DYING:
            if "Death" in self.animation and self.animation["Death"]:
                self.set_animation("Death")
    
    def update_state(self, delta_time: float):
        """Update enemy state based on velocity and other factors"""
        # Skip state update if in the middle of an attack or death animation
        if self.state in [EntityState.ATTACKING, EntityState.DYING]:
            return
            
        # Check if enemy is moving
        velocity_magnitude = to_vector(self.velocity).length()
        
        if velocity_magnitude > DEAD_ZONE:
            if self.state != EntityState.WALKING:
                self.state = EntityState.WALKING
                self.set_animation_for_state()
        else:
            if self.state != EntityState.IDLE:
                self.state = EntityState.IDLE
                self.set_animation_for_state()
    
    def attack(self):
        """Trigger attack animation"""
        if self.state not in [EntityState.ATTACKING, EntityState.DYING]:
            self.state = EntityState.ATTACKING
            self.set_animation_for_state()
    
    def update_facing_direction(self, target_pos: Vec2):
        """Update facing direction to look at target"""
        # Calculate angle between enemy and target
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        angle = math.atan2(dx, dy) * 180 / math.pi+180
        self.angle = angle
        
        # Set facing based on angle
        self.facing_direction = angle

class Zombie(Enemy):
    """Specific implementation for zombie enemies"""
    
    def __init__(
        self, image_path, zombie_type="Army_zombie", scale=CHARACTER_SCALING,
        friction=PLAYER_FRICTION, speed=int(PLAYER_MOVEMENT_SPEED * 0.4)
    ):
        super().__init__(image_path, scale=scale, friction=friction, speed=speed, enemy_type=zombie_type)
        
        # Zombie-specific properties
        self.detection_range = 300
        self.attack_range = 50
        self.damage = 10


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()

        self.window.background_color = arcade.color.AMAZON

        # Camera for scrolling
        self.camera = arcade.Camera2D()
        self.camera_bounds = self.window.rect

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = arcade.Camera2D()

        self.scene = self.create_scene()

        # Set up the player info
        self.player = Player(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            speed=PLAYER_MOVEMENT_SPEED,
        )
        
        # Enemy list and physics engines - initialize before spawning enemies
        self.enemies = []
        self.enemy_physics_engines = []
        
        # Add a test zombie
        self.spawn_zombie("Army_zombie", x=400, y=350)

        # Physics engines - one for player and one for each enemy
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Platforms"),
        )

        # Track the current state of what key is pressed
        self.key_down = {
            LEFT_KEY: False,
            RIGHT_KEY: False,
            UP_KEY: False,
            DOWN_KEY: False,
            A_KEY: False,
            D_KEY: False,
            W_KEY: False,
            S_KEY: False,
        }

        # Mouse position tracking
        self.mouse_position = Vec2(0, 0)

        self.reset()

    def spawn_zombie(self, zombie_type, x, y):
        """Spawn a zombie at the specified position"""
        # Use a placeholder image initially - it will be replaced by the animation system
        placeholder_image = os.path.join(ZOMBIE_ASSETS_DIR, zombie_type, "Walk", "walk_000.png")
        if not os.path.exists(placeholder_image):
            placeholder_image = ":resources:images/animated_characters/zombie/zombie_idle.png"
            
        zombie = Zombie(placeholder_image, zombie_type=zombie_type)
        zombie.position = Vec2(x, y)
        
        self.enemies.append(zombie)
        self.scene.add_sprite("Enemies", zombie)
        
        # Create physics engine for this enemy
        physics_engine = arcade.PhysicsEngineSimple(
            zombie,
            self.scene.get_sprite_list("Platforms"),
        )
        self.enemy_physics_engines.append(physics_engine)
        
        return zombie

    def create_scene(self) -> arcade.Scene:
        """Set up the game and initialize the variables."""
        scene = arcade.Scene()
        
        # Add sprite lists to the scene
        scene.add_sprite_list("Platforms")
        scene.add_sprite_list("Player")
        scene.add_sprite_list("Enemies")
        
        spacing = 200
        for column in range(10):
            for row in range(10):
                sprite = arcade.Sprite(
                    ":resources:images/tiles/grassCenter.png",
                    scale=TILE_SCALING,
                )

                x = (column + 1) * spacing
                y = (row + 1) * sprite.height

                sprite.center_x = x
                sprite.center_y = y
                if random.randrange(100) > 20:
                    scene.add_sprite("Platforms", sprite)

        return scene

    def reset(self):
        self.scene = self.create_scene()

        self.player.position = Vec2(50, 350)
        self.scene.add_sprite("Player", self.player)
        
        # Clear and recreate enemy lists
        self.enemies = []
        self.enemy_physics_engines = []
        
        # Add a test zombie
        self.spawn_zombie("Army_zombie", x=400, y=350)
        
        # Physics engine for player
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Platforms"),
        )
        
        # Initialize player state - state system will handle animations
        self.player.state = PlayerState.IDLE
        self.player.set_animation_for_state()

    def on_draw(self):
        """Render the screen."""

        # Disable CRT filter - render directly to window
        self.clear()

        with self.camera.activate():
            self.scene.draw()

        with self.camera_gui.activate():
            Debug.render(10, 10)

    def update_player_speed(self):
        # Calculate speed based on the keys pressed

        movement_direction_x = 0
        movement_direction_y = 0
        has_movement = False
        # Handle left/right movement (Left/Right arrows or A/D)
        if (self.key_down[LEFT_KEY] or self.key_down[A_KEY]) and not (self.key_down[RIGHT_KEY] or self.key_down[D_KEY]):
            has_movement = True
            movement_direction_x = -1
        elif (self.key_down[RIGHT_KEY] or self.key_down[D_KEY]) and not (self.key_down[LEFT_KEY] or self.key_down[A_KEY]):
            has_movement = True
            movement_direction_x = 1

        # Handle up/down movement (Up/Down arrows or W/S)
        if (self.key_down[UP_KEY] or self.key_down[W_KEY]) and not (self.key_down[DOWN_KEY] or self.key_down[S_KEY]):
            has_movement = True
            movement_direction_y = 1
        elif (self.key_down[DOWN_KEY] or self.key_down[S_KEY]) and not (self.key_down[UP_KEY] or self.key_down[W_KEY]):
            has_movement = True
            movement_direction_y = -1

        self.player.move(Vec2(movement_direction_x, movement_direction_y))
        Debug.update(
            "Velocity", f"{self.player.velocity.x}, {self.player.velocity.y}"
        )

    def update_enemies(self, delta_time):
        """Update all enemies in the game"""
        for i, enemy in enumerate(self.enemies):
            # Update enemy delta time
            enemy.delta_time = delta_time
            
            # Simple AI: move towards player if within detection range
            dx = self.player.position[0] - enemy.position[0]
            dy = self.player.position[1] - enemy.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < enemy.detection_range:
                # Move towards player
                direction = Vec2(dx, dy).normalize() if distance > 0 else Vec2(0, 0)
                enemy.move(direction)
                
                # Attack if close enough
                if distance < enemy.attack_range and random.random() < 0.01:  # Small chance to attack each frame
                    enemy.attack()
            else:
                # Random movement when player not detected
                if random.random() < 0.01:  # Change direction occasionally
                    direction = Vec2(
                        random.uniform(-1, 1),
                        random.uniform(-1, 1)
                    ).normalize()
                    enemy.move(direction)
                else:
                    # Continue current movement
                    enemy.move(Vec2(0, 0))  # This will apply friction but not add new velocity
            
            # Update the enemy facing direction to look at player
            enemy.update_facing_direction(self.player.position)
            
            # Update animation state
            enemy.update_state(delta_time)
            enemy.animate(delta_time)
            
            # Update physics
            if i < len(self.enemy_physics_engines):
                self.enemy_physics_engines[i].update()

    def on_key_press(self, key, modifiers):
        self.key_down[key] = True
        
        # Toggle fullscreen with F11
        if key == FULLSCREEN_KEY:
            self.window.set_fullscreen(not self.window.fullscreen)
            # Update camera when toggling fullscreen
            self.on_resize(self.window.width, self.window.height)
        
        # Weapon switching with number keys
        if key == arcade.key.KEY_1:
            self.player.set_weapon(WeaponType.GUN)
        elif key == arcade.key.KEY_2:
            self.player.set_weapon(WeaponType.BAT)
        elif key == arcade.key.KEY_3:
            self.player.set_weapon(WeaponType.KNIFE)
        elif key == arcade.key.KEY_4:
            self.player.set_weapon(WeaponType.RIFLE)
        elif key == arcade.key.KEY_5:
            self.player.set_weapon(WeaponType.FLAMETHROWER)
        
        # Attack with space
        if key == arcade.key.SPACE:
            self.player.attack()
        
        # Death animation with K (for testing)
        if key == arcade.key.K:
            self.player.die()
        
        # Spawn different zombies with Z key (for testing)
        if key == arcade.key.Z:
            zombie_types = ["Army_zombie", "Cop_Zombie", "Zombie1_female", 
                           "Zombie2_female", "Zombie3_male", "Zombie4_male"]
            zombie_type = random.choice(zombie_types)
            x = self.player.position.x + random.randint(-300, 300)
            y = self.player.position.y + random.randint(-300, 300)
            self.spawn_zombie(zombie_type, x, y)
            Debug.update("Spawned", f"{zombie_type} at {x}, {y}")

    def on_key_release(self, key, modifiers):
        self.key_down[key] = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement"""
        # Convert screen coordinates to world coordinates
        world_pos = self.camera.position + Vec2(x - WINDOW_WIDTH / 2, y - WINDOW_HEIGHT / 2)
        self.mouse_position = world_pos

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.attack()

    def center_camera_to_player(self, delta_time):
        # Move the camera to center on the player
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player.position,
            delta_time,
            FOLLOW_DECAY_CONST,
        )

        # Constrain the camera's position to the camera bounds.
        self.camera.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )
        
    def on_update(self, delta_time):
        self.center_camera_to_player(delta_time)
        
        # Update player
        self.player.delta_time = delta_time
        self.update_player_speed()
        self.physics_engine.update()
        
        # Update player state based on movement
        self.player.update_state(delta_time)
        
        # Update player animation
        self.player.animate(delta_time)
        
        # Update player facing direction
        self.player.update_facing_direction(self.mouse_position)
        
        # Update all enemies
        self.update_enemies(delta_time)
        
        # Debug info for current animation and state
        Debug.update("Current Animation", f"{self.player.current_animation}")
        Debug.update("Animation Frame", f"{self.player.current_animation_frame}")
        Debug.update("Player State", f"{self.player.state.value}")
        Debug.update("Facing Direction", f"{self.player.angle}")
        Debug.update("Mouse Position", f"{self.mouse_position.x:.0f}, {self.mouse_position.y:.0f}")
        Debug.update("Enemy Count", f"{len(self.enemies)}")

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        # Update the cameras to match the new window size
        self.camera.match_window()
        # The position argument keeps `0, 0` in the bottom left corner.
        self.camera_gui.match_window(position=True)
        
        # Handle fullscreen detection - check if window dimensions match display dimensions
        display_width, display_height = arcade.get_display_size()
        
        # Handle fullscreen detection
        if width == display_width and height == display_height:
            # We're in fullscreen or maximized
            self.window.set_fullscreen(True)
        elif self.window.fullscreen and (width < display_width or height < display_height):
            # We were in fullscreen but now in a smaller window
            self.window.set_fullscreen(False)
            
        Debug.update("Window Size", f"{width}x{height}")
        Debug.update("Display Size", f"{display_width}x{display_height}")
        Debug.update("Fullscreen", f"{self.window.fullscreen}")


def main():
    """Main function"""
    window = arcade.Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE,
        update_rate=WINDOW_RATE,
        draw_rate=WINDOW_RATE,
        resizable=True,
    )
    game = GameView()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
