#!/usr/bin/env python3
"""
Test script to verify car interaction logic
"""

from src.sprites.car import Car
from src.constants import REQUIRED_CAR_PARTS

def test_car_interaction():
    """Test car interaction logic"""
    print("=== Testing Car Interaction Logic ===")
    
    # Create a new car (not starting car)
    car = Car((100, 100), is_starting_car=False)
    
    print(f"Initial car state:")
    print(f"  Is starting car: {car.is_starting_car}")
    print(f"  Required parts: {car.required_parts}")
    print(f"  Collected parts: {car.collected_parts}")
    print(f"  Can use: {car.can_use()}")
    print(f"  Can interact: {car.can_interact()}")
    
    # Add parts one by one
    for i in range(REQUIRED_CAR_PARTS + 1):
        print(f"\n--- Adding part {i+1} ---")
        part_added = car.add_part()
        print(f"  Part added: {part_added}")
        print(f"  Parts status: {car.get_parts_status()}")
        print(f"  Can use: {car.can_use()}")
        print(f"  Can interact: {car.can_interact()}")
        
        # Test interaction
        should_transition = car.handle_interaction()
        print(f"  Should transition: {should_transition}")
    
    print(f"\n=== Final Test ===")
    print(f"Final parts: {car.get_parts_status()}")
    print(f"Can use: {car.can_use()}")
    print(f"Can interact: {car.can_interact()}")
    
    # Test final interaction
    should_transition = car.handle_interaction()
    print(f"Final interaction should transition: {should_transition}")

if __name__ == "__main__":
    test_car_interaction() 