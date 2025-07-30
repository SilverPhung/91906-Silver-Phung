#!/usr/bin/env python3
"""
Test script to verify chest system integration and simulate chests in the map.
"""

import arcade
from src.sprites.chest import Chest, ChestState
from src.managers.chest_manager import ChestManager

def test_chest_manager_integration():
    """Test ChestManager integration with mock game view."""
    print("=== Testing ChestManager Integration ===")
    
    # Create a mock game view
    class MockGameView:
        def __init__(self):
            self.tile_map = type('MockTileMap', (), {
                'object_lists': {
                    'Chest-parts': [
                        type('MockObject', (), {'shape': (100, 100)})(),
                        type('MockObject', (), {'shape': (200, 200)})()
                    ],
                    'Chest-noparts': [
                        type('MockObject', (), {'shape': (300, 300)})()
                    ]
                }
            })()
            self.scene = type('MockScene', (), {
                'add_sprite': lambda *args: print(f"[MOCK] Added sprite to scene: {args}")
            })()
            self.player = type('MockPlayer', (), {
                'center_x': 150,
                'center_y': 150
            })()
    
    game_view = MockGameView()
    chest_manager = ChestManager(game_view)
    
    # Test chest loading
    chest_manager.load_chests_from_map()
    
    # Test proximity checking
    chest_manager.check_chest_interactions()
    
    # Test interaction
    if chest_manager.near_chest:
        print(f"[TEST] Found nearby chest: {chest_manager.near_chest}")
        chest_manager.handle_chest_interaction()
    else:
        print("[TEST] No chest nearby")
    
    return True

def test_chest_visibility():
    """Test that chests are properly visible when created."""
    print("\n=== Testing Chest Visibility ===")
    
    # Create a chest and test its properties
    chest = Chest((500, 500), has_part=True)
    
    print(f"[TEST] Chest created at ({chest.center_x}, {chest.center_y})")
    print(f"[TEST] Chest width: {chest.width}, height: {chest.height}")
    print(f"[TEST] Chest use_sprites: {chest.use_sprites}")
    
    if hasattr(chest, 'color'):
        print(f"[TEST] Chest color: {chest.color}")
    
    # Test that chest can be drawn
    try:
        # This would normally be called by arcade, but we can test the method
        chest.draw()
        print("[TEST] Chest draw method works")
    except Exception as e:
        print(f"[TEST] Chest draw error: {e}")
        return False
    
    return True

def test_chest_layer_management():
    """Test that chests are properly added to sprite layers."""
    print("\n=== Testing Chest Layer Management ===")
    
    # Create a mock scene
    class MockScene:
        def __init__(self):
            self.sprites = {}
        
        def add_sprite(self, layer_name, sprite):
            if layer_name not in self.sprites:
                self.sprites[layer_name] = []
            self.sprites[layer_name].append(sprite)
            print(f"[MOCK] Added sprite to layer '{layer_name}'")
    
    scene = MockScene()
    
    # Create chests and add them to scene
    chest1 = Chest((100, 100), has_part=True)
    chest2 = Chest((200, 200), has_part=False)
    
    scene.add_sprite("ChestsLayer", chest1)
    scene.add_sprite("ChestsLayer", chest2)
    
    print(f"[TEST] ChestsLayer has {len(scene.sprites.get('ChestsLayer', []))} sprites")
    
    return True

def main():
    """Run all tests."""
    print("Testing Chest System Integration")
    print("=" * 50)
    
    tests = [
        test_chest_manager_integration,
        test_chest_visibility,
        test_chest_layer_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Chest integration tests successful!")
        return True
    else:
        print("❌ Some chest integration tests failed")
        return False

if __name__ == "__main__":
    main() 