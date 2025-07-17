# Zombie Shooter Game Design Document

## Game Overview

### Concept
A top-down zombie shooter where players must navigate through a post-apocalyptic environment to collect car components while fighting off hordes of zombies. The ultimate goal is to assemble a complete car and escape before being overwhelmed.

### Genre
Top-down shooter, Survival, Action

### Platform
PC (Windows, macOS, Linux) - Built with Python Arcade

### Target Audience
Players who enjoy action-packed survival games with resource management elements

## Core Gameplay Loop

1. **Explore** the map to find car components and weapons
2. **Fight** zombies that spawn in waves
3. **Collect** weapons, ammo, and car parts
4. **Manage** inventory and resources
5. **Assemble** car components to complete the vehicle
6. **Escape** once the car is fully assembled

## Game Mechanics

### Player Systems

#### Movement
- **Control Scheme**: WASD for movement, mouse for aiming
- **Movement Speed**: 1000 units/second with friction-based deceleration
- **Character Types**: Female or Male adventurer with weapon-specific animations

#### Combat
- **Aiming**: Mouse cursor determines facing direction and shooting angle
- **Weapons**: Multiple weapon types with different characteristics
- **Ammunition**: Limited ammo system requiring pickups
- **Health**: Player health system with damage from zombie attacks

#### Animation States
- **Idle**: Gun_Shot animation (weapon ready)
- **Walking**: Walk_gun animation (moving with weapon)
- **Shooting**: Weapon-specific firing animations
- **Death**: Death animation sequence

### Weapon System

#### Weapon Types
1. **Pistol** (Gun_Shot)
   - Fast firing rate
   - Low damage
   - Common ammo

2. **Rifle** (Riffle)
   - Medium firing rate
   - High damage
   - Accurate shots

3. **Shotgun** (Not in current assets - to be added)
   - Slow firing rate
   - High close-range damage
   - Spread shot pattern

4. **Flamethrower** (FlameThrower)
   - Continuous damage
   - Short range
   - Area of effect

5. **Melee** (Bat/Knife)
   - Close combat
   - No ammo required
   - High risk, high reward

#### Ammunition System
- **Ammo Types**: Pistol rounds, rifle rounds, shotgun shells, fuel
- **Pickup System**: Ammo scattered throughout the map
- **Inventory Limits**: Maximum carrying capacity for each ammo type

### Zombie System

#### Zombie Behavior
- **AI**: Simple pathfinding toward player
- **Spawning**: Wave-based spawning system
- **Health**: Variable health based on zombie type
- **Damage**: Melee attacks when in close proximity
- **Animation**: Walking, attacking, and death animations

#### Zombie Types (Future Enhancement)
- **Basic Walker**: Slow, low health
- **Runner**: Fast, medium health
- **Brute**: Slow, high health, high damage

### Car Assembly System

#### Required Components
1. **Engine** - Core component for vehicle operation
2. **Tires** (4x) - Movement capability
3. **Battery** - Electrical systems
4. **Fuel Tank** - Energy source
5. **Windshield** - Protection
6. **Doors** (2x) - Entry/exit points

#### Collection Mechanics
- Components scattered throughout the map
- Each component has a specific spawn location
- Visual indicators show component locations
- Progress tracking in UI

### Map Design

#### Environment
- **Tileset**: Post-apocalyptic urban environment
- **Tile Types**: 
  - Asphalt roads and cracked surfaces
  - Grass and vegetation
  - Building walls and roofs
  - Water features
- **Obstacles**: Buildings, debris, vehicles
- **Safe Zones**: Areas with temporary respite

#### Layout
- **Size**: Large explorable area with multiple districts
- **Buildings**: Searchable structures containing loot
- **Spawn Points**: Designated zombie emergence locations
- **Objective Markers**: Visual indicators for car components

## Technical Specifications

### Engine and Framework
- **Engine**: Python Arcade
- **Graphics**: 2D sprite-based rendering
- **Physics**: Arcade's built-in physics engine
- **Audio**: Arcade's audio system for sound effects

### Window Configuration
- **Resolution**: 1280x720 (16:9 aspect ratio)
- **Framerate**: 144 FPS target
- **Scaling**: Configurable sprite scaling

### Asset Structure
```
resources/
├── Players/
│   ├── Girl/           # Female character animations
│   └── Man/            # Male character animations
├── Zombies/            # Zombie sprites and animations
├── sound/
│   ├── weapon/         # Weapon sound effects
│   └── zombie/         # Zombie audio
└── tiles/              # Environment tileset
```

### Animation System
- **Frame Rate**: 10 FPS animation playback
- **Format**: PNG sprite sequences
- **Naming Convention**: [Action]_[Frame].png
- **States**: Idle, Walking, Shooting, Death

### Camera System
- **Type**: 2D Camera with smooth following
- **Follow Speed**: Configurable decay constant
- **Boundaries**: Constrained to map limits
- **Effects**: CRT filter for retro aesthetic

## User Interface

### HUD Elements
- **Health Bar**: Visual health indicator
- **Ammo Counter**: Current weapon ammunition
- **Minimap**: Top-down view of surroundings
- **Component Progress**: Car assembly status
- **Crosshair**: Mouse cursor indicator
- **Debug Panel**: Development information overlay

### Menu Systems
- **Main Menu**: Start game, options, quit
- **Pause Menu**: Resume, restart, settings, quit
- **Game Over Screen**: Death notification, restart option
- **Victory Screen**: Escape success, statistics

### Controls
- **Movement**: WASD keys
- **Shooting**: Left mouse button
- **Weapon Switch**: Number keys (1-5)
- **Inventory**: Tab key
- **Pause**: Escape key

## Audio Design

### Sound Effects
- **Weapon Sounds**: Firing, reloading, switching
- **Zombie Audio**: Groans, footsteps, death sounds
- **Environmental**: Ambient sounds, pickup notifications
- **UI Audio**: Menu navigation, button clicks

### Music
- **Ambient**: Tense atmospheric background
- **Combat**: Intense music during zombie encounters
- **Victory**: Triumphant escape theme

## Development Phases

### Phase 1: Core Systems (2-3 weeks)
- [ ] Zombie entity implementation
- [ ] Basic AI and pathfinding
- [ ] Weapon system foundation
- [ ] Collision detection
- [ ] Health and damage systems

### Phase 2: Game Loop (2-3 weeks)
- [ ] Car component system
- [ ] Inventory management
- [ ] Map generation
- [ ] Spawn system
- [ ] Victory conditions

### Phase 3: Polish and UI (1-2 weeks)
- [ ] User interface elements
- [ ] Sound integration
- [ ] Visual effects
- [ ] Game state management

### Phase 4: Balance and Testing (1 week)
- [ ] Gameplay balancing
- [ ] Bug testing
- [ ] Performance optimization
- [ ] Final polish

## Technical Requirements

### Dependencies
- Python 3.8+
- Arcade library
- Pyglet (included with Arcade)
- Additional libraries: math, random, enum, asyncio

### Performance Targets
- **FPS**: Maintain 60+ FPS with 50+ zombies
- **Memory**: < 512MB RAM usage
- **Loading**: < 3 seconds initial load time

### File Structure
```
game/
├── main.py              # Main game loop
├── entities/
│   ├── player.py        # Player class
│   ├── zombie.py        # Zombie class
│   └── bullet.py        # Bullet class
├── systems/
│   ├── weapon_system.py # Weapon management
│   ├── inventory.py     # Inventory system
│   └── car_assembly.py  # Car component system
├── ui/
│   ├── hud.py          # HUD elements
│   └── menus.py        # Menu systems
└── utils/
    ├── constants.py     # Game constants
    └── helpers.py       # Utility functions
```

## Quality Assurance

### Testing Checklist
- [ ] Player movement and controls
- [ ] Weapon switching and firing
- [ ] Zombie AI and pathfinding
- [ ] Collision detection accuracy
- [ ] UI element functionality
- [ ] Audio playback
- [ ] Performance under load

### Bug Priorities
1. **Critical**: Game crashes, save corruption
2. **High**: Gameplay breaking bugs
3. **Medium**: UI/UX issues
4. **Low**: Minor visual glitches

## Future Enhancements

### Post-Launch Features
- **Multiplayer**: Cooperative survival mode
- **Difficulty Levels**: Varying zombie spawn rates
- **Weapon Upgrades**: Modification system
- **Additional Maps**: New environments
- **Character Customization**: Multiple player models
- **Achievements**: Progress tracking system

### Technical Improvements
- **Procedural Generation**: Random map layouts
- **Advanced AI**: Smarter zombie behavior
- **Physics Upgrades**: Realistic bullet physics
- **Graphics Enhancement**: Lighting and shadows

## Final Game Completion Checklists

### 🎮 Core Game Systems
- [ ] **Player Entity System**
  - [ ] Player movement with WASD controls
  - [ ] Mouse-based aiming and rotation
  - [ ] Health system with damage/healing
  - [ ] Death and respawn mechanics
  - [ ] Player state management (idle, walking, shooting, dead)
  - [ ] Animation system with all weapon types
  - [ ] Inventory system for weapons and items

- [ ] **Zombie System**
  - [ ] Zombie entity class with health/damage
  - [ ] Basic AI pathfinding toward player
  - [ ] Zombie spawning system with waves
  - [ ] Multiple zombie types (walker, runner, brute)
  - [ ] Zombie attack mechanics and damage
  - [ ] Death animations and cleanup
  - [ ] Zombie sound effects (groans, footsteps)

- [ ] **Weapon System**
  - [ ] Base weapon class with common properties
  - [ ] Pistol implementation (fast, low damage)
  - [ ] Rifle implementation (medium speed, high damage)
  - [ ] Shotgun implementation (slow, spread damage)
  - [ ] Flamethrower implementation (continuous, area damage)
  - [ ] Melee weapons (bat, knife)
  - [ ] Weapon switching (1-5 keys)
  - [ ] Ammunition system with pickup mechanics
  - [ ] Reload mechanics and animations

- [ ] **Combat System**
  - [ ] Bullet entity with physics
  - [ ] Collision detection (bullets vs zombies)
  - [ ] Damage calculation system
  - [ ] Muzzle flash effects
  - [ ] Blood splatter effects
  - [ ] Screen shake on impact
  - [ ] Weapon recoil mechanics

### 🗺️ World and Environment
- [ ] **Map System**
  - [ ] Tilemap implementation using provided assets
  - [ ] Building placement and collision
  - [ ] Obstacle and cover system
  - [ ] Spawn point system for zombies
  - [ ] Safe zone areas
  - [ ] Map boundaries and constraints

- [ ] **Car Assembly System**
  - [ ] Define 8 required car components
  - [ ] Component spawn locations on map
  - [ ] Component pickup mechanics
  - [ ] Progress tracking system
  - [ ] Visual indicators for component locations
  - [ ] Car assembly interface
  - [ ] Victory condition when all components collected

- [ ] **Item System**
  - [ ] Weapon pickups with visual indicators
  - [ ] Ammo pickup system
  - [ ] Health pack/medical supplies
  - [ ] Car component pickups
  - [ ] Pickup sound effects and notifications

### 🎨 User Interface
- [ ] **HUD Elements**
  - [ ] Health bar with damage visualization
  - [ ] Ammo counter for current weapon
  - [ ] Weapon indicator showing current weapon
  - [ ] Car component progress display
  - [ ] Minimap showing player, zombies, objectives
  - [ ] Crosshair following mouse cursor
  - [ ] Damage indicators when hit

- [ ] **Menu Systems**
  - [ ] Main menu (Start, Options, Quit)
  - [ ] Pause menu (Resume, Restart, Settings, Quit)
  - [ ] Game over screen with restart option
  - [ ] Victory screen with statistics
  - [ ] Options menu (volume, controls, graphics)
  - [ ] Credits screen

- [ ] **Inventory Interface**
  - [ ] Weapon selection display
  - [ ] Ammo count for each weapon type
  - [ ] Car component collection status
  - [ ] Tab-based inventory navigation

### 🔊 Audio Implementation
- [ ] **Sound Effects**
  - [ ] Weapon firing sounds for each weapon type
  - [ ] Weapon reload sounds
  - [ ] Weapon switching sounds
  - [ ] Zombie vocal sounds (groans, growls)
  - [ ] Zombie movement sounds (footsteps, dragging)
  - [ ] Player footstep sounds
  - [ ] Item pickup sounds
  - [ ] UI interaction sounds (clicks, hovers)
  - [ ] Environmental ambient sounds

- [ ] **Music System**
  - [ ] Background ambient music
  - [ ] Combat music during zombie encounters
  - [ ] Victory music for escape
  - [ ] Menu music
  - [ ] Dynamic music system based on threat level

### 🎭 Animation and Visual Effects
- [ ] **Player Animations**
  - [ ] Idle animations for each weapon type
  - [ ] Walking animations for each weapon type
  - [ ] Shooting animations for each weapon type
  - [ ] Death animation sequence
  - [ ] Weapon switching transitions

- [ ] **Zombie Animations**
  - [ ] Walking/shambling animations
  - [ ] Attack animations
  - [ ] Death animations
  - [ ] Idle/standing animations

- [ ] **Visual Effects**
  - [ ] Muzzle flash particles
  - [ ] Blood splatter effects
  - [ ] Explosion effects (if applicable)
  - [ ] Screen shake for impacts
  - [ ] Particle system for ambient effects
  - [ ] Lighting effects for weapons

### 🧪 Testing and Quality Assurance
- [ ] **Gameplay Testing**
  - [ ] Player movement responsiveness
  - [ ] Weapon switching functionality
  - [ ] Zombie AI behavior verification
  - [ ] Combat balance testing
  - [ ] Component collection mechanics
  - [ ] Victory condition testing

- [ ] **Performance Testing**
  - [ ] Frame rate stability with multiple zombies
  - [ ] Memory usage optimization
  - [ ] Loading time optimization
  - [ ] Collision detection performance
  - [ ] Audio performance testing

- [ ] **Bug Testing**
  - [ ] Edge case scenario testing
  - [ ] Boundary condition testing
  - [ ] Input validation testing
  - [ ] Save/load functionality (if applicable)
  - [ ] Error handling and recovery

### 🎯 Game Balance and Tuning
- [ ] **Difficulty Tuning**
  - [ ] Zombie spawn rates
  - [ ] Weapon damage values
  - [ ] Player health values
  - [ ] Ammo availability
  - [ ] Component spawn distribution

- [ ] **Gameplay Flow**
  - [ ] Early game progression
  - [ ] Mid-game challenge scaling
  - [ ] End-game difficulty curve
  - [ ] Player feedback systems
  - [ ] Reward distribution

### 🚀 Final Polish and Release
- [ ] **Code Quality**
  - [ ] Code documentation and comments
  - [ ] Error handling and logging
  - [ ] Performance optimization
  - [ ] Code cleanup and refactoring
  - [ ] Version control and backup

- [ ] **Asset Integration**
  - [ ] All art assets properly integrated
  - [ ] Audio assets correctly implemented
  - [ ] Asset optimization for file size
  - [ ] Proper asset attribution

- [ ] **User Experience**
  - [ ] Tutorial or instruction system
  - [ ] Clear objective communication
  - [ ] Intuitive control scheme
  - [ ] Visual feedback for all actions
  - [ ] Accessibility considerations

- [ ] **Release Preparation**
  - [ ] Final build testing
  - [ ] Installation/setup instructions
  - [ ] README file creation
  - [ ] License and legal compliance
  - [ ] Distribution package creation

### 📋 Milestone Checkpoints

#### **Alpha Build** (Core Systems Complete)
- [ ] Player can move and shoot
- [ ] Basic zombies spawn and attack
- [ ] Simple weapon system functional
- [ ] Basic collision detection working

#### **Beta Build** (Feature Complete)
- [ ] All weapon types implemented
- [ ] Car component system functional
- [ ] UI elements complete
- [ ] Audio system integrated
- [ ] Victory condition achievable

#### **Release Candidate** (Polish Complete)
- [ ] All bugs fixed
- [ ] Performance optimized
- [ ] All assets finalized
- [ ] Complete testing passed
- [ ] Documentation complete

#### **Gold Master** (Ready for Release)
- [ ] Final build verified
- [ ] All checklists completed
- [ ] User testing completed
- [ ] Performance benchmarks met
- [ ] Ready for distribution

---

## Conclusion

This zombie shooter game combines classic top-down action with resource management and objective-based gameplay. The modular design allows for iterative development and easy expansion of features. The focus on tight controls, responsive combat, and clear objectives ensures an engaging player experience.

**Next Steps**: Begin implementation with Phase 1 focusing on core zombie and weapon systems to establish the fundamental gameplay loop. 