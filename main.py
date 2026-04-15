"""
################################################################################
#                                                                              #
#      ______ ______ _   _ ______ _____         _       _                      #
#     |  ____|  ____| \ | |  ____|  __ \   /\   | |     | |                     #
#     | |__  | |__  |  \| | |__  | |__) | /  \  | |     | |                     #
#     |  __| |  __| | . ` |  __| |  _  / / /\ \ | |     | |                     #
#     | |____| |____| |\  | |____| | \ \/ ____ \| |____ | |____                 #
#     |______|______|_| \_|______|_|  \_\/_/    \_\______|______|                #
#                                                                              #
#      _      ______          _____  _   _ ______ _____                        #
#     | |    |  ____|   /\   |  __ \| \ | |  ____|  __ \                       #
#     | |    | |__     /  \  | |__) |  \| | |__  | |__) |                      #
#     | |    |  __|   / /\ \ |  _  /| . ` |  __| |  _  /                       #
#     | |____| |____ / ____ \| | \ \| |\  | |____| | \ \                       #
#     |______|______/_/    \_\_|  \_\_| \_|______|_|  \_\                      #
#                                                                              #
################################################################################

GENERAL LEARNER 5 (GL5) - THE COGNITIVE ORCHESTRATOR
===================================================

This is the primary entry point for the General Learner 5 simulation. It 
implements the "Synthetic Theatre" where the cognitive architecture meets 
the environment.

SCIENTIFIC FOUNDATIONS:
-----------------------
1. CYBERNETICS & HOMEOSTASIS:
   Based on W. Grey Walter's "Machina Speculatrix" (1950). The robots 
   (Bot 1 & 2) seek "phototropic" equivalents (batteries) to satisfy 
   internal homeostatic drives (hunger/tiredness).
   Ref: Walter, W. G. (1953). The Living Brain. Norton.

2. UNIVERSAL LEARNER PRINCIPLE:
   Implements Walter Fritz's architecture where an agent must autonomously 
   map perceptions to actions via reinforcement.
   Ref: Fritz, W. (1989). The General Learner. 

3. GLOBAL WORKSPACE THEORY (GWT):
   Orchestrates the competition for consciousness between specialized 
   modules (Vision, Spatial, Motor).
   Ref: Baars, B. J. (1988). A Cognitive Theory of Consciousness.

4. DUAL-BOT EXPERIMENTAL FRAMEWORK:
   Implements social learning and Pauli Exclusion (collision physics) 
   between two autonomous agents.

Author: Marco
Project: General_Learner_5 (GL5)
"""

import pygame
import sys
import json
import sqlite3
import psutil
import os
from constants import *
from environment import Environment
from robot import Robot
from memory import Memory
from learner import Learner
from experiment_logger import ExperimentLogger
from gwt import GWTIntegrator
import math
import graphics
from graphics import (
    Button,
    TextBox,
    create_robot_icon,
    create_battery_icon,
    create_wall_icon,
    create_mirror_icon,
    create_reset_button_icon,
)


class GeneralLearnerApp:
    """
    ############################################################################
    #   _____ _      _        _____        _____  _____                        #
    #  / ____| |    | |      / ____|      / ____|/ ____|                       #
    # | |  __| |    | |     | (___       | (___ | |                            #
    # | | |_ | |    | |      \___ \       \___ \| |                            #
    # | |__| | |____| |____  ____) |      ____) | |____                        #
    #  \_____|______|______||_____/      |_____/ \_____|                       #
    ############################################################################

    Main Application class for the General Learner 5.
    
    This class acts as the 'Central Nervous System' of the simulation, 
    managing the PyGame loop, UI events, and the interaction between 
    the environment and the cognitive bots.

    CORE RESPONSIBILITIES:
    - Initializing the Environment (The Labyrinth).
    - Managing Bot 1 & Bot 2 instances.
    - Routing UI events (Manual Reinforcement, Command Entry, Dream cycles).
    - Visualizing the 'Global Workspace' and 'Situational Maps'.
    - Logging experimental data for research analysis.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("General Learner 4 - Cognitive Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 12)

        # Initialize Core Components
        self.env = Environment()

        # Bot 1 (primary) - starts at center
        self.memory_bot1 = Memory("bot1_memory.db")
        self.robot1 = Robot(self.env, self_id=1)
        self.robot1.x = GRID_W // 2
        self.robot1.y = GRID_H // 2
        self.learner1 = Learner(self.memory_bot1, self.env)
        self.gwt1 = GWTIntegrator(self.env, self.robot1, self.memory_bot1)

        # Bot 2 (dual-bot) - starts offset from center to respect Pauli Exclusion
        self.memory_bot2 = Memory("bot2_memory.db")
        self.robot2 = Robot(self.env, self_id=2)
        self.robot2.x = GRID_W // 2
        self.robot2.y = GRID_H // 2 + 1  # Offset by 1 tile
        self.learner2 = Learner(self.memory_bot2, self.env)
        self.gwt2 = GWTIntegrator(self.env, self.robot2, self.memory_bot2)

        # Active bot selector
        self.active_bot = 1  # 1 or 2

        # Per-bot step tracking for experimental framework
        self.bot1_steps = 0
        self.bot2_steps = 0

        # GL5 Dual-Bot: Experimental framework logger (Spec 5)
        self.experiment_logger = ExperimentLogger()

        # Helper properties for active bot access
        self.last_action_reward = 0

        self.autonomous = False
        self.guide_mode = False
        self.guide_path = []  # Visualization of the path being taught
        self.total_steps = 0
        self.stats_history = []  # Stores (step, score, rules_count)
        self.show_network = False
        self.view_mode = "SITUATIONAL"  # 'SITUATIONAL' or 'TERRITORY'

        # Load Graphical Assets (Procedural Bitmaps)
        self.robot_img = create_robot_icon(CELL_SIZE)
        self.robot1_img = create_robot_icon(
            CELL_SIZE, (50, 100, 200)
        )  # Bot 1: darker blue
        self.robot2_img = create_robot_icon(CELL_SIZE, (200, 100, 50))  # Bot 2: orange
        self.battery_img = create_battery_icon(CELL_SIZE)
        self.wall_img = create_wall_icon(CELL_SIZE)
        self.mirror_img = create_mirror_icon(CELL_SIZE)
        self.reset_button_img = create_reset_button_icon(CELL_SIZE)

        self.last_action_reward = 0
        self.timer = 0
        self.step_delay = 500  # Autonomous mode step delay in ms

        # Dream/sleep cooldown to prevent overload
        self._dream_cooldown = 0
        self._in_dream = False

        # UI Layout Setup
        self._init_buttons()

        # Performance caching
        self._cache_timestamp = 0
        self._cache_rules = None
        self._cache_frames = None
        self._cache_graph = None
        self._cache_interval = 10  # Refresh every 10 frames

    def _init_buttons(self):
        btn_x = CANVAS_WIDTH + 20
        btn_w = PANEL_WIDTH - 40
        y_off = 20
        step_y = BTN_HEIGHT + BTN_MARGIN

        # Behavior Control
        self.btn_auto = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "AUTONOMOUS", GRAY)
        y_off += step_y
        self.btn_comm = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "COMMAND", GRAY)
        y_off += step_y

        # Direct Command Interface
        self.txt_box = TextBox(btn_x, y_off, btn_w, 25)
        y_off += 30
        self.btn_do = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DO ACTION", GRAY)
        y_off += step_y

        # Manual Reinforcement
        self.btn_plus = Button(btn_x, y_off, btn_w // 2 - 5, BTN_HEIGHT, "+", GREEN)
        self.btn_minus = Button(
            btn_x + btn_w // 2 + 5, y_off, btn_w // 2 - 5, BTN_HEIGHT, "-", RED
        )
        y_off += step_y

        # Knowledge Management
        self.btn_sleep = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "DREAM / SLEEP", BLUE)
        y_off += step_y
        self.btn_clear = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "CLEAR MEMORY", RED)
        y_off += step_y

        # Vicarious Learning
        self.btn_guide = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "GUIDE MODE", GRAY)
        y_off += step_y

        # Control & Reporting Buttons
        self.btn_network = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "SHOW NETWORK", PURPLE
        )
        y_off += step_y
        self.btn_territory = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "TERRITORY MAP", BLUE
        )
        y_off += step_y
        self.btn_bayes = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "TOGGLE BAYES", CYAN)
        y_off += step_y
        self.btn_pov = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "TOGGLE POV", CYAN)
        y_off += step_y
        self.btn_inform = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "EXPORT REPORT", YELLOW
        )
        y_off += step_y
        self.btn_inferences = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "INFERENCES", ORANGE
        )
        y_off += step_y
        self.btn_new_maze = Button(btn_x, y_off, btn_w, BTN_HEIGHT, "NEW MAZE", RED)
        y_off += step_y
        self.btn_reset_stagnation = Button(
            btn_x, y_off, btn_w, BTN_HEIGHT, "RESET STAGNATION", PINK
        )
        y_off += step_y

        # GL5 Dual-Bot: Bot Selector Buttons (spec 4)
        self.btn_bot1 = Button(btn_x, y_off, btn_w // 2 - 5, BTN_HEIGHT, "BOT 1", GRAY)
        self.btn_bot2 = Button(
            btn_x + btn_w // 2 + 5, y_off, btn_w // 2 - 5, BTN_HEIGHT, "BOT 2", GRAY
        )

        # UI States
        self.show_pov = False
        self.show_inferences = False

    @property
    def robot(self):
        """Returns the active robot based on active_bot selection."""
        return self.robot1 if self.active_bot == 1 else self.robot2

    @property
    def memory(self):
        """Returns the active memory based on active_bot selection."""
        return self.memory_bot1 if self.active_bot == 1 else self.memory_bot2

    @property
    def learner(self):
        """Returns the active learner based on active_bot selection."""
        return self.learner1 if self.active_bot == 1 else self.learner2

    @property
    def gwt(self):
        """Returns the active GWT integrator based on active_bot selection."""
        return self.gwt1 if self.active_bot == 1 else self.gwt2

    def get_active_robot(self):
        """Returns the active robot instance (for direct access)."""
        return self.robot1 if self.active_bot == 1 else self.robot2

    def get_other_robot(self):
        """Returns the other robot instance (for physics interaction)."""
        return self.robot2 if self.active_bot == 1 else self.robot1

    def run(self):
        """Standard PyGame simulation loop."""
        running = True
        while running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        """
        - [x] Update `constants.py` with `LIGHT_ORANGE`
        - [x] Implement `decay_rules` in `memory.py`
        - [x] Integrate rule decay into `learner.py`'s `sleep_cycle`
        - [x] Update `main.py` with active-state UI coloring (Light Orange)
        - [x] Final verification and walkthrough
        - [x] Extensive English documentation for all core files:
            - [x] `memory.py`
            - [x] `learner.py`
            - [x] `environment.py`
            - [x] `robot.py`
            - [x] `main.py`
            - [x] `graphics.py`
        - [/] Finalize `README.md` with screenshot and architecture overview
        - [ ] Verify planning behavior in Autonomous mode
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Textbox interaction: only execute step IF 'cmd' is True (when user presses Enter)
            cmd = self.txt_box.handle_event(event)
            if cmd is True:
                self.execute_step()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # Check sidebar button clicks
                if self.btn_auto.is_clicked(pos):
                    self.autonomous = not self.autonomous
                    if self.autonomous:
                        self.guide_mode = False  # Mutually exclusive
                elif self.btn_comm.is_clicked(pos):
                    self.autonomous = False
                    self.guide_mode = False
                elif self.btn_do.is_clicked(pos):
                    # Manual Step / Command Execution
                    self.execute_step()
                elif self.btn_plus.is_clicked(pos):
                    self.apply_manual_reinforcement(10)
                elif self.btn_minus.is_clicked(pos):
                    self.apply_manual_reinforcement(-10)
                elif self.btn_sleep.is_clicked(pos):
                    self.dream()
                elif self.btn_clear.is_clicked(pos):
                    self.memory.clear()
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Memory wiped.")
                elif self.btn_guide.is_clicked(pos):
                    self.guide_mode = not self.guide_mode
                    if self.guide_mode:
                        self.autonomous = False  # Stop auto logic
                    if not self.guide_mode:
                        self.guide_path = []
                elif self.btn_inform.is_clicked(pos):
                    self.export_report()
                elif self.btn_network.is_clicked(pos):
                    self.show_network = not self.show_network
                    self.view_mode = "SITUATIONAL"
                elif self.btn_territory.is_clicked(pos):
                    self.show_network = True
                    self.view_mode = "TERRITORY"
                if self.btn_bayes.is_clicked(event.pos):
                    self.learner.bayesian = not self.learner.bayesian
                if self.btn_pov.is_clicked(event.pos):
                    self.show_pov = not self.show_pov
                if self.btn_inferences.is_clicked(event.pos):
                    self.show_inferences = not self.show_inferences
                if self.btn_new_maze.is_clicked(event.pos):
                    self.env.reset()
                    self.robot.x, self.robot.y = GRID_W // 2, GRID_H // 2
                    self.robot.direction = DIR_N
                    self.learner.pos_history.clear()
                    self.learner.action_history.clear()
                    self.learner.active_plan.clear()
                    self._cache_graph = None
                    print("Maze regenerated and robot position reset.")
                if self.btn_reset_stagnation.is_clicked(event.pos):
                    self.learner.stagnant = False
                    self.learner.pos_history.clear()
                    self.learner.action_history.clear()
                    self.learner.active_plan.clear()
                    self.learner.agenda.clear()
                    print("Stagnation reset! Robot is free to move again.")

                # GL5 Dual-Bot: Bot selector buttons (Spec 4)
                if self.btn_bot1.is_clicked(event.pos):
                    self.active_bot = 1
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Switched to Bot 1")
                elif self.btn_bot2.is_clicked(event.pos):
                    self.active_bot = 2
                    self._cache_rules = None
                    self._cache_frames = None
                    self._cache_graph = None
                    print("Switched to Bot 2")

                # Grid interaction (Guide Mode)
                if pos[0] < CANVAS_WIDTH and pos[1] < CANVAS_HEIGHT:
                    gx, gy = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        if self.guide_mode:
                            self.handle_guide_click(gx, gy)

    def execute_step(self, forced_action=None):
        """Triggers the robot to perform a single step/decision cycle."""
        text_cmd = self.txt_box.text.strip() if self.txt_box.text else None

        # Check if guided (forced action = guided mode)
        is_guided = forced_action is not None
        if is_guided:
            self.learner._guided_this_step = True
        else:
            self.learner._guided_this_step = False

        other_robot = self.robot2 if self.active_bot == 1 else self.robot1
        
        # GL5.1: Integrate GWT cognitive cycle
        gwt_context = self.gwt.run_cycle()
        
        # Determine action: either the user-forced one (Guided) or the learner's act
        if forced_action is not None:
            action = forced_action
        else:
            action = self.learner.act(
                self.robot, text_command=text_cmd, other_bot=other_robot, gwt_context=gwt_context
            )

        reward = self.robot.step(action, other_robot)

        # GL5 Dual-Bot: Check if all batteries consumed → spawn reset button
        if self.env.count_batteries() == 0 and self.env.reset_button_pos is None:
            self.env.spawn_reset_button()

        # GL5 Dual-Bot: Check if robot stepped on reset button → respawn batteries
        current_tile = self.env.get_at(self.robot.x, self.robot.y)
        if current_tile == RESET_BUTTON_ID:
            self.env.respawn_batteries()
            print("Maze reset! Batteries respawned.")
            # GL5 Dual-Bot: Log reset trigger (Spec 5)
            self.experiment_logger.log_reset_trigger()

        # GL5 Dual-Bot: Log battery collection (Spec 5)
        if current_tile == BATTERY_ID:
            active_robot = self.robot1 if self.active_bot == 1 else self.robot2
            self.experiment_logger.log_battery_collected(active_robot.self_id)

        # GL5 Dual-Bot: Log collision events in manual mode (Spec 3 & 5)
        if getattr(self.robot, "last_collision", False):
            self.experiment_logger.log_collision(self.active_bot, -IMPACT_UNITS)
            self.experiment_logger.log_energy_delta(self.active_bot, -IMPACT_UNITS)

        # GL5 Dual-Bot: Log proximity events (within 2 tiles)
        dist = abs(self.robot.x - other_robot.x) + abs(self.robot.y - other_robot.y)
        if dist <= 2:
            self.experiment_logger.log_proximity_event(self.active_bot, dist)

        # 3. USE THE NEW AGNOSTIC LEARNING FLOW
        self.learner.learn(
            self.robot, action, reward, text_command=text_cmd, other_bot=other_robot
        )

        self.last_action_reward = reward
        self.guide_path = []
        self.total_steps += 1

        # Invalidate cache after learning
        self._cache_rules = None

        # Synchronize stats for reports
        if self.total_steps % 5 == 0:
            self.capture_stats()

    def _execute_bot_step(self, bot_id):
        """
        Executes a step for a specific bot in autonomous mode.

        Args:
            bot_id: 1 or 2, indicating which bot to step
        """
        robot = self.robot1 if bot_id == 1 else self.robot2
        other_robot = self.robot2 if bot_id == 1 else self.robot1
        memory = self.memory_bot1 if bot_id == 1 else self.memory_bot2
        learner = self.learner1 if bot_id == 1 else self.learner2
        gwt = self.gwt1 if bot_id == 1 else self.gwt2

        # GL5.1: Integrate GWT cognitive cycle
        gwt_context = gwt.run_cycle()

        # Get action from learner (pass other_bot for collision-aware perception)
        action = learner.act(robot, other_bot=other_robot, gwt_context=gwt_context)

        # Execute step with other bot for collision detection (Pauli Exclusion)
        reward = robot.step(action, other_robot)

        # GL5 Dual-Bot: Check if all batteries consumed → spawn reset button
        if self.env.count_batteries() == 0 and self.env.reset_button_pos is None:
            self.env.spawn_reset_button()

        # GL5 Dual-Bot: Check if robot stepped on reset button → respawn batteries
        current_tile = self.env.get_at(robot.x, robot.y)
        if current_tile == RESET_BUTTON_ID:
            self.env.respawn_batteries()
            print(f"Bot {bot_id} triggered maze reset! Batteries respawned.")
            # GL5 Dual-Bot: Log reset trigger (Spec 5)
            self.experiment_logger.log_reset_trigger()

        # GL5 Dual-Bot: Log battery collection (Spec 5)
        if current_tile == BATTERY_ID:
            self.experiment_logger.log_battery_collected(robot.self_id)

        # GL5 Dual-Bot: Log collision events (Spec 3 & 5)
        if getattr(robot, "last_collision", False):
            self.experiment_logger.log_collision(bot_id, -IMPACT_UNITS)
            self.experiment_logger.log_energy_delta(bot_id, -IMPACT_UNITS)

        # GL5 Dual-Bot: Log proximity events (within 2 tiles)
        dist = abs(robot.x - other_robot.x) + abs(robot.y - other_robot.y)
        if dist <= 2:
            self.experiment_logger.log_proximity_event(bot_id, dist)

        # Learn
        learner.learn(robot, action, reward, other_bot=other_robot)

        # Update step counts
        if bot_id == 1:
            self.bot1_steps += 1
        else:
            self.bot2_steps += 1
        self.total_steps += 1

    def capture_stats(self):
        """Records current metrics for the reporting dashboard."""
        rules_count = len(self._cache_rules) if self._cache_rules is not None else 0
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        cpu_percent = process.cpu_percent()
        self.stats_history.append(
            {
                "step": self.total_steps,
                "score": self.robot.score,
                "rules": rules_count,
                "memory_mb": round(mem_mb, 1),
                "cpu_percent": round(cpu_percent, 1),
            }
        )

    def apply_manual_reinforcement(self, amount):
        """Forces reinforcement for the last taken action using conceptual IDs."""
        history = self.memory.get_all_chrono()
        if history:
            last = history[-1]
            perc_id = json.dumps(last["perception"])
            cmd_id = None
            if last.get("command_text"):
                cmd_id = self.memory.get_or_create_concept_id(
                    last["command_text"].upper()
                )

            self.memory.add_rule(
                perc_id, last["action"], weight=amount, command_id=cmd_id
            )
            print(f"Manual reinforcement applied: {amount}")
            self._cache_rules = None

    def dream(self):
        """Triggers the Sleep Cycle for rules consolidation."""
        if self._in_dream:
            print("Dream already in progress, skipping...")
            return

        self._in_dream = True

        # 1. Consolidate new rules
        count = self.learner.sleep_cycle()

        # 2. Identify spatial landmarks to protect them from forgetting
        nodes, _ = self.learner.get_situational_graph()

        # 3. Apply biological forgetting (Differential Decay)
        self.memory.decay_rules()

        self.memory.clear_chrono()
        print(f"Dream complete: Consolidated {count} rules/transitions.")

        self._in_dream = False
        self._dream_cooldown = 60

    def export_db(self):
        """Exports the semantic memory (Rules) to a human-readable text file."""
        with open("db_export.txt", "w") as f:
            f.write("--- LEARNED COGNITIVE RULES ---\n")
            rules = self.memory.get_rules()
            for r in rules:
                trans = str(r["next_perception"]) if r["next_perception"] else "None"
                f.write(
                    f"ID: {r['id']} | Action: {r['target_action']} | Success: {r['weight']} | Transition: {trans}...\n"
                )
        print("Knowledge exported to db_export.txt")

    def export_report(self):
        """Generates a comprehensive research-quality report for both bots."""
        import datetime
        from constants import MEMORY_EPISODIC, MEMORY_SEMANTIC, MEMORY_DERIVED

        with open("behavior_report.txt", "w") as f:
            f.write("=" * 60 + "\n")
            f.write("       GENERAL LEARNER 5 - DUAL BOT RESEARCH REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Session Duration: {self.total_steps} steps\n")
            f.write("-" * 60 + "\n")

            for bot_id in [1, 2]:
                memory = self.memory_bot1 if bot_id == 1 else self.memory_bot2
                learner = self.learner1 if bot_id == 1 else self.learner2
                robot = self.robot1 if bot_id == 1 else self.robot2

                rules = memory.get_rules()
                episodic = [r for r in rules if r.get("memory_type") == MEMORY_EPISODIC]
                semantic = [r for r in rules if r.get("memory_type") == MEMORY_SEMANTIC]
                derived = [r for r in rules if r.get("memory_type") == MEMORY_DERIVED]

                concepts = memory.conn.execute(
                    "SELECT id, value FROM conceptual_ids"
                ).fetchall()
                try:
                    derived_cmd_ids = memory.conn.execute(
                        "SELECT DISTINCT command_id FROM rules WHERE command_id IS NOT NULL"
                    ).fetchall()
                    compound_concepts_ids = set(r[0] for r in derived_cmd_ids if r[0])
                except:
                    compound_concepts_ids = set()
                simple_concepts = [
                    c for c in concepts if c[0] not in compound_concepts_ids
                ]
                compound_concepts = [
                    c for c in concepts if c[0] in compound_concepts_ids
                ]

                frames = memory.get_all_frames()
                coord_frames = [fr for fr in frames if fr["relation_type"] == "COORD"]
                opp_frames = [fr for fr in frames if fr["relation_type"] == "OPP"]

                weights = [r["weight"] for r in rules] if rules else [0]
                avg_weight = sum(weights) / len(weights) if weights else 0

                action_counts = {}
                for r in rules:
                    a = r["target_action"]
                    action_counts[a] = action_counts.get(a, 0) + 1
                action_names = {0: "FORWARD", 1: "BACKWARD", 2: "LEFT", 3: "RIGHT"}

                f.write(f"\n{'=' * 60}\n")
                f.write(
                    f"### BOT {bot_id} REPORT {'(ACTIVE)' if self.active_bot == bot_id else ''}\n"
                )
                f.write(f"{'=' * 60}\n")

                f.write("\n### EXECUTIVE SUMMARY\n")
                f.write(f"  Total Steps:         {self.total_steps}\n")
                f.write(f"  Final Score:        {robot.score}\n")
                f.write(f"  Batteries Found:     {robot.score // 10}\n")

                f.write("\n### RULE STATISTICS\n")
                f.write(f"  Total Rules:         {len(rules)}\n")
                f.write(f"  Concrete Rules:     {len(episodic)}\n")
                f.write(f"  Semantic Rules:     {len(semantic)}\n")
                f.write(f"  Derived Rules:      {len(derived)}\n")
                f.write(f"  Avg Weight:         {avg_weight:+.2f}\n")
                f.write(f"  Max Weight:         {max(weights):+.2f}\n")
                f.write(f"  Min Weight:         {min(weights):+.2f}\n")

                f.write("\n### CONCEPTS\n")
                f.write(f"  Total Concepts:     {len(concepts)}\n")
                f.write(f"  Simple Concepts:    {len(simple_concepts)}\n")
                f.write(f"  Compound Concepts:  {len(compound_concepts)}\n")

                f.write("\n### ACTION DISTRIBUTION\n")
                for act, count in sorted(action_counts.items()):
                    name = action_names.get(act, f"ACT_{act}")
                    pct = (count / len(rules) * 100) if rules else 0
                    f.write(f"  {name:10s}: {count:4d} ({pct:5.1f}%)\n")

                f.write("\n### RFT RELATIONSHIPS\n")
                f.write(f"  Total Frames:       {len(frames)}\n")
                f.write(f"  Coordination:       {len(coord_frames)}\n")
                f.write(f"  Opposition:         {len(opp_frames)}\n")

                f.write("\n### HOMEOSTASIS\n")
                f.write(f"  Final Hunger:       {robot.hunger}\n")
                f.write(f"  Final Tiredness:    {robot.tiredness}\n")
                f.write(
                    f"  Bayesian Mode:      {'ENABLED' if learner.bayesian else 'DISABLED'}\n"
                )

                f.write("\n### LEARNING EFFICIENCY\n")
                score_per_step = (
                    robot.score / self.total_steps if self.total_steps > 0 else 0
                )
                rules_per_step = (
                    len(rules) / self.total_steps if self.total_steps > 0 else 0
                )
                f.write(f"  Score/Step:         {score_per_step:.4f}\n")
                f.write(f"  Rules/Step:         {rules_per_step:.4f}\n")
                f.write(
                    f"  Exploration:        {self.total_steps - robot.score} steps\n"
                )

            f.write("\n" + "=" * 60 + "\n")
            f.write("                    END OF REPORT\n")
            f.write("=" * 60 + "\n")

        print("Performance report exported to behavior_report.txt")

    def handle_guide_click(self, gx, gy):
        """
        Processes a grid click during Guide Mode.
        FORCED: Immediately moves the robot and associates text.
        """
        target_action = self.robot.get_action_to(gx, gy)
        if target_action is not None:
            # Immediate forced movement
            self.execute_step(forced_action=target_action)
            # Add visual feedback for the clicked target (briefly)
            self.guide_path = [(gx, gy)]

    def update(self, dt):
        """Continuous simulation updates and UI color state."""
        # 1. Update button visual states
        self.btn_auto.color = LIGHT_ORANGE if self.autonomous else GRAY
        self.btn_comm.color = ORANGE if not self.autonomous else GRAY
        self.btn_guide.color = LIGHT_ORANGE if self.guide_mode else GRAY
        self.btn_bayes.text = "BAYES: ON" if self.learner.bayesian else "BAYES: OFF"
        self.btn_bayes.color = LIGHT_ORANGE if self.learner.bayesian else GRAY

        if self.autonomous:
            self.timer += dt
            if self.timer >= self.step_delay:
                # GL5 Dual-Bot: Both bots take turns in autonomous mode
                # Execute step for both bots each cycle
                self._execute_bot_step(1)
                self._execute_bot_step(2)
                # Note: Display stays on manually selected bot (no auto-switch)
                self.timer = 0

        # Decrement dream cooldown
        if self._dream_cooldown > 0:
            self._dream_cooldown -= 1

        # Homeostasis check: If tired, active robot must sleep (dream phase)
        if self.robot.tiredness >= TIREDNESS_MAX and self._dream_cooldown == 0:
            print(
                "Homeostasis Alert: Robot is exhausted. Triggering automatic Sleep phase..."
            )
            self.dream()
            self.robot.tiredness = 0

    def draw(self):
        """Renders the world and the sidebar HUD."""
        self.screen.fill(BLACK)

        # 1. Render World Grid & Objects
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (30, 35, 45), rect, 1)

                # Visual guide feedback
                if (x, y) in self.guide_path:
                    overlay = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2))
                    overlay.set_alpha(120)
                    overlay.fill(PINK)
                    self.screen.blit(overlay, (x * CELL_SIZE + 1, y * CELL_SIZE + 1))

                val = self.env.grid[y][x]
                if val == WALL_ID:
                    self.screen.blit(self.wall_img, rect)
                elif val == BATTERY_ID:
                    self.screen.blit(self.battery_img, rect)
                elif val == MIRROR_ID:
                    self.screen.blit(self.mirror_img, rect)
                elif val == RESET_BUTTON_ID:
                    self.screen.blit(self.reset_button_img, rect)

        # 2. Render Robot 1 (with rotation based on direction)
        r1 = self.robot1
        r1_rect = pygame.Rect(r1.x * CELL_SIZE, r1.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rot_deg = {DIR_N: 0, DIR_E: -90, DIR_S: 180, DIR_W: 90}
        rotated_r1 = pygame.transform.rotate(self.robot1_img, rot_deg[r1.direction])
        self.screen.blit(rotated_r1, r1_rect)

        # 2b. Render Robot 2 (with rotation based on direction)
        r2 = self.robot2
        r2_rect = pygame.Rect(r2.x * CELL_SIZE, r2.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        rotated_r2 = pygame.transform.rotate(self.robot2_img, rot_deg[r2.direction])
        self.screen.blit(rotated_r2, r2_rect)

        # 3. Sidebar Surface
        pygame.draw.rect(
            self.screen, LIGHT_GRAY, (CANVAS_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        )
        self.btn_auto.draw(self.screen)
        self.btn_comm.draw(self.screen)
        self.txt_box.draw(self.screen)
        self.btn_do.draw(self.screen)
        self.btn_plus.draw(self.screen)
        self.btn_minus.draw(self.screen)
        self.btn_sleep.draw(self.screen)
        self.btn_clear.draw(self.screen)
        self.btn_guide.draw(self.screen)
        self.btn_inform.draw(self.screen)
        self.btn_network.draw(self.screen)
        self.btn_territory.draw(self.screen)
        self.btn_bayes.draw(self.screen)
        self.btn_pov.draw(self.screen)
        self.btn_inferences.draw(self.screen)
        self.btn_new_maze.draw(self.screen)
        self.btn_reset_stagnation.draw(self.screen)

        # GL5 Dual-Bot: Bot selector buttons (Spec 4)
        self.btn_bot1.color = LIGHT_ORANGE if self.active_bot == 1 else GRAY
        self.btn_bot2.color = LIGHT_ORANGE if self.active_bot == 2 else GRAY
        self.btn_bot1.draw(self.screen)
        self.btn_bot2.draw(self.screen)

        # 3. Cognitive Dashboard
        self.draw_reports()

        # 4. POV (3D Raycasting) - Positioned to the right of cognitive performance
        if self.show_pov:
            rep_x = CANVAS_WIDTH + PANEL_WIDTH + 10
            rep_w = REPORT_WIDTH - 30
            pov_rect = pygame.Rect(rep_x + rep_w + 10, 60, POV_WIDTH, POV_HEIGHT)
            graphics.draw_raycast_view(
                self.screen,
                pov_rect,
                self.robot,
                self.env,
                self.learner,
                other_bot=self.robot2 if self.active_bot == 1 else self.robot1,
                active_bot=self.active_bot,
            )

        # 4. HUD Stats & Agenda (with caching - only update when needed)
        if self._cache_rules is None:
            self._cache_rules = self.memory.get_rules()
            self._cache_frames = self.memory.get_all_frames()
            self._cache_graph = self.learner.get_situational_graph()
            self._cache_timestamp = self.total_steps

        rules_count = len(self._cache_rules) if self._cache_rules else 0
        rft_count = len(self._cache_frames) if self._cache_frames else 0
        bayes_status = "ENABLED" if self.learner.bayesian else "DISABLED"
        auto_status = "AUTO" if self.autonomous else "MANUAL"
        guide_status = "GUIDE" if self.guide_mode else "FREE"

        # GL5 Dual-Bot: Include bot ID in stats
        stats = f"Bot{self.active_bot} | Score: {self.robot.score} | Rules: {rules_count} | BAYES: {bayes_status} | {auto_status} | {guide_status} | RFT: {rft_count}"
        stat_surf = self.font.render(stats, True, BLACK)
        self.screen.blit(stat_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 70))

        # VISUOSPATIAL AGENDA (Mental Landmarks)
        agenda_title = self.font.render("VISUOSPATIAL AGENDA:", True, DARK_GRAY)
        self.screen.blit(agenda_title, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 50))

        if self.learner.agenda:
            for i, landmark in enumerate(self.learner.agenda[:5]):
                graphics.draw_mini_perception(
                    self.screen,
                    CANVAS_WIDTH + 10 + i * 35,
                    WINDOW_HEIGHT - 35,
                    30,
                    landmark,
                )

        if self.learner.active_plan:
            plan_text = f"ACTIVE PLAN: [{len(self.learner.active_plan)} steps]"
            plan_surf = self.font.render(plan_text, True, BLUE)
            self.screen.blit(plan_surf, (CANVAS_WIDTH + 10, WINDOW_HEIGHT - 30))

        # 5. Inferences Sub-Window (Below 2D World)
        if self.show_inferences:
            inf_rect = pygame.Rect(10, CANVAS_HEIGHT + 15, CANVAS_WIDTH - 20, 250)
            graphics.draw_inferences_window(
                self.screen, inf_rect, self.learner, self.robot
            )

        pygame.display.flip()

    def draw_reports(self):
        """Renders graphical charts or situational network to the right panel."""
        rep_x = CANVAS_WIDTH + PANEL_WIDTH + 10
        rep_w = REPORT_WIDTH - 30

        if self.show_network:
            rep_rect = pygame.Rect(rep_x, 60, rep_w, 450)
            if self.view_mode == "SITUATIONAL":
                if self._cache_graph:
                    nodes, edges = self._cache_graph
                else:
                    nodes, edges = self.learner.get_situational_graph()
                header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
                    "SITUATIONAL WORLD MAP", True, PURPLE
                )
                self.screen.blit(header_surf, (rep_x, 20))
                graphics.draw_situational_network(
                    self.screen, rep_rect, nodes, edges, self.memory
                )
            else:
                territory = self.memory.get_territory()
                header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
                    "GLOBAL TERRITORY MAP", True, BLUE
                )
                self.screen.blit(header_surf, (rep_x, 20))
                graphics.draw_territory_map(self.screen, rep_rect, territory)
            return

        # Header
        header_surf = pygame.font.SysFont("Arial", 20, bold=True).render(
            "COGNITIVE PERFORMANCE", True, CYAN
        )
        self.screen.blit(header_surf, (rep_x, 20))

        if not self.stats_history:
            msg = self.font.render(
                "Simulating... Waiting for data points.", True, DARK_GRAY
            )
            self.screen.blit(msg, (rep_x, 60))
            return

        # Score Chart (Goals Achieved)
        chart_h = 180
        score_data = [s["score"] for s in self.stats_history]
        score_rect = pygame.Rect(rep_x, 60, rep_w, chart_h)
        graphics.draw_scaled_plot(
            self.screen,
            score_rect,
            score_data,
            GREEN,
            "GOALS ACHIEVED (Score Trend)",
            "S",
        )

        # Knowledge Chart (Rules Learned)
        knowledge_data = [s["rules"] for s in self.stats_history]
        rules_rect = pygame.Rect(rep_x, 60 + chart_h + 30, rep_w, chart_h)
        graphics.draw_scaled_plot(
            self.screen,
            rules_rect,
            knowledge_data,
            PURPLE,
            "KNOWLEDGE BASE (Semantic Rules)",
            "R",
        )

        # Resource Monitor (Memory & CPU)
        mem_data = [s.get("memory_mb", 0) for s in self.stats_history]
        cpu_data = [s.get("cpu_percent", 0) for s in self.stats_history]
        res_rect = pygame.Rect(rep_x, 60 + (chart_h + 30) * 2, rep_w, 100)
        graphics.draw_resource_monitor(self.screen, res_rect, mem_data, cpu_data)

        # Session Insights
        insight_y = 60 + (chart_h + 30) * 3
        insights = [
            f"Learning Efficiency: {knowledge_data[-1] / (self.total_steps + 1):.2f} rules/step",
            f"Average Reward: {score_data[-1] / (self.total_steps + 1):.2f} pts/step",
            f"Total Exploratory Steps: {self.total_steps}",
            f"Memory: {mem_data[-1]:.1f} MB | CPU: {cpu_data[-1]:.1f}%",
        ]
        for i, text in enumerate(insights):
            surf = self.font.render(text, True, (180, 180, 180))
            self.screen.blit(surf, (rep_x, insight_y + i * 20))


if __name__ == "__main__":
    app = GeneralLearnerApp()
    app.run()

# =============================================================================
# OPTIMIZED COGNITIVE NETWORK VISUALIZATION EXPORTER
# =============================================================================

def export_cognitive_network_image(app, bot_id=1, filepath=None):
    """
    GL5.1: Exports an optimized visual graph of the robot's conceptual network.
    Correctly connects RFT frames, Cognitive Productions, and Macros.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import math
        import json
    except ImportError:
        print("ERROR: matplotlib not available for graph export")
        return None

    learner = app.learner1 if bot_id == 1 else app.learner2
    memory = learner.memory

    if filepath is None:
        filepath = f"cognitive_network_bot{bot_id}.png"

    # Collect all knowledge components
    rules = memory.get_rules(limit=500)
    frames = memory.get_all_frames()
    prods = memory.get_cognitive_productions(limit=50)
    heard = memory.get_heard_songs(min_strength=0.1, limit=30)
    
    # Get concept labels for RFT mapping
    concept_labels = {}
    try:
        cur = memory.conn.cursor()
        cur.execute("SELECT id, value FROM conceptual_ids")
        for row in cur.fetchall():
            concept_labels[row["id"]] = row["value"]
    except:
        pass

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(24, 18))
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_title(
        f"Symbolic Cognitive Architecture - Bot {bot_id}\n"
        f"Rules: {len(rules)} | RFT Frames: {len(frames)} | "
        f"CogProds: {len(prods)} | Hearing: {len(heard)}",
        fontsize=18, fontweight="bold", pad=20, color="#2C3E50"
    )

    node_pos = {}
    node_colors = []
    node_labels = {}
    node_sizes = []
    node_types = {} # Store type for edge logic

    # Categories for radial layout
    action_nodes = []
    percept_nodes = []
    self_nodes = []
    prod_nodes = []
    heard_nodes = []
    
    action_names = {0: "LEFT", 1: "RIGHT", 2: "FORWARD", 3: "BACK"}

    # 1. Action Nodes (Center)
    for i in range(4):
        name = action_names[i]
        action_nodes.append(name)
        node_pos[name] = (1.5 * math.cos(i * 3.14/2), 1.5 * math.sin(i * 3.14/2))
        node_colors.append("#FF6B6B") # Red
        node_sizes.append(1200)
        node_labels[name] = name
        node_types[name] = "action"

    # 2. Percept & Self Nodes (Middle Rings)
    processed_percepts = set()
    for rule in rules[:150]:
        perc = rule.get("perception_pattern", "")
        if isinstance(perc, str):
            try: perc = json.loads(perc)
            except: perc = {}
        
        if isinstance(perc, dict):
            for key, val in perc.items():
                node_key = f"{key}:{val}"
                if key.startswith("SELF_"):
                    if key not in self_nodes: self_nodes.append(key)
                elif val != "ANY" and node_key not in processed_percepts:
                    percept_nodes.append(node_key)
                    processed_percepts.add(node_key)

    # Layout Self-Concepts
    for i, node in enumerate(self_nodes[:20]):
        angle = i * (2 * 3.14 / max(len(self_nodes[:20]), 1))
        node_pos[node] = (4.0 * math.cos(angle), 4.0 * math.sin(angle))
        node_colors.append("#FFE66D") # Yellow
        node_sizes.append(700)
        node_labels[node] = node.replace("SELF_", "S_")[:10]
        node_types[node] = "self"

    # Layout Percepts
    for i, node in enumerate(percept_nodes[:40]):
        angle = i * (2 * 3.14 / max(len(percept_nodes[:40]), 1)) + 0.2
        dist = 6.5 + (i % 2) * 0.8 # Jitter for less overlap
        node_pos[node] = (dist * math.cos(angle), dist * math.sin(angle))
        node_colors.append("#4ECDC4") # Teal
        node_sizes.append(400)
        node_labels[node] = node.split(":")[-1][:8]
        node_types[node] = "percept"

    # 3. Cognitive Productions (Outer Ring)
    for i, prod in enumerate(prods[:25]):
        name = prod["name"]
        prod_nodes.append(name)
        angle = i * (2 * 3.14 / max(len(prods[:25]), 1))
        node_pos[name] = (9.5 * math.cos(angle), 9.5 * math.sin(angle))
        node_colors.append("#9B59B6") # Purple
        node_sizes.append(800)
        node_labels[name] = name[:12]
        node_types[name] = "prod"

    # 4. Heard Songs
    for i, h in enumerate(heard[:15]):
        name = f"SONG_{h['heard_song']}"
        heard_nodes.append(name)
        angle = i * (2 * 3.14 / max(len(heard[:15]), 1)) - 0.5
        node_pos[name] = (11.0 * math.cos(angle), 11.0 * math.sin(angle))
        node_colors.append("#3498DB") # Blue
        node_sizes.append(600)
        node_labels[name] = h["heard_song"][:10]
        node_types[name] = "heard"

    # DRAW EDGES
    # a) Rules (Green/Red)
    rule_map = {r["id"]: r for r in rules}
    for rule in rules[:250]:
        action = rule["target_action"]
        weight = rule["weight"]
        perc = rule["perception_pattern"]
        if isinstance(perc, str):
            try: perc = json.loads(perc)
            except: perc = {}
        
        target = action_names.get(action)
        if target and isinstance(perc, dict):
            for key, val in perc.items():
                source = f"{key}:{val}" if not key.startswith("SELF_") else key
                if source in node_pos and target in node_pos:
                    style = "-" if rule["is_composite"] == 0 else "--"
                    alpha = min(0.8, 0.2 + abs(weight)/10.0)
                    ax.annotate("", xy=node_pos[target], xytext=node_pos[source],
                                arrowprops=dict(arrowstyle="->", color="#1B5E20" if weight > 0 else "#B71C1C", 
                                              lw=1.5 + abs(weight)/8, alpha=alpha, linestyle=style))

    # b) RFT Frames (Darker and thicker)
    for frame in frames[:30]:
        c1 = concept_labels.get(frame["concept_a"])
        c2 = concept_labels.get(frame["concept_b"])
        rel = frame["relation_type"]
        if c1 in node_pos and c2 in node_pos:
            color = "#2E7D32" if rel == "COORD" else "#C62828"
            style = ":" if rel == "OPP" else "-."
            ax.plot([node_pos[c1][0], node_pos[c2][0]], [node_pos[c1][1], node_pos[c2][1]], 
                    color=color, linestyle=style, alpha=min(1.0, frame["strength"] + 0.2), lw=2.5)

    # c) Cognitive Production Component Connections (Higher contrast)
    for prod in prods[:15]:
        p_name = prod["name"]
        if p_name in node_pos and prod["component_rules"]:
            try:
                comp_ids = json.loads(prod["component_rules"])
                for rid in comp_ids:
                    if rid in rule_map:
                        r = rule_map[rid]
                        a_target = action_names.get(r["target_action"])
                        if a_target in node_pos:
                            ax.plot([node_pos[p_name][0], node_pos[a_target][0]], 
                                    [node_pos[p_name][1], node_pos[a_target][1]], 
                                    color="#6A1B9A", alpha=0.4, lw=1.5)
            except: pass

    # DRAW NODES
    for name, pos in node_pos.items():
        idx = list(node_pos.keys()).index(name)
        color = node_colors[idx]
        size = node_sizes[idx]
        ax.scatter(pos[0], pos[1], s=size, color=color, edgecolors="white", linewidth=1.5, zorder=5)
        ax.text(pos[0], pos[1], node_labels.get(name, ""), ha="center", va="center", 
                fontsize=7, fontweight="bold", color="#2C3E50" if color == "#FFE66D" else "white", zorder=6)

    # LEGEND
    legend_elements = [
        mpatches.Patch(color="#FF6B6B", label="Actions (Motor)"),
        mpatches.Patch(color="#4ECDC4", label="Percepts (Sensory)"),
        mpatches.Patch(color="#FFE66D", label="Self-Concepts (Identity)"),
        mpatches.Patch(color="#9B59B6", label="CogProductions (Abstraction)"),
        mpatches.Patch(color="#3498DB", label="Hearing (Social)"),
        plt.Line2D([0], [0], color="#2ECC71", label="COORD Frame / Pos Rule"),
        plt.Line2D([0], [0], color="#E74C3C", label="OPP Frame / Neg Rule"),
        plt.Line2D([0], [0], color="gray", linestyle="--", label="Macro (Composite)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", frameon=True, shadow=True)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
    plt.close()

    print(f"Expert Cognitive Network exported to: {filepath}")
    return filepath


def export_learning_trajectory_csv(app, bot_id=1, filepath=None):
    """
    Exports learning trajectory data to CSV for analysis.
    """
    learner = app.learner1 if bot_id == 1 else app.learner2
    memory = learner.memory

    if filepath is None:
        filepath = f"learning_trajectory_bot{bot_id}.csv"

    import csv

    rules = memory.get_rules(limit=10000)
    
    rows = []
    for i, rule in enumerate(rules):
        rows.append({
            "bot_id": bot_id,
            "rule_id": rule.get("id", i),
            "perception": str(rule.get("perception_pattern", ""))[:100],
            "action": rule.get("target_action", -1),
            "weight": rule.get("weight", 0),
            "memory_type": rule.get("memory_type", 0),
            "is_composite": rule.get("is_composite", 0)
        })

    with open(filepath, "w", newline="") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    print(f"Learning trajectory exported to: {filepath}")
    return filepath
