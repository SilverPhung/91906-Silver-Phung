import arcade
import random
from pyglet.math import Vec2, clamp
import time
from arcade.experimental.crt_filter import CRTFilter
import os
import asyncio
from enum import Enum
import math

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_RATE = 1 / 144  # 144hz

# Constants
CHARACTER_SCALING = 1
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

PLAYER_ASSETS_DIR = "resources/Players"

# Animation constants
RIGHT_FACING = 0
LEFT_FACING = 1
DEAD_ZONE = 0.1  # Minimum velocity to consider as moving

class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    SHOOTING = "shooting"


def to_vector(point: tuple[float, float] | arcade.types.Point2 | Vec2) -> Vec2:
    return Vec2(point[0], point[1])


class Debug:
    debug_dict = {}

    @staticmethod
    def update(key: str, text: str):
        Debug.debug_dict[key] = text

    @staticmethod
    def render(x: float, y: float):

        for key, text in Debug.debug_dict.items():
            arcade.draw_text(
                f"{key}: {text}",
                x,
                y,
                arcade.csscolor.WHITE,
                18,
            )
            y += 20

PLAYER_ANIMATION_STRUCTURE = {
    "Bat": 12,
    "Death": 6,
    "FlameThrower": 9,
    "Gun_Shot": 5,
    "Knife": 8,
    "Riffle": 9,
    "Walk_bat": 6,
    "Walk_FireThrhrower": 6,
    "Walk_gun": 6,
    "Walk_knife": 6,
    "Walk_riffle": 6
}

class Entity(arcade.Sprite):
    def __init__(
        self, image_path, scale=CHARACTER_SCALING, friction=PLAYER_FRICTION, speed=PLAYER_MOVEMENT_SPEED, player_preset="Girl"
    ):
        super().__init__(image_path, scale=scale)

        self.speed = speed

        self.position: Vec2 = Vec2(0, 0)
        self.velocity: Vec2 = Vec2(0, 0)
        self.friction = clamp(friction, 0, 1)
        self.delta_time = WINDOW_RATE

        self.player_preset = player_preset
        self.animation = {}

        self.current_animation = None
        self.current_animation_frame = 0
        self.current_animation_time = 0
        
        # State system
        self.state = PlayerState.IDLE
        self.facing_direction = RIGHT_FACING
        self.mouse_position = Vec2(0, 0)
        
        # Animation timing
        self.animation_fps = 10
        self.frame_duration = 1.0 / self.animation_fps
        
        # Load animations
        asyncio.run(self.load_animation())

    # Example image name: Walk_gun_003.png
    async def load_animation(self):
        animation_dict = {}
        total_frames = 0
        
        # Loop through each animation type in the structure
        for animation_type, frame_count in PLAYER_ANIMATION_STRUCTURE.items():
            # Store animations for both facing directions
            animation_dict[animation_type] = []
            
            # Get the directory path for this animation type
            animation_dir = os.path.join(PLAYER_ASSETS_DIR, self.player_preset, animation_type)
            
            # Check if the directory exists
            if os.path.exists(animation_dir):
                # Get all PNG files in the directory
                file_list = [f for f in os.listdir(animation_dir) if f.endswith(".png")]
                
                # Sort files alphabetically to ensure correct animation sequence
                file_list.sort()
                
                # Load animation frames
                animation_frames = []
                
                # Load each frame into the animation list
                for file_name in file_list:
                    # Create the full path to the image
                    image_path = os.path.join(animation_dir, file_name)
                    # Load the texture
                    texture = arcade.load_texture(image_path)
                    # Add the texture to the animation frames
                    animation_frames.append(texture)
                
                # Store the animation frames
                animation_dict[animation_type] = animation_frames
                total_frames += len(animation_frames)
        
        self.animation = animation_dict
        # Add summary debug info
        Debug.update(f"{self.player_preset} Animations", f"{len(animation_dict)} types, {total_frames} frames")

        # print(self.animation)

    def move(self, direction: Vec2):
        if direction.length() > 0:
            self.velocity = direction * self.speed * self.delta_time

        self.update()

    def update(self):

        # friction
        self.velocity = to_vector(self.velocity) * (1 - self.friction) ** (
            self.delta_time
        )

        # Clamp the velocity to the max speed
        velocity_length = self.velocity.length()

        self.velocity = self.velocity.normalize() * clamp(
            velocity_length, 0, self.speed
        )
        # time.sleep(0.01)

    def animate(self, delta_time: float):

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
                    self.texture = animation_frames[self.current_animation_frame]
                    
                    # Set the sprite's facing direction
                    if self.facing_direction == LEFT_FACING:
                        self.texture = self.texture.flip_horizontally()

    def set_animation(self, animation_name: str):
        """Set the current animation by name"""
        if animation_name in self.animation and self.animation[animation_name]:
            self.current_animation = animation_name
            self.current_animation_frame = 0
            self.current_animation_time = 0
            # Set the first frame immediately
            self.texture = self.animation[animation_name][0]
            if self.facing_direction == LEFT_FACING:
                self.texture = self.texture.flip_horizontally()
                
    def update_state(self, delta_time: float):
        """Update player state based on velocity and other factors"""
        # Check if player is moving
        velocity_magnitude = self.velocity.length()
        
        if velocity_magnitude > DEAD_ZONE:
            if self.state != PlayerState.WALKING:
                self.state = PlayerState.WALKING
                self.set_animation("Walk_gun")
        else:
            if self.state != PlayerState.IDLE:
                self.state = PlayerState.IDLE
                self.set_animation("Gun_Shot")  # Using Gun_Shot as idle animation
                
    def update_facing_direction(self, mouse_pos: Vec2):
        """Update facing direction based on mouse position"""
        self.mouse_position = mouse_pos
        
        # Calculate direction from player to mouse
        direction_x = mouse_pos.x - self.position.x
        
        # Update facing direction
        new_facing = RIGHT_FACING if direction_x >= 0 else LEFT_FACING
        
        if new_facing != self.facing_direction:
            self.facing_direction = new_facing
            # Update current texture to match new facing direction
            if self.current_animation and self.current_animation in self.animation:
                animation_frames = self.animation[self.current_animation]
                if animation_frames:
                    self.texture = animation_frames[self.current_animation_frame]
                    if self.facing_direction == LEFT_FACING:
                        self.texture = self.texture.flip_horizontally()


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
        self.player = Entity(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            speed=PLAYER_MOVEMENT_SPEED,
        )

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
        }

        # Mouse position tracking
        self.mouse_position = Vec2(0, 0)

        self.reset()

        # Create the crt filter
        self.crt_filter = CRTFilter(WINDOW_WIDTH, WINDOW_HEIGHT,
                                    resolution_down_scale=3.0,
                                    hard_scan=-6.0,
                                    hard_pix=-4.0,
                                    display_warp=Vec2(1.0 / 16.0, 1.0 / 16.0),
                                    mask_dark=0.5,
                                    mask_light=1.5)

    def create_scene(self) -> arcade.Scene:
        """Set up the game and initialize the variables."""
        scene = arcade.Scene()
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
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Platforms"),
        )
        
        # Initialize player state - state system will handle animations
        self.player.state = PlayerState.IDLE
        self.player.set_animation("Gun_Shot")  # Start with idle animation

    def on_draw(self):
        """Render the screen."""

        self.crt_filter.use()
        self.crt_filter.clear()

        with self.camera.activate():
            self.scene.draw()

        self.window.use()
        self.clear()
        self.crt_filter.draw()

        with self.camera_gui.activate():
            Debug.render(10, 10)

        

    def update_player_speed(self):
        # Calculate speed based on the keys pressed

        movement_direction_x = 0
        movement_direction_y = 0
        has_movement = False
        if self.key_down[LEFT_KEY] and not self.key_down[RIGHT_KEY]:
            has_movement = True
            movement_direction_x = -1
        elif self.key_down[RIGHT_KEY] and not self.key_down[LEFT_KEY]:
            has_movement = True
            movement_direction_x = 1

        if self.key_down[UP_KEY] and not self.key_down[DOWN_KEY]:
            has_movement = True
            movement_direction_y = 1
        elif self.key_down[DOWN_KEY] and not self.key_down[UP_KEY]:
            has_movement = True
            movement_direction_y = -1

        self.player.move(Vec2(movement_direction_x, movement_direction_y))
        Debug.update(
            "Velocity", f"{self.player.velocity.x}, {self.player.velocity.y}"
        )

    def on_key_press(self, key, modifiers):
        self.key_down[key] = True

    def on_key_release(self, key, modifiers):
        self.key_down[key] = False

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse movement"""
        # Convert screen coordinates to world coordinates
        world_pos = self.camera.position + Vec2(x - WINDOW_WIDTH / 2, y - WINDOW_HEIGHT / 2)
        self.mouse_position = world_pos

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
        self.player.delta_time = delta_time
        self.update_player_speed()
        self.physics_engine.update()
        
        # Update player state based on movement
        self.player.update_state(delta_time)
        
        # Update player facing direction based on mouse position
        self.player.update_facing_direction(self.mouse_position)
        
        # Update player animation
        self.player.animate(delta_time)
        
        # Debug info for current animation and state
        Debug.update("Current Animation", f"{self.player.current_animation}")
        Debug.update("Animation Frame", f"{self.player.current_animation_frame}")
        Debug.update("Player State", f"{self.player.state.value}")
        Debug.update("Facing Direction", f"{'Left' if self.player.facing_direction == LEFT_FACING else 'Right'}")
        Debug.update("Mouse Position", f"{self.mouse_position.x:.0f}, {self.mouse_position.y:.0f}")

    def on_resize(self, width: int, height: int):
        """Resize window"""
        super().on_resize(width, height)
        # Update the cameras to match the new window size
        self.camera.match_window()
        # The position argument keeps `0, 0` in the bottom left corner.
        self.camera.match_window(position=True)


def main():
    """Main function"""
    window = arcade.Window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE,
        update_rate=WINDOW_RATE,
        draw_rate=WINDOW_RATE,
    )
    game = GameView()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
