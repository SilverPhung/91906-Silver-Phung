#!/usr/bin/env python3
"""
Character Asset Analyzer

This tool analyzes character folders and generates JSON configuration
files with image paths and anchor point settings for proper sprite rotation.

Usage:
    python character_analyzer.py

This will scan the Players and Zombies directories and generate:
- resources/animation_config/players_config.json
- resources/animation_config/zombies_config.json

The developer can then manually edit these JSON files to set the anchor points
for each sprite based on the character's center of mass.
"""

import os
import json
from PIL import Image
import glob
from typing import Dict, Any

# Default asset directories
DEFAULT_PLAYER_ASSETS_DIR = "resources/Players"
DEFAULT_ZOMBIE_ASSETS_DIR = "resources/Zombies"
OUTPUT_DIR = "resources/animation_config"


def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get the dimensions of an image file."""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return (0, 0)


def analyze_player_directory(base_dir: str) -> Dict[str, Any]:
    """Analyze the player directory structure and generate configuration."""
    config = {}

    if not os.path.exists(base_dir):
        print(f"Player directory not found: {base_dir}")
        return config

    # Get all character folders (Girl, Man, etc.)
    character_folders = [
        f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))
    ]

    for character in character_folders:
        character_path = os.path.join(base_dir, character)
        config[character] = {}

        # Get all animation folders for this character
        animation_folders = [
            f
            for f in os.listdir(character_path)
            if os.path.isdir(os.path.join(character_path, f))
        ]

        for animation in animation_folders:
            animation_path = os.path.join(character_path, animation)

            # Get all PNG files in this animation folder
            png_files = glob.glob(os.path.join(animation_path, "*.png"))
            png_files.sort()

            animation_type = "Movement"  # Default to Movement
            if animation.startswith("Walk_"):
                animation_type = "Movement"
            else:
                animation_type = "Action"  # For players, not Walk_

            if png_files:
                # Get dimensions from first frame (all frames should have same dimensions)
                width, height = get_image_dimensions(png_files[0])

                # Create animation configuration with anchor points at animation level
                config[character][animation] = {
                    "anchor_x": width // 2,  # Default to center
                    "anchor_y": height // 2,  # Default to center
                    "width": width,
                    "height": height,
                    "frames": [png_file.replace("\\", "/") for png_file in png_files],
                    "animation_type": animation_type,
                }

            print(f"Processed {character}/{animation}: {len(png_files)} frames")

    return config


def analyze_zombie_directory(base_dir: str) -> Dict[str, Any]:
    """Analyze the zombie directory structure and generate configuration."""
    config = {}

    if not os.path.exists(base_dir):
        print(f"Zombie directory not found: {base_dir}")
        return config

    # Get all zombie type folders (Army_zombie, Cop_Zombie, etc.)
    zombie_folders = [
        f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))
    ]

    for zombie_type in zombie_folders:
        zombie_path = os.path.join(base_dir, zombie_type)
        config[zombie_type] = {}

        # Get all animation folders for this zombie type
        animation_folders = [
            f
            for f in os.listdir(zombie_path)
            if os.path.isdir(os.path.join(zombie_path, f))
        ]

        for animation in animation_folders:
            animation_path = os.path.join(zombie_path, animation)

            # Get all PNG files in this animation folder
            png_files = glob.glob(os.path.join(animation_path, "*.png"))
            png_files.sort()

            animation_type = "Movement"  # Default to Movement
            if animation == "Walk":
                animation_type = "Movement"
            elif animation in ["Attack", "Death"]:
                animation_type = "Action"

            if png_files:
                # Get dimensions from first frame (all frames should have same dimensions)
                width, height = get_image_dimensions(png_files[0])

                # Create animation configuration with anchor points at animation level
                config[zombie_type][animation] = {
                    "anchor_x": width // 2,  # Default to center
                    "anchor_y": height // 2,  # Default to center
                    "width": width,
                    "height": height,
                    "frames": [png_file.replace("\\", "/") for png_file in png_files],
                    "animation_type": animation_type,
                }

            print(f"Processed {zombie_type}/{animation}: {len(png_files)} frames")

    return config


def generate_sample_config():
    """Generate a sample configuration to show the expected format."""
    sample = {
        "Girl": {
            "Walk_gun": {
                "anchor_x": 64,
                "anchor_y": 80,
                "width": 128,
                "height": 128,
                "frames": [
                    "resources/Players/Girl/Walk_gun/Walk_gun_000.png",
                    "resources/Players/Girl/Walk_gun/Walk_gun_001.png",
                    "resources/Players/Girl/Walk_gun/Walk_gun_002.png",
                ],
                "animation_type": "Movement",
            },
            "Riffle": {
                "anchor_x": 64,
                "anchor_y": 80,
                "width": 128,
                "height": 128,
                "frames": [
                    "resources/Players/Girl/Riffle/Riffle_000.png",
                    "resources/Players/Girl/Riffle/Riffle_001.png",
                    "resources/Players/Girl/Riffle/Riffle_002.png",
                ],
                "animation_type": "Action",
            },
        }
    }

    sample_config_path = os.path.join(OUTPUT_DIR, "sample_config.json")
    with open(sample_config_path, "w") as f:
        json.dump(sample, f, indent=2)

    print(f"Generated {sample_config_path} to show expected format")


def get_user_input():
    """Get user input for character folder paths."""
    print("Character Asset Analyzer")
    print("=" * 50)

    # Get player assets directory
    player_input = input(
        f"Enter player assets directory path "
        f"(default: {DEFAULT_PLAYER_ASSETS_DIR}): "
    ).strip()
    player_dir = player_input if player_input else DEFAULT_PLAYER_ASSETS_DIR

    # Get zombie assets directory
    zombie_input = input(
        f"Enter zombie assets directory path "
        f"(default: {DEFAULT_ZOMBIE_ASSETS_DIR}): "
    ).strip()
    zombie_dir = zombie_input if zombie_input else DEFAULT_ZOMBIE_ASSETS_DIR

    return player_dir, zombie_dir


def main():
    """Main function to analyze all character directories."""
    # Get user input for paths
    player_dir, zombie_dir = (
        DEFAULT_PLAYER_ASSETS_DIR,
        DEFAULT_ZOMBIE_ASSETS_DIR,
    )

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Analyze player assets
    print("\nAnalyzing Player Assets...")
    player_config = analyze_player_directory(player_dir)

    if player_config:
        player_config_path = os.path.join(OUTPUT_DIR, "players_config.json")
        with open(player_config_path, "w") as f:
            json.dump(player_config, f, indent=2)
        print(
            f"Generated {player_config_path} with " f"{len(player_config)} characters"
        )

    # Analyze zombie assets
    print("\nAnalyzing Zombie Assets...")
    zombie_config = analyze_zombie_directory(zombie_dir)

    if zombie_config:
        zombie_config_path = os.path.join(OUTPUT_DIR, "zombies_config.json")
        with open(zombie_config_path, "w") as f:
            json.dump(zombie_config, f, indent=2)
        print(
            f"Generated {zombie_config_path} with " f"{len(zombie_config)} zombie types"
        )

    print("\n" + "=" * 50)
    print("Configuration files generated in:", OUTPUT_DIR)
    print("\nNext steps:")
    players_config = os.path.join(OUTPUT_DIR, "players_config.json")
    zombies_config = os.path.join(OUTPUT_DIR, "zombies_config.json")
    print(f"1. Open {players_config} and {zombies_config}")
    print(
        "2. For each animation folder, adjust anchor_x and anchor_y to "
        "match the character's center of mass"
    )
    print("3. anchor_x: pixels from left edge to center of mass")
    print("4. anchor_y: pixels from bottom edge to center of mass")
    print("5. Use an image editor to measure these values visually")
    print("6. All frames in the same animation will share the same " "anchor point")
    print("7. Update your game code to load from these configuration files")


if __name__ == "__main__":
    main()
