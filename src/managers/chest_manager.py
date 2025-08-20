import arcade
from src.sprites.chest import Chest
from src.constants import TILE_SCALING, INTERACTION_DISTANCE, ENABLE_TESTING
from src.debug import Debug


class ChestManager:
    """
    Manages all chest-related functionality including loading, interaction, and state.

    Uses the Interactable-based Chest class for consistent interaction behavior.
    Handles chest loading from map object layers and part collection integration.
    """

    def __init__(self, game_view):
        self.game_view = game_view

        # Chest-related properties
        self.chests_with_parts = []  # List of chests that contain parts
        self.chests_without_parts = (
            []
        )  # List of chests that don't contain parts
        self.near_chest = None  # Track which chest player is near
        self.parts_collected_from_chests = (
            0  # Track parts collected from chests
        )

    def clear_chests(self):
        """Clear chests completely for new map."""
        # Clear from scene
        all_chests = self.chests_with_parts + self.chests_without_parts
        for chest in all_chests:
            try:
                # Remove from scene
                chest_list = self.game_view.scene.get_sprite_list(
                    "ChestsLayer"
                )
                if chest in chest_list:
                    chest_list.remove(chest)
            except Exception as e:
                pass

        # Clear lists
        self.chests_with_parts.clear()
        self.chests_without_parts.clear()
        self.near_chest = None
        self.parts_collected_from_chests = 0

    def load_chests_from_map(self):
        """Load chests from the Tiled object layers."""
        # Check if chests are already loaded
        if self.chests_with_parts or self.chests_without_parts:
            print(f"[CHEST_MANAGER] Chests already loaded, skipping")
            return  # Already loaded

        # Get tile_map from MapManager
        tile_map = (
            self.game_view.map_manager.get_tile_map()
            if hasattr(self.game_view, "map_manager")
            else self.game_view.tile_map
        )

        try:
            chest_layers = {
                "Chest-parts": (
                    self.chests_with_parts,
                    True,
                ),  # Chests with parts
                "Chest-noparts": (
                    self.chests_without_parts,
                    False,
                ),  # Chests without parts
            }

            for layer_name, (chest_list, has_part) in chest_layers.items():
                # Get tile_map from MapManager
                tile_map = (
                    self.game_view.map_manager.get_tile_map()
                    if hasattr(self.game_view, "map_manager")
                    else self.game_view.tile_map
                )
                chest_objects = tile_map.object_lists.get(layer_name, [])
                print(
                    f"[CHEST_MANAGER] Looking for {layer_name}, found {len(chest_objects)} objects"
                )

                if not chest_objects:
                    continue

                for i, chest_object in enumerate(chest_objects):
                    try:
                        pos_x, pos_y = chest_object.shape
                        chest = Chest((pos_x, pos_y), has_part=has_part)
                        chest_list.append(chest)
                        self.game_view.scene.add_sprite("ChestsLayer", chest)

                    except Exception as e:

                        import traceback

                        traceback.print_exc()

            # Add test chests if no chests were loaded from map
            total_chests = len(self.chests_with_parts) + len(
                self.chests_without_parts
            )
            if total_chests == 0:
                self._add_test_chests()
                total_chests = len(self.chests_with_parts) + len(
                    self.chests_without_parts
                )

        except Exception as e:

            import traceback

            traceback.print_exc()

    def _add_test_chests(self):
        """Add test chests to verify the system works."""

        # Add a chest with part near the old car
        if self.game_view.car_manager.old_car:
            old_car_pos = (
                self.game_view.car_manager.old_car.center_x + 100,
                self.game_view.car_manager.old_car.center_y,
            )
            test_chest_with_part = Chest(old_car_pos, has_part=True)
            self.chests_with_parts.append(test_chest_with_part)
            self.game_view.scene.add_sprite(
                "ChestsLayer", test_chest_with_part
            )
            print(
                f"[CHEST_MANAGER] Added chest with part to scene at ({test_chest_with_part.center_x:.1f}, {test_chest_with_part.center_y:.1f})"
            )

        # Add a chest without part near the new car
        if self.game_view.car_manager.new_car:
            new_car_pos = (
                self.game_view.car_manager.new_car.center_x - 100,
                self.game_view.car_manager.new_car.center_y,
            )
            test_chest_without_part = Chest(new_car_pos, has_part=False)
            self.chests_without_parts.append(test_chest_without_part)
            self.game_view.scene.add_sprite(
                "ChestsLayer", test_chest_without_part
            )
            print(
                f"[CHEST_MANAGER] Added chest without part to scene at ({test_chest_without_part.center_x:.1f}, {test_chest_without_part.center_y:.1f})"
            )

        # Add a chest in the middle of the map
        middle_pos = (1000, 1000)
        test_chest_middle = Chest(middle_pos, has_part=True)
        self.chests_with_parts.append(test_chest_middle)
        self.game_view.scene.add_sprite("ChestsLayer", test_chest_middle)
        print(
            f"[CHEST_MANAGER] Added middle chest to scene at ({test_chest_middle.center_x:.1f}, {test_chest_middle.center_y:.1f})"
        )

    def check_chest_interactions(self):
        """
        Check if player is near any chest and update interaction state.

        Uses the new Interactable proximity checking system.
        """
        previous_near_chest = self.near_chest
        self.near_chest = None

        # Check all chests (with and without parts)
        all_chests = self.chests_with_parts + self.chests_without_parts

        # # Track testing data
        # if ENABLE_TESTING:
        #     Debug.track_event("chest_proximity_check", {
        #         'total_chests': len(all_chests),
        #         'player_position': (self.game_view.player.center_x, self.game_view.player.center_y) if hasattr(self.game_view, 'player') else None
        #     })

        for i, chest in enumerate(all_chests):
            if not self.near_chest:
                # Use the new Interactable proximity checking
                is_near = chest.check_proximity(self.game_view.player)
                if is_near:
                    self.near_chest = chest

                    # Track testing data
                    if ENABLE_TESTING:
                        Debug.track_event(
                            "chest_proximity_detected",
                            {
                                "chest_id": i + 1,
                                "chest_position": (
                                    chest.center_x,
                                    chest.center_y,
                                ),
                                "chest_has_part": chest.has_part,
                                "chest_state": chest.state,
                            },
                        )
                    break

        # Reset interaction state for chests not near player
        for chest in all_chests:
            if chest != self.near_chest:
                chest.reset_interaction_state()

    def handle_chest_interaction(self):
        """
        Handle chest interaction when E key is pressed.

        Uses the new Interactable interaction system and integrates
        with car parts collection.
        """
        if not self.near_chest:
            return

        if not self.near_chest.can_interact():
            return

        # Track testing data before interaction
        if ENABLE_TESTING:
            Debug.track_event(
                "chest_interaction_attempt",
                {
                    "chest_has_part": self.near_chest.has_part,
                    "chest_state": self.near_chest.state,
                    "parts_collected_before": self.parts_collected_from_chests,
                },
            )

        # Use the new Interactable interaction handling
        part_collected = self.near_chest.handle_interaction()

        if part_collected:
            self.parts_collected_from_chests += 1

            # Add the part to the car
            if self.game_view.car_manager.new_car:
                part_added = self.game_view.car_manager.new_car.add_part()
                if part_added:
                    # Also update the car manager's counter for UI display
                    self.game_view.car_manager.car_parts_collected += 1
                    print(f"[CHEST_MANAGER] Part collected from chest. Total parts: {self.game_view.car_manager.car_parts_collected}")

        # Track testing data after interaction
        if ENABLE_TESTING:
            Debug.track_event(
                "chest_interaction_result",
                {
                    "part_collected": part_collected,
                    "parts_collected_after": self.parts_collected_from_chests,
                    "chest_state_after": self.near_chest.state,
                },
            )

    def get_near_chest_interaction_text(self):
        """
        Get the interaction text for the chest the player is near.

        Returns:
            str: Interaction text or None if no chest nearby
        """
        if self.near_chest:
            return self.near_chest.get_interaction_text()
        return None

    def reset_chests(self):
        """Reset chest state for new map."""
        # Reset all chests to initial state
        all_chests = self.chests_with_parts + self.chests_without_parts
        for chest in all_chests:
            chest.reset_state()

        self.chests_with_parts.clear()
        self.chests_without_parts.clear()
        self.near_chest = None
        self.parts_collected_from_chests = 0

    def get_chest_stats(self):
        """
        Get statistics about chests and parts collection.

        Returns:
            dict: Statistics about chests and parts
        """
        total_chests = len(self.chests_with_parts) + len(
            self.chests_without_parts
        )
        chests_with_parts = len(self.chests_with_parts)
        chests_without_parts = len(self.chests_without_parts)

        return {
            "total_chests": total_chests,
            "chests_with_parts": chests_with_parts,
            "chests_without_parts": chests_without_parts,
            "parts_collected": self.parts_collected_from_chests,
            "parts_remaining": chests_with_parts
            - self.parts_collected_from_chests,
        }
