# Testing Framework Instructions

## Overview

This testing framework provides a comprehensive system for testing game functionality with clear objectives, automated tracking, and detailed reporting. The framework is designed to be non-intrusive and can be easily enabled/disabled.

## Quick Start

### Enabling Testing

1. **Enable Testing Mode**: Set `ENABLE_TESTING = True` in `src/constants.py`
2. **Enable Debug Mode**: Set `ENABLE_DEBUG = True` in `src/constants.py`
3. **Run the Game**: Start the game normally

### Using the Testing Framework

#### Menu Screen Testing
- **T Key**: Cycle through available testing objectives
- **R Key**: Queue tests for the current objective
- **Space**: Start the game (tests will run automatically)

#### In-Game Testing
- **F1**: Run movement tests
- **F2**: Run combat tests  
- **F3**: Run car interaction tests
- **F4**: Run health system tests
- **F5**: Run all tests
- **F6**: Show current test results

## Testing Objectives

### 1. Movement Testing
**Objective**: Test player movement controls (WASD/Arrow keys)

**What it tests**:
- Basic player movement in all directions
- Movement speed validation
- Collision detection system

**Validation criteria**:
- Player can move in all directions
- Movement speed is within acceptable range
- Collision detection components are available

### 2. Combat Testing
**Objective**: Test shooting mechanics and enemy interaction

**What it tests**:
- Shooting mechanics availability
- Bullet collision detection
- Enemy damage system

**Validation criteria**:
- Shooting methods are available
- Bullet collision detection is implemented
- Enemy damage system is functional

### 3. Car Interaction Testing
**Objective**: Test car part collection and car usage

**What it tests**:
- Car part collection system
- Car usage functionality
- Interaction mechanics

**Validation criteria**:
- Car manager is available
- Part collection system is functional
- Car usage methods are implemented

### 4. Health System Testing
**Objective**: Test health bar and damage mechanics

**What it tests**:
- Health bar updates
- Damage application system
- Health change tracking

**Validation criteria**:
- Health bar components are available
- Damage system is functional
- Health change methods are implemented

### 5. Map Progression Testing
**Objective**: Test map transitions and level completion

**What it tests**:
- Map transition system
- Level completion logic
- Progress tracking

**Validation criteria**:
- Map transition components are available
- Level completion system is functional
- Progress tracking is implemented

## Testing Components

### 1. Tracking Components

#### MovementTracker
- Tracks player movement events
- Records direction changes
- Measures movement speed
- Tracks collision events

#### CombatTracker
- Tracks shots fired and hits landed
- Records weapon switches
- Calculates accuracy
- Tracks damage events

#### CarInteractionTracker
- Tracks interaction attempts
- Records part collections
- Monitors car usage
- Calculates success rates

#### HealthTracker
- Tracks health changes
- Records damage and healing events
- Monitors health bar updates
- Calculates net health changes

### 2. Centralized Tests

All tests are centralized in `src/testing/centralized_tests.py`:

- `test_player_movement()`: Basic movement validation
- `test_movement_speed()`: Speed measurement
- `test_collision_detection()`: Collision system check
- `test_shooting_mechanics()`: Shooting system validation
- `test_bullet_collision()`: Bullet collision check
- `test_enemy_damage()`: Enemy damage system
- `test_car_part_collection()`: Car part collection
- `test_car_usage()`: Car usage functionality
- `test_health_bar_updates()`: Health bar system
- `test_damage_application()`: Damage application

### 3. Integration System

The `TestingIntegration` class provides runtime injection:

- **Player Tracking**: Injects tracking into player movement and damage
- **Car Manager Tracking**: Monitors car interactions
- **Chest Manager Tracking**: Monitors chest interactions
- **Game View Tracking**: Tracks overall game updates

## Test Results

### Success Criteria
- **Movement Tests**: Player can move, speed is valid, collision detection available
- **Combat Tests**: Shooting mechanics available, bullet collision implemented
- **Car Tests**: Car manager available, part collection functional
- **Health Tests**: Health system available, damage application functional

### Result Format
```json
{
  "total_tests": 10,
  "passed_tests": 8,
  "failed_tests": 2,
  "success_rate": 80.0,
  "detailed_results": {
    "movement": {
      "movement_basic": true,
      "movement_speed": true,
      "collision": false
    },
    "combat": {
      "shooting": true,
      "bullet_collision": true,
      "enemy_damage": true
    }
  }
}
```

## Debug Output

The testing framework provides detailed debug output with the `[TESTING]` prefix:

```
[TESTING] TestingManager initialized
[TESTING] Objective set: Test player movement controls (WASD/Arrow keys)
[TESTING] Starting movement tests...
[TESTING] Movement tracker created
[TESTING] Player Movement: PASSED
[TESTING] Movement Speed: PASSED
[TESTING] Collision Detection: FAILED
[TESTING] Movement tests completed
[TESTING] Test Report: 2/3 tests passed (66.7%)
```

## Configuration

### Constants (`src/constants.py`)

```python
# Testing constants
ENABLE_TESTING = True
TESTING_OBJECTIVES = {
    "movement": "Test player movement controls (WASD/Arrow keys)",
    "combat": "Test shooting mechanics and enemy interaction",
    "car_interaction": "Test car part collection and car usage",
    "map_progression": "Test map transitions and level completion",
    "health_system": "Test health bar and damage mechanics"
}

# Testing validation thresholds
MOVEMENT_SPEED_THRESHOLD = 0.1
COLLISION_DISTANCE_THRESHOLD = 50
SHOOTING_ACCURACY_THRESHOLD = 0.3
HEALTH_CHANGE_THRESHOLD = 1
```

### Disabling Testing

To disable testing completely:
1. Set `ENABLE_TESTING = False` in `src/constants.py`
2. Set `ENABLE_DEBUG = False` in `src/constants.py`

## Troubleshooting

### Common Issues

1. **Tests not running**: Ensure `ENABLE_TESTING = True` and `ENABLE_DEBUG = True`
2. **No debug output**: Check that debug mode is enabled
3. **Tests failing**: Review the validation criteria for each test type
4. **Integration not working**: Ensure game components are properly initialized

### Debug Commands

- **Console Output**: All testing events are logged with `[TESTING]` prefix
- **Error Tracking**: Failed tests are clearly identified in the output
- **Performance Monitoring**: Test execution time is tracked
- **Result Summary**: Comprehensive test reports are generated

## Best Practices

1. **Run tests during development**: Use F1-F6 keys to test specific systems
2. **Monitor debug output**: Watch for `[TESTING]` messages in console
3. **Validate results**: Check test reports for success rates
4. **Clean up**: Disable testing in production builds
5. **Extend tests**: Add new test methods to `centralized_tests.py`

## Extending the Framework

### Adding New Tests

1. **Create test method** in `src/testing/centralized_tests.py`:
```python
def test_new_feature(self) -> bool:
    """Test new feature functionality."""
    # Test implementation
    return Debug.validate_test("New Feature", condition)
```

2. **Add to test runner** in `src/testing/test_runner.py`:
```python
def run_new_feature_tests(self):
    """Run new feature tests."""
    results = {
        'new_feature': self.centralized_tests.test_new_feature()
    }
    return results
```

3. **Update input manager** in `src/managers/input_manager.py`:
```python
def _run_new_feature_tests(self):
    """Run new feature tests."""
    results = self.game_view.run_tests_for_objective("new_feature")
```

### Adding New Tracking Components

1. **Create tracker class** in `src/testing/tracking_components.py`
2. **Add to centralized tests** in `src/testing/centralized_tests.py`
3. **Update integration** in `src/testing/integration.py`

## Conclusion

The testing framework provides a comprehensive, non-intrusive way to validate game functionality. It follows established patterns from the chest system implementation and can be easily enabled/disabled as needed. 