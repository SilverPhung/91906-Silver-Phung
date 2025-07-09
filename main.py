import arcade
import random
from pyglet.math import Vec2

# Window settings
WINDOW_TITLE = "Starting Template"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Constants
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COLLECTABLE_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Player Movement
PLAYER_MOVEMENT_SPEED = 10

# Camera constants
FOLLOW_DECAY_CONST = 0.3  # get within 1% of the target position within 2 seconds

VIEWPORT_MARGIN = 250
HORIZONTAL_BOUNDARY = WINDOW_WIDTH / 2.0 - VIEWPORT_MARGIN
VERTICAL_BOUNDARY = WINDOW_HEIGHT / 2.0 - VIEWPORT_MARGIN

# Key constants
LEFT_KEY = arcade.key.LEFT
RIGHT_KEY = arcade.key.RIGHT
UP_KEY = arcade.key.UP
DOWN_KEY = arcade.key.DOWN

def to_vector(point: tuple[float, float] | arcade.types.Point2) -> Vec2:
    return Vec2(point[0], point[1])



class Entity(arcade.Sprite):
    def __init__(self, image_path, scale=1.0):
        super().__init__(image_path, scale=scale)
        self.position = (0, 0)
        self.velocity = (0, 0)


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
            scale=CHARACTER_SCALING,
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

        # List of debug text objects
        self.debug_dict = {}


        self.reset()

        
    def create_scene(self) -> arcade.Scene:
        """ Set up the game and initialize the variables. """
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

        self.player.position = (50, 350)
        self.scene.add_sprite("Player", self.player) 
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.scene.get_sprite_list("Platforms"),
        )

    def on_draw(self):
        """ Render the screen. """

        self.clear()

        with self.camera.activate():
            self.scene.draw()

        with self.camera_gui.activate():
            debug_text = arcade.Text(
                "",
                x=10,
                y=10,
                color=arcade.csscolor.WHITE,
                font_size=18,
            )
            for key, text in self.debug_dict.items():
                debug_text.text += f"{key}: {text}\n"
            debug_text.draw()

    def update_player_speed(self):
        # Calculate speed based on the keys pressed
        self.player.change_x = 0

        if self.key_down[LEFT_KEY] and not self.key_down[RIGHT_KEY]:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.key_down[RIGHT_KEY] and not self.key_down[LEFT_KEY]:
            self.player.change_x = PLAYER_MOVEMENT_SPEED

        self.player.change_y = 0

        if self.key_down[UP_KEY] and not self.key_down[DOWN_KEY]:
            self.player.change_y = PLAYER_MOVEMENT_SPEED
        elif self.key_down[DOWN_KEY] and not self.key_down[UP_KEY]:
            self.player.change_y = -PLAYER_MOVEMENT_SPEED

        # Normalize the speed
        self.player.velocity = to_vector(self.player.velocity).normalize() * PLAYER_MOVEMENT_SPEED
        self.add_debug_text("Velocity", f"{self.player.velocity.x}, {self.player.velocity.y}")

    def on_key_press(self, key, modifiers):
        self.key_down[key] = True

    def on_key_release(self, key, modifiers):
        self.key_down[key] = False
    def center_camera_to_player(self):
        # Move the camera to center on the player
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player.position,
            self.window.delta_time,
            FOLLOW_DECAY_CONST,
        )

        # Constrain the camera's position to the camera bounds.
        self.camera.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )    
        
    def on_update(self, delta_time):
        self.update_player_speed()
        self.physics_engine.update()
        self.center_camera_to_player()  
    def on_resize(self, width: int, height: int):
        """ Resize window """
        super().on_resize(width, height)
        # Update the cameras to match the new window size
        self.camera.match_window()
        # The position argument keeps `0, 0` in the bottom left corner.
        self.camera.match_window(position=True)

    def add_debug_text(self, key: str, text: str):
        self.debug_dict[key] = text


def main():
    """ Main function """
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()

    window.show_view(game)
    arcade.run()



if __name__ == "__main__":
    main()