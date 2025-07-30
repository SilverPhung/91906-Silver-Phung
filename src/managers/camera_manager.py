import arcade
from pyglet.math import Vec2
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, TILE_SCALING, FOLLOW_DECAY_CONST


class CameraManager:
    """Manages all camera-related functionality including positioning, zoom, and bounds."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        
        # Camera for scrolling
        self.camera = arcade.Camera2D()
        self.camera_bounds = self.game_view.window.rect
        self.target_zoom = 1.0

    def setup_camera_bounds(self, tile_map):
        """Set up camera bounds based on the tile map."""
        self.camera_bounds = arcade.LRBT(
            self.game_view.window.width/2.0,
            tile_map.width * TILE_SIZE * TILE_SCALING - self.game_view.window.width/2.0,
            self.game_view.window.height/2.0,
            tile_map.height * TILE_SIZE * TILE_SCALING
        )

    def center_camera_to_player(self, delta_time):
        """Center the camera on the player with smooth following."""
        current_camera_position = Vec2(
            self.camera.position[0], self.camera.position[1]
        )
        player_position_vec = Vec2(
            self.game_view.player.position[0], self.game_view.player.position[1]
        )

        new_camera_position_vec = arcade.math.smerp_2d(
            current_camera_position,
            player_position_vec,
            delta_time,
            FOLLOW_DECAY_CONST,
        )
        self.camera.position = (
            new_camera_position_vec.x,
            new_camera_position_vec.y,
        )

        # Constrain the camera's position to the camera bounds.
        self.camera.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera.view_data, self.camera_bounds
        )

    def update_zoom(self, delta_time):
        """Update camera zoom with smooth interpolation."""
        current_zoom = self.camera.zoom
        if abs(current_zoom - self.target_zoom) > 0.001:
            new_zoom = arcade.math.lerp(
                current_zoom, self.target_zoom, 5 * delta_time
            )
            self.camera.zoom = new_zoom

    def set_target_zoom(self, zoom_level):
        """Set the target zoom level."""
        self.target_zoom = zoom_level

    def get_camera(self):
        """Get the camera instance."""
        return self.camera

    def get_camera_bounds(self):
        """Get the camera bounds."""
        return self.camera_bounds

    def match_window(self):
        """Match camera to window size."""
        self.camera.match_window()

    def activate(self):
        """Activate the camera for drawing."""
        return self.camera.activate() 