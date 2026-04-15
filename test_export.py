#!/usr/bin/env python3
"""
Test script to verify the enhanced export function works correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_export_function():
    """Test the export function with a mock app"""
    try:
        # Import required modules
        import main
        from memory import Memory
        from learner import Learner
        from environment import Environment
        from robot import Robot
        import pygame

        # Initialize pygame (needed for some components)
        pygame.init()

        # Create a minimal app-like object for testing
        class MockApp:
            def __init__(self):
                self.env = Environment()
                self.memory_bot1 = Memory("test_bot1_memory.db")
                self.robot1 = Robot(self.env, self_id=1)
                self.robot1.x = 5
                self.robot1.y = 5
                self.learner1 = Learner(self.memory_bot1, self.env)

        print("Creating mock app...")
        app = MockApp()

        # Add some test data to make the export more interesting
        print("Adding test data to memory...")

        # Add some concepts
        concept_ids = []
        for concept in ["GO_FORWARD", "TURN_LEFT", "BATTERY", "WALL", "SELF_POSITION"]:
            concept_id = app.memory_bot1.get_or_create_concept_id(concept)
            concept_ids.append(concept_id)
            print(f"Created concept '{concept}' with ID {concept_id}")

        # Add some rules
        import json

        for i in range(5):
            perception = {"SELF_BATTERY_DIST": "NEAR", "FRONT_WALL": "FAR"}
            action = i % 4  # Cycle through actions
            weight = (i + 1) * 2.0
            app.memory_bot1.add_rule(
                perception_pattern=perception,
                action=action,
                weight=weight,
                memory_type=1,  # SEMANTIC
            )
            print(f"Added rule {i}: {perception} -> action {action} (weight {weight})")

        # Add some relational frames
        if len(concept_ids) >= 2:
            app.memory_bot1.add_relational_frame(
                concept_ids[0], "COORD", concept_ids[1], strength=0.8
            )
            print(f"Added COORD frame between {concept_ids[0]} and {concept_ids[1]}")

        if len(concept_ids) >= 3:
            app.memory_bot1.add_relational_frame(
                concept_ids[0], "OPP", concept_ids[2], strength=0.6
            )
            print(f"Added OPP frame between {concept_ids[0]} and {concept_ids[2]}")

        # Test the export function
        print("\nTesting export_cognitive_network_image function...")
        result_path = main.export_cognitive_network_image(
            app, bot_id=1, filepath="test_cognitive_network.png"
        )

        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"SUCCESS: Export completed successfully!")
            print(f"File saved as: {result_path}")
            print(f"File size: {file_size} bytes")

            # Clean up test files
            try:
                os.remove("test_bot1_memory.db")
                os.remove("test_cognitive_network.png")
                print("Cleaned up test files")
            except:
                pass

            return True
        else:
            print("ERROR: Export failed - file not created")
            return False

    except Exception as e:
        print(f"ERROR: Exception occurred during test: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        try:
            pygame.quit()
        except:
            pass


if __name__ == "__main__":
    print("Testing enhanced cognitive network export function...")
    success = test_export_function()
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)
