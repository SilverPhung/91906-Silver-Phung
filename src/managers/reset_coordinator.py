"""
Reset Coordinator - Centralized reset management system.

This module provides a clean, centralized approach to managing game state \
    resets
following SOLID principles and clean architecture patterns.
"""

import time
from typing import Protocol, List


class Resetable(Protocol):
    """Protocol for components that can be reset."""

    def reset(self) -> None:
        """Reset the component to its initial state."""
        ...


class MapResetable(Protocol):
    """Protocol for components that reset when changing maps."""

    def reset_for_map(self) -> None:
        """Reset the component for a new map."""
        ...


class GameResetable(Protocol):
    """Protocol for components that reset for a new game."""

    def reset_for_game(self) -> None:
        """Reset the component for a new game."""
        ...


class ResetCoordinator:
    """Coordinates all reset operations following a clear hierarchy."""

    def __init__(self, game_view):
        self.game_view = game_view
        self.resetable_components: List[Resetable] = []
        self.map_resetable_components: List[MapResetable] = []
        self.game_resetable_components: List[GameResetable] = []

        print("[RESET_COORDINATOR] Initialized")

    def register_component(
        self, component: Resetable, reset_type: str = "map"
    ) -> None:
        """Register a component for reset operations.

        Args:
            component: The component to register
            reset_type: Either "map" or "game" to determine reset behavior
        """
        if reset_type == "game":
            if hasattr(component, "reset_for_game"):
                self.game_resetable_components.append(component)
            else:
                print(
                    f"[RESET_COORDINATOR] Warning: \
                        {component.__class__.__name__} doesn't implement reset_for_game"
                )
        else:
            if hasattr(component, "reset_for_map"):
                self.map_resetable_components.append(component)
            else:
                print(
                    f"[RESET_COORDINATOR] Warning: \
                        {component.__class__.__name__} doesn't implement reset_for_map"
                )

        self.resetable_components.append(component)
        print(
            f"[RESET_COORDINATOR] Registered {component.__class__.__name__} \
                for {reset_type} reset"
        )

    def reset_for_map(self) -> None:
        """Reset all components for a new map."""
        print("[RESET_COORDINATOR] Starting map reset...")

        # 1. Clear entities (enemies, bullets)
        self._clear_entities()

        # 2. Reset map-specific components
        for component in self.map_resetable_components:
            try:
                component.reset_for_map()
                print(
                    f"[RESET_COORDINATOR] Reset \
                        {component.__class__.__name__}"
                )
            except Exception as e:
                print(
                    f"[RESET_COORDINATOR] Error resetting \
                        {component.__class__.__name__}: {e}"
                )

        # 3. Regenerate pathfinding
        self._regenerate_pathfinding()

        # 4. Spawn new entities
        self._spawn_entities()

        print("[RESET_COORDINATOR] Map reset complete")

    def reset_for_game(self) -> None:
        """Reset all components for a new game."""
        print("[RESET_COORDINATOR] Starting game reset...")

        # Reset all components
        for component in self.game_resetable_components:
            try:
                component.reset_for_game()
                print(
                    f"[RESET_COORDINATOR] Reset \
                        {component.__class__.__name__}"
                )
            except Exception as e:
                print(
                    f"[RESET_COORDINATOR] Error resetting \
                        {component.__class__.__name__}: {e}"
                )

        print("[RESET_COORDINATOR] Game reset complete")

    def _clear_entities(self) -> None:
        """Clear all entities from the current scene."""
        # Clear enemies
        enemy_count = len(self.game_view.enemies)
        for enemy in self.game_view.enemies:
            enemy.cleanup()
        self.game_view.enemies.clear()
        print(f"[RESET_COORDINATOR] Cleared {enemy_count} enemies")

        # Clear bullets
        bullet_count = len(self.game_view.bullet_list)
        self.game_view.bullet_list.clear()
        print(f"[RESET_COORDINATOR] Cleared {bullet_count} bullets")

    def _regenerate_pathfinding(self) -> None:
        """Regenerate pathfinding barrier."""
        if hasattr(self.game_view, "map_manager"):
            self.game_view.map_manager.create_pathfinding_barrier()
            print("[RESET_COORDINATOR] Pathfinding barrier regenerated")

    def _spawn_entities(self) -> None:
        """Spawn new entities for the map."""
        if hasattr(self.game_view, "spawn_manager"):
            zombie_count = 10
            current_time = time.time()
            spawn_positions = self.game_view.spawn_manager.get_spawn_positions(
                zombie_count, current_time
            )

            for x, y in spawn_positions:
                self.game_view.spawn_manager.create_zombie(x, y)

            print(
                f"[RESET_COORDINATOR] Spawned \
                    {len(self.game_view.enemies)} enemies"
            )
