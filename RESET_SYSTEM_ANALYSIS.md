# Reset System Analysis & Refactoring Plan

## Current State Analysis

### Problems with Current Reset System

1. **Violation of Single Responsibility Principle (SRP)**
   - Multiple managers have reset responsibilities scattered across different classes
   - `GameView.reset()` handles both entity cleanup and game state reset
   - `MapManager.reset_entities()` duplicates entity cleanup logic
   - Each manager has its own reset method with overlapping responsibilities

2. **Violation of Open/Closed Principle (OCP)**
   - Adding new resetable components requires modifying multiple reset methods
   - No clear interface for what can be reset
   - Reset logic is tightly coupled to specific manager implementations

3. **Violation of Dependency Inversion Principle (DIP)**
   - Reset logic depends on concrete implementations rather than abstractions
   - `GameView` directly calls reset methods on specific managers
   - No common interface for resetable components

4. **Code Duplication (DRY Violation)**
   - Entity cleanup logic duplicated between `GameView.reset()` and `MapManager.reset_entities()`
   - Similar reset patterns repeated across multiple managers
   - No centralized reset coordination

5. **Complexity and Convolution**
   - Reset logic is scattered across 8+ different classes
   - Unclear reset order and dependencies
   - Difficult to understand what gets reset when and why

### Current Reset Methods Found:
- `GameView.reset()` - Main reset method
- `MapManager.reset_entities()` - Entity-specific reset
- `MapManager.reset_game_state_for_map()` - Game state reset
- `GameStateManager.reset_game()` - Game state reset
- `GameStateManager.reset_for_new_map()` - Map-specific reset
- `CarManager.reset_car_parts()` - Car parts reset
- `CarManager.reset_cars()` - Car state reset
- `ChestManager.reset_chests()` - Chest state reset
- `InputManager.reset_keys()` - Input state reset
- `UIManager.reset_ui()` - UI state reset
- `Player.reset()` - Player state reset
- `Car.reset_parts()` - Individual car reset
- `Chest.reset_state()` - Individual chest reset
- `Interactable.reset_interaction_state()` - Interaction state reset

## Proposed Refactoring Solution

### 1. Create Resetable Interface (DIP)

```python
from abc import ABC, abstractmethod
from typing import Protocol

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
```

### 2. Create Reset Coordinator (SRP)

```python
class ResetCoordinator:
    """Coordinates all reset operations following a clear hierarchy."""
    
    def __init__(self, game_view):
        self.game_view = game_view
        self.resetable_components = []
        self.map_resetable_components = []
        self.game_resetable_components = []
    
    def register_component(self, component: Resetable, reset_type: str = "map"):
        """Register a component for reset operations."""
        if reset_type == "game":
            self.game_resetable_components.append(component)
        else:
            self.map_resetable_components.append(component)
        self.resetable_components.append(component)
    
    def reset_for_map(self):
        """Reset all components for a new map."""
        print("[RESET] Starting map reset...")
        
        # 1. Clear entities (enemies, bullets)
        self._clear_entities()
        
        # 2. Reset map-specific components
        for component in self.map_resetable_components:
            try:
                component.reset_for_map()
            except Exception as e:
                print(f"[RESET] Error resetting {component.__class__.__name__}: {e}")
        
        # 3. Regenerate pathfinding
        self._regenerate_pathfinding()
        
        # 4. Spawn new entities
        self._spawn_entities()
        
        print("[RESET] Map reset complete")
    
    def reset_for_game(self):
        """Reset all components for a new game."""
        print("[RESET] Starting game reset...")
        
        # Reset all components
        for component in self.game_resetable_components:
            try:
                component.reset_for_game()
            except Exception as e:
                print(f"[RESET] Error resetting {component.__class__.__name__}: {e}")
        
        print("[RESET] Game reset complete")
    
    def _clear_entities(self):
        """Clear all entities from the current scene."""
        # Clear enemies
        enemy_count = len(self.game_view.enemies)
        for enemy in self.game_view.enemies:
            enemy.cleanup()
        self.game_view.enemies.clear()
        print(f"[RESET] Cleared {enemy_count} enemies")
        
        # Clear bullets
        bullet_count = len(self.game_view.bullet_list)
        self.game_view.bullet_list.clear()
        print(f"[RESET] Cleared {bullet_count} bullets")
    
    def _regenerate_pathfinding(self):
        """Regenerate pathfinding barrier."""
        self.game_view.map_manager.create_pathfinding_barrier()
        print("[RESET] Pathfinding barrier regenerated")
    
    def _spawn_entities(self):
        """Spawn new entities for the map."""
        zombie_count = 10
        current_time = time.time()
        spawn_positions = self.game_view.spawn_manager.get_spawn_positions(zombie_count, current_time)
        
        for x, y in spawn_positions:
            zombie = self.game_view.spawn_manager.create_zombie(x, y)
        
        print(f"[RESET] Spawned {len(self.game_view.enemies)} enemies")
```

### 3. Refactor Existing Components

#### 3.1 Update Managers to Implement Resetable Interface

```python
class CarManager(Resetable, MapResetable):
    def reset_for_map(self):
        """Reset car state for new map."""
        self.reset_car_parts()
        self.reset_cars()
    
    def reset_for_game(self):
        """Reset car state for new game."""
        self.reset_for_map()

class ChestManager(Resetable, MapResetable):
    def reset_for_map(self):
        """Reset chest state for new map."""
        self.reset_chests()

class InputManager(Resetable, MapResetable):
    def reset_for_map(self):
        """Reset input state for new map."""
        self.reset_keys()

class UIManager(Resetable, MapResetable):
    def reset_for_map(self):
        """Reset UI state for new map."""
        self.reset_ui()

class GameStateManager(Resetable, GameResetable):
    def reset_for_game(self):
        """Reset game state for new game."""
        self.reset_game()
    
    def reset_for_map(self):
        """Reset game state for new map."""
        self.reset_for_new_map()
```

#### 3.2 Simplify GameView Reset

```python
class GameView(FadingView):
    def __init__(self):
        # ... existing init code ...
        
        # Initialize reset coordinator
        self.reset_coordinator = ResetCoordinator(self)
        self._register_resetable_components()
    
    def _register_resetable_components(self):
        """Register all resetable components with the coordinator."""
        self.reset_coordinator.register_component(self.car_manager, "map")
        self.reset_coordinator.register_component(self.chest_manager, "map")
        self.reset_coordinator.register_component(self.input_manager, "map")
        self.reset_coordinator.register_component(self.ui_manager, "map")
        self.reset_coordinator.register_component(self.game_state_manager, "game")
    
    def reset(self):
        """Reset the game state for the current map."""
        self.reset_coordinator.reset_for_map()
```

### 4. Benefits of This Approach

1. **Single Responsibility**: Each component handles its own reset logic
2. **Open/Closed**: Easy to add new resetable components without modifying existing code
3. **Dependency Inversion**: Components depend on the Resetable interface
4. **DRY**: No duplication of reset logic
5. **Clear Hierarchy**: Reset coordinator manages the reset order and dependencies
6. **Testability**: Each component can be tested independently
7. **Maintainability**: Clear separation of concerns and easy to understand

### 5. Implementation Plan

#### Phase 1: Create Interfaces and Coordinator
1. Create `Resetable`, `MapResetable`, `GameResetable` protocols
2. Implement `ResetCoordinator` class
3. Add reset coordinator to `GameView`

#### Phase 2: Refactor Existing Managers
1. Update `CarManager` to implement `MapResetable`
2. Update `ChestManager` to implement `MapResetable`
3. Update `InputManager` to implement `MapResetable`
4. Update `UIManager` to implement `MapResetable`
5. Update `GameStateManager` to implement `GameResetable`

#### Phase 3: Simplify GameView
1. Remove complex reset logic from `GameView.reset()`
2. Use `ResetCoordinator` for all reset operations
3. Register all components with the coordinator

#### Phase 4: Clean Up MapManager
1. Remove duplicate reset logic from `MapManager`
2. Use `ResetCoordinator` for entity cleanup
3. Simplify `load_complete_map()` method

#### Phase 5: Testing and Validation
1. Test map transitions
2. Test game resets
3. Verify all components reset correctly
4. Ensure no memory leaks or performance issues

### 6. Migration Strategy

1. **Backward Compatibility**: Keep existing reset methods during transition
2. **Gradual Migration**: Update one manager at a time
3. **Testing**: Test each phase thoroughly before proceeding
4. **Documentation**: Update all reset-related documentation

This refactoring will create a much cleaner, more maintainable reset system that follows SOLID principles and is easy to extend and test. 