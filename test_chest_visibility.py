#!/usr/bin/env python3
"""
Simple test to verify chest visibility and add test chests to the map.
"""

import arcade
from src.sprites.chest import Chest

def test_chest_creation():
    """Test that chests can be created and are visible."""
    print("=== Testing Chest Creation ===")
    
    # Test chest with part
    chest_with_part = Chest((100, 100), has_part=True)
    print(f"[TEST] Chest with part created at ({chest_with_part.center_x}, {chest_with_part.center_y})")
    print(f"[TEST] Chest width: {chest_with_part.width}, height: {chest_with_part.height}")
    print(f"[TEST] Chest use_sprites: {chest_with_part.use_sprites}")
    
    if hasattr(chest_with_part, 'color'):
        print(f"[TEST] Chest color: {chest_with_part.color}")
    
    # Test chest without part
    chest_without_part = Chest((200, 200), has_part=False)
    print(f"[TEST] Chest without part created at ({chest_without_part.center_x}, {chest_without_part.center_y})")
    
    return True

def test_chest_draw():
    """Test that chests can be drawn."""
    print("\n=== Testing Chest Drawing ===")
    
    chest = Chest((300, 300), has_part=True)
    
    try:
        # This would normally be called by arcade, but we can test the method
        chest.draw()
        print("[TEST] Chest draw method works")
        return True
    except Exception as e:
        print(f"[TEST] Chest draw error: {e}")
        return False

def main():
    """Run chest visibility tests."""
    print("Testing Chest Visibility")
    print("=" * 30)
    
    tests = [test_chest_creation, test_chest_draw]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
    
    print(f"\n{'=' * 30}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Chest visibility tests successful!")
        return True
    else:
        print("❌ Some chest visibility tests failed")
        return False

if __name__ == "__main__":
    main() 