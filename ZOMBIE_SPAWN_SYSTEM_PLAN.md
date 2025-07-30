# Zombie Spawn System Implementation Plan

## Overview
Currently, zombies are spawned randomly across the map using `spawn_random_position()` method. This plan modifies the system to use predefined spawn points placed on the maps, ensuring zombies don't spawn inside walls and providing better gameplay control.

## Current System Analysis

### Current Zombie Spawning
- **Location**: `src/views/game_view.py` lines 260-270
- **Method**: `spawn_random_position()` in `src/entities/enemy.py` lines 60-62
- **Current Count**: 10 zombies per map
- **Spawn Logic**: Random coordinates within map bounds (`MAP_WIDTH_PIXEL`, `MAP_HEIGHT_PIXEL`)

### Current Map Structure
- **Map Files**: `resources/maps/map1.tmx`, `resources/maps/map2.tmx`
- **Existing Object Groups**: 
  - `Chest-parts` (chests with car parts)
  - `Chest-noparts` (empty chests)
  - `Old-car` (starting car position)
  - `New-car` (target car position)

## Implementation Plan

### Phase 1: Map Modification
**Objective**: Add zombie spawn point object groups to both maps

#### 1.1 Map Analysis
- Analyze current map layouts to identify suitable spawn areas
- Ensure spawn points are not inside walls or obstacles
- Distribute 25 spawn points evenly across each map

#### 1.2 Map1.tmx Modifications
- Add new object group: `<objectgroup id="12" name="Zombie-spawns">`
- Place 25 spawn points in strategic locations:
  - Avoid wall areas (Walls layer)
  - Distribute across different map regions
  - Ensure minimum distance between spawn points
  - Place in open areas (Grass, Dirt, Road layers)

#### 1.3 Map2.tmx Modifications
- Add new object group: `<objectgroup id="12" name="Zombie-spawns">`
- Place 25 spawn points following same criteria as Map1
- Consider map2's unique layout and obstacles

### Phase 2: Code Modifications

#### 2.1 Enemy Class Updates
**File**: `src/entities/enemy.py`

**Changes**:
- Add new method: `spawn_at_position(x, y)` to replace `spawn_random_position()`
- Modify `spawn_random_position()` to use predefined spawn points
- Add spawn point validation to ensure no wall collisions

#### 2.2 Game View Updates
**File**: `src/views/game_view.py`

**Changes**:
- Modify zombie spawning logic in `load_map()` method
- Add spawn point loading from map object layers
- Implement spawn point selection algorithm
- Update spawn count from 10 to 25 zombies

#### 2.3 Spawn Manager Creation
**New File**: `src/managers/spawn_manager.py`

**Purpose**: Centralized spawn point management
- Load spawn points from map object layers
- Validate spawn points (no wall collisions)
- Distribute zombies across available spawn points
- Handle spawn point selection and assignment

### Phase 3: Integration and Testing

#### 3.1 Manager Integration
- Integrate `SpawnManager` into `ManagerFactory`
- Update `GameView` to use `SpawnManager`
- Ensure proper initialization and cleanup

#### 3.2 Testing Framework
- Add spawn point validation tests
- Test zombie distribution across spawn points
- Verify no wall collisions
- Test map transitions with new spawn system

## Technical Details

### Spawn Point Validation
```python
def validate_spawn_point(x, y, wall_list):
    """Check if spawn point is valid (not inside walls)"""
    # Check collision with walls
    # Return True if valid, False if invalid
```

### Spawn Point Selection
```python
def select_spawn_points(spawn_points, zombie_count):
    """Select spawn points for zombies"""
    # Randomly select spawn points
    # Ensure even distribution
    # Return list of (x, y) coordinates
```

### Map Object Loading
```python
def load_spawn_points_from_map(tile_map):
    """Load zombie spawn points from map object layer"""
    # Extract spawn points from "Zombie-spawns" object group
    # Return list of spawn point coordinates
```

## File Structure Changes

### New Files
- `src/managers/spawn_manager.py` - Spawn point management
- `test_spawn_system.py` - Spawn system tests

### Modified Files
- `resources/maps/map1.tmx` - Add zombie spawn points
- `resources/maps/map2.tmx` - Add zombie spawn points
- `src/entities/enemy.py` - Update spawning methods
- `src/views/game_view.py` - Integrate spawn manager
- `src/managers/manager_factory.py` - Add spawn manager
- `src/managers/__init__.py` - Export spawn manager

## Implementation Checklist

### Phase 1: Map Preparation
- [x] Analyze map1.tmx layout and identify suitable spawn areas
- [x] Add 25 zombie spawn points to map1.tmx
- [x] Analyze map2.tmx layout and identify suitable spawn areas
- [x] Add 25 zombie spawn points to map2.tmx
- [x] Validate spawn points don't overlap with walls

### Phase 2: Core Implementation
- [ ] Create `src/managers/spawn_manager.py`
- [ ] Implement spawn point loading from map files
- [ ] Implement spawn point validation
- [ ] Implement spawn point selection algorithm
- [ ] Update `src/entities/enemy.py` with new spawning methods
- [ ] Update `src/views/game_view.py` to use spawn manager
- [ ] Integrate spawn manager into manager factory

### Phase 3: Testing and Validation
- [ ] Test spawn point loading from both maps
- [ ] Verify 25 zombies spawn per map
- [ ] Test spawn point validation (no wall collisions)
- [ ] Test zombie distribution across spawn points
- [ ] Test map transitions with new spawn system
- [ ] Remove debug logging after validation

### Phase 4: Documentation
- [ ] Update code comments for new spawn system
- [ ] Document spawn point placement guidelines
- [ ] Update testing instructions if needed

## Success Criteria
1. **25 zombies spawn per map** instead of 10
2. **No zombies spawn inside walls** or obstacles
3. **Even distribution** of zombies across map areas
4. **Consistent spawning** across map transitions
5. **Maintains existing zombie behavior** (AI, animations, etc.)

## Risk Mitigation
- **Wall Collision Risk**: Implement thorough spawn point validation
- **Performance Risk**: Optimize spawn point loading and selection
- **Map Compatibility Risk**: Ensure new object groups don't break existing map loading
- **Testing Risk**: Comprehensive testing of spawn system before deployment

## Timeline Estimate
- **Phase 1**: 2-3 hours (map analysis and modification)
- **Phase 2**: 4-5 hours (core implementation)
- **Phase 3**: 2-3 hours (testing and validation)
- **Phase 4**: 1 hour (documentation)
- **Total**: 9-12 hours

## Notes
- Spawn points should be placed in open areas (grass, dirt, road tiles)
- Minimum distance between spawn points to avoid clustering
- Consider player starting position to avoid immediate zombie encounters
- Maintain existing zombie AI and behavior systems 