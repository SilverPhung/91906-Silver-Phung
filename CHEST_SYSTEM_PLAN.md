# Chest System Implementation Plan

## Overview
Implement a chest system similar to the existing car system, with chests that can contain parts for the car. The system will use the "Chest-parts" and "Chest-noparts" object layers.

## Current State Analysis

### Existing Architecture
- **Car System**: Uses `CarManager` class with `Car` sprites
- **Interaction Pattern**: Player proximity detection + E key interaction
- **State Management**: Parts collection system with visual feedback
- **Map Integration**: Loads from Tiled object layers

### Current Object Layers
- `Chest-parts` → Chests with parts
- `Chest-noparts` → Chests without parts

## Implementation Plan

### Phase 1: Create Base Interactable System
1. **Create `Interactable` base class** in `src/sprites/interactable.py`
   - Abstract base class for all interactable objects
   - Common properties: position, interaction distance, state
   - Abstract methods: `can_interact()`, `handle_interaction()`, `get_interaction_text()`

2. **Refactor `Car` class** to inherit from `Interactable`
   - Move common interaction logic to base class
   - Keep car-specific logic in `Car` class

### Phase 2: Create Chest System
3. **Create `Chest` class** in `src/sprites/chest.py`
   - Inherit from `Interactable`
   - States: CLOSED, OPEN_EMPTY, OPEN_WITH_PART
   - Visual states using chest sprites:
     - `closed.png` - Initial state
     - `open-empty.png` - Opened but empty
     - `open-glow1.png` - Opened with part (ready to collect)

4. **Create `ChestManager` class** in `src/managers/chest_manager.py`
   - Similar structure to `CarManager`
   - Load chests from map object layers
   - Handle chest interactions and state management
   - Track which chest player is near

### Phase 3: Integration with Existing Systems
5. **Update `GameView`** to include chest management
   - Add `ChestManager` instance
   - Add chest interaction checking in `on_update()`
   - Add chest interaction handling

6. **Update `InputManager`** to handle chest interactions
   - Add chest interaction to E key handling
   - Ensure proper interaction priority (car vs chest)

7. **Update `constants.py`**
   - Add chest-related constants
   - Add chest sprite paths and scaling

### Phase 4: State Management
8. **Implement chest state system**
   - **CLOSED**: Initial state, shows closed.png
   - **OPEN_EMPTY**: After first E press if no part, shows open-empty.png
   - **OPEN_WITH_PART**: After first E press if has part, shows open-glow1.png
   - **COLLECTED**: After second E press, part collected, shows open-empty.png

9. **Part collection logic**
   - First E press: Opens chest, reveals if part exists
   - Second E press: Collects part (only if chest has part)
   - Part collection adds to car parts count

### Phase 5: Visual and Audio Feedback
10. **Sprite management**
    - Load chest sprites from `resources/Chest/`
    - Handle sprite transitions based on state
    - Ensure proper scaling and positioning

11. **UI feedback**
    - Show interaction prompts when near chest
    - Display chest state information
    - Update car parts counter when parts collected

### Phase 6: Testing and Polish
12. **Test chest interactions**
    - Test chest loading from maps
    - Test interaction states and transitions
    - Test part collection and car integration

13. **Map integration**
    - Use renamed object layers: "Chest-parts" and "Chest-noparts"
    - Add chest objects to the Tiled maps as needed

## File Structure Changes

### New Files
```
src/sprites/
├── interactable.py      # Base interactable class
└── chest.py            # Chest sprite class

src/managers/
└── chest_manager.py    # Chest management system
```

### Modified Files
```
src/sprites/car.py              # Inherit from Interactable
src/managers/car_manager.py     # Minor updates for consistency
src/views/game_view.py          # Add chest manager integration
src/managers/input_manager.py   # Add chest interaction handling
src/constants.py                # Add chest constants
```

## Implementation Order

1. **Create base Interactable class** - Foundation for both car and chest systems
2. **Refactor Car class** - Ensure compatibility with new base class
3. **Create Chest class** - Implement chest-specific logic and states
4. **Create ChestManager** - Handle chest loading and interaction logic
5. **Update GameView** - Integrate chest system into main game loop
6. **Update InputManager** - Add chest interaction to E key handling
7. **Update constants** - Add chest-related configuration
8. **Test and debug** - Ensure all systems work together properly

## Key Design Principles

- **Single Responsibility**: Each class handles one specific concern
- **Open/Closed**: Base Interactable class open for extension
- **Dependency Inversion**: GameView depends on abstractions (managers)
- **DRY**: Reuse interaction patterns between car and chest systems
- **Clear Interfaces**: Simple, well-defined interaction methods

## Success Criteria

- [x] **Phase 1 Complete**: Base Interactable system created and Car class refactored
- [x] **Phase 2 Complete**: Chest system implemented with state management and integration
- [x] **Bug Fixes Complete**: Fixed chest visibility and zombie texture issues
- [x] **Phase 3 Complete**: Integration with existing systems - GameView, InputManager, and UI updated
- [x] **Test Chests Added**: Added test chests to verify system works when no chests in map
- [ ] Player can approach chests and see interaction prompt
- [ ] E key opens chest and shows appropriate visual state
- [ ] Second E key collects part (if chest has one)
- [ ] Collected parts add to car parts counter
- [ ] Chest states persist correctly across game sessions
- [ ] No conflicts with existing car interaction system
- [ ] Proper visual feedback for all chest states 