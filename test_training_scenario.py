
import os
import pygame
import json
from memory import Memory
from gl4_logic import VisionWindow

# Headless setup
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
screen = pygame.display.set_mode((800, 600))

def run_training_scenario():
    print("--- Starting Hierarchical Training Scenario ---")
    if os.path.exists("training_scenario.db"): os.remove("training_scenario.db")
    mem = Memory("training_scenario.db")
    vision = VisionWindow(screen, mem)

    # 1. Teach POINT
    print("\n[Step 1] Teaching POINT")
    vision.grid[0][0] = 1
    vision.cmd_box.text = "POINT"
    vision._process_learning()
    print(vision.status_msg)

    # 2. Teach LINE (using POINT as part)
    print("\n[Step 2] Teaching LINE (drawing a line including the POINT)")
    vision.grid = [[0 for _ in range(10)] for _ in range(10)]
    vision.grid[0][0] = 1
    vision.grid[0][1] = 1
    vision.cmd_box.text = "LINE"
    vision._process_learning()
    print(vision.status_msg)

    # 3. Teach ANGLE (using LINE as part)
    print("\n[Step 3] Teaching ANGLE (drawing an angle including the LINE)")
    vision.grid = [[0 for _ in range(10)] for _ in range(10)]
    vision.grid[0][0] = 1
    vision.grid[0][1] = 1
    vision.grid[1][1] = 1
    vision.cmd_box.text = "ANGLE"
    vision._process_learning()
    print(vision.status_msg)

    # 4. Final verification
    print("\n[Step 4] Final Verification of Cognitive Network:")
    cur = mem.conn.cursor()
    cur.execute("SELECT name, component_rules FROM cognitive_productions WHERE production_type='VISUAL_PATTERN'")
    for name, comps in cur.fetchall():
        print(f"Concept '{name}' has components (IDs): {comps}")

    mem.close()
    print("\n--- Training Scenario Completed ---")

if __name__ == "__main__":
    run_training_scenario()
