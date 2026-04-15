
import os
import sys
import pygame

# Mock display for headless environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from main import GeneralLearnerApp, export_cognitive_network_image
from constants import *

def run_headless_simulation(steps=100):
    print(f"Starting headless simulation for {steps} steps...")
    app = GeneralLearnerApp()
    
    # Force autonomous mode
    app.autonomous = True
    
    for i in range(steps):
        # Execute steps for both bots
        app._execute_bot_step(1)
        app._execute_bot_step(2)
        
        if (i + 1) % 20 == 0:
            print(f"Step {i+1}/{steps} completed...")
            
    print("Simulation finished. Exporting data...")
    
    # Export cognitive network for both bots
    app.active_bot = 1
    export_cognitive_network_image(app, bot_id=1, filepath="simulation_bot1_network.png")
    
    app.active_bot = 2
    export_cognitive_network_image(app, bot_id=2, filepath="simulation_bot2_network.png")
    
    # Export full behavioral report
    app.export_report()
    
    print("All exports completed successfully.")

if __name__ == "__main__":
    try:
        run_headless_simulation(100)
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
