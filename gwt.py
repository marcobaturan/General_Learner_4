"""
################################################################################
#                                                                              #
#       _____  _      ____  ____          _                                    #
#      / ____|| |    / __ \|  _ \   /\   | |                                   #
#     | |  __ | |   | |  | | |_) | /  \  | |                                   #
#     | | |_ || |   | |  | |  _  / / /\ \ | |                                  #
#     | |__| || |___| |__| | |_) / ____ \| |____                               #
#      \_____||______\____/|____/_/    \_\______|                              #
#                                                                              #
#      __          ______  _____  _  __ _____  _____        _____  ______      #
#      \ \        / / __ \|  __ \| |/ // ____||  __ \ /\   / ____||  ____|     #
#       \ \  /\  / / |  | | |__) | ' /| (___  | |__) /  \ | |     | |__        #
#        \ \/  \/ /| |  | |  _  /|  <  \___ \ |  ___/ /\ \| |     |  __|       #
#         \  /\  / | |__| | | \ \| . \ ____) || |  / ____ \ |____ | |____      #
#          \/  \/   \____/|_|  \_\_|\_\_____/ |_| /_/    \_\_____||______|     #
#                                                                              #
################################################################################

GLOBAL WORKSPACE THEORY (GWT) MODULE
====================================

This module implements Bernard Baars' (1988) Global Workspace Theory, 
providing a central "Theatre of Consciousness" for the GL5 agent.

SCIENTIFIC FOUNDATIONS:
-----------------------
1. THE THEATRE METAPHOR:
   Based on Baars (1997). The architecture consists of a stage (Working 
   Memory), a spotlight (Attention), and an audience (Specialized Modules).
   Ref: Baars, B. J. (1997). In the Theatre of Consciousness.

2. GLOBAL BROADCASTING:
   Consciousness is the process of broadcasting information from a central 
   workspace to a distributed set of specialized unconscious processors.

3. COMPETITION FOR ACCESS:
   Multiple specialized modules (Vision, Spatial, Motor) compete for 
   access to the limited-capacity workspace. Only the most salient 
   information wins the "Spotlight".

4. LONG-RANGE PERCEPTION:
   The GL5.1 Vision module implements an enhanced 'Global' view of the 
   maze, allowing for high-level spatial strategy.

Author: Marco
"""

import json
import math
from collections import defaultdict
from constants import (
    GRID_W,
    GRID_H,
    DIR_N,
    DIR_E,
    DIR_S,
    DIR_W,
    WALL_ID,
    BATTERY_ID,
    EMPTY_ID,
    MIRROR_ID,
    RESET_BUTTON_ID,
)


class GlobalWorkspace:
    """
    ############################################################################
    #   _____ _      ____  ____          _                                     #
    #  / ____| |    / __ \|  _ \   /\   | |                                    #
    # | |  __| |   | |  | | |_) | /  \  | |                                    #
    # | | |_ | |   | |  | |  _  / / /\ \ | |                                   #
    # | |__| | |___| |__| | |_) / ____ \| |____                                #
    #  \_____|______|____/|____/_/    \_\______|                               #
    ############################################################################

    The central workspace where competing modules broadcast their content.
    """

    def __init__(self):
        self.conscious_content = None
        self.conscious_context = None
        self.attention_strength = 1.0
        self.attention_decay = 0.1
        self.episode_history = []
        self.max_history = 100
        self.competition_threshold = 0.3
        self.winner_boost = 1.5
        
        # GL5.1 Optimized: Inhibition of Return (IOR)
        # Prevents getting stuck on the same stimulus
        self.last_winners = [] # Queue of recent winners
        self.ior_penalty = 0.4 # Penalty for recent winners

    def add_module(self, module):
        """
        Register a specialized module with the workspace.

        Modules are the "audience" in the theatre metaphor - they operate
        unconsciously in parallel and compete for conscious access.

        Args:
            module: A GWTModule instance (Vision, Spatial, or Motor)

        The module will receive broadcasts and be able to bid for
        consciousness.
        """
        if not hasattr(self, "modules"):
            self.modules = []
        self.modules.append(module)
        # Give the module a reference to the workspace
        module.workspace = self

    def receive_bid(self, module, content, context, intensity):
        """
        Receive a bid from a module for workspace access.

        Each module operates unconsciously and can bid to have its
        processing become conscious. Bids are collected during the
        cognitive cycle and resolved in run_competition().

        THE BIDDING PROCESS (from Baars, 1997):
        ----------------------------------------
        1. Each module computes a "bid" based on:
           - Its current salience (importance)
           - Urgency of information
           - Recency of related content
           - Current goals/needs

        2. Bids are collected during the cycle

        3. Competition selects the winner

        4. Winner is broadcast to all modules

        Args:
            module: The bidding module (Vision, Spatial, or Motor)
            content: What the module wants to broadcast (its "proposition")
            context: Additional context for interpreting the content
            intensity: Urgency/importance of the bid (0-1 normalized)

        Returns:
            bool: True if this bid wins immediately (rare), usually False

        The bid intensity represents how "consciously accessible" the module
        wants its content to be. High intensity = urgent, novel, or
        goal-relevant information.
        """
        if not hasattr(self, "bids"):
            self.bids = []

        self.bids.append(
            {
                "module": module,
                "content": content,
                "context": context,
                "intensity": intensity,
                "id": id(module),
            }
        )
        return False

    def run_competition(self):
        """
        Run the competition with IOR and Dynamic Spotlight mechanisms.
        """
        if not hasattr(self, "bids") or not self.bids:
            return None

        # Dynamic Threshold: Higher urgency -> narrower focus
        current_urgency = max([b["intensity"] for b in self.bids])
        dynamic_threshold = self.competition_threshold
        if current_urgency > 0.8:
            dynamic_threshold += 0.2 # Raise bar for distractions

        best_bid = None
        best_score = -1

        for bid in self.bids:
            score = bid["intensity"] * bid["module"].salience

            # Apply IOR (Inhibition of Return)
            if bid["module"].name in self.last_winners:
                score *= (1.0 - self.ior_penalty)

            # Apply recency bonus
            if self.conscious_content and self._is_similar(bid["content"], self.conscious_content):
                score *= self.winner_boost

            if score > best_score:
                best_score = score
                best_bid = bid

        self.bids = []

        if best_bid and best_score > dynamic_threshold:
            self.conscious_content = best_bid["content"]
            self.conscious_context = best_bid["context"]

            # Update IOR queue
            self.last_winners.append(best_bid["module"].name)
            if len(self.last_winners) > 2: self.last_winners.pop(0)

            self.episode_history.append({
                "content": self.conscious_content,
                "context": self.conscious_context,
                "winner": best_bid["module"].name,
                "intensity": best_score,
            })

            if len(self.episode_history) > self.max_history:
                self.episode_history.pop(0)

            self._broadcast(best_bid)
            return best_bid

        return None

    def _is_similar(self, content1, content2):
        """
        Check if two contents are similar for recency boost.

        Similarity allows content that is related to current consciousness
        to have a better chance of becoming conscious (associative
        spread of attention).

        Args:
            content1: First content to compare
            content2: Second content to compare

        Returns:
            bool: True if contents are similar enough
        """
        if isinstance(content1, str) and isinstance(content2, str):
            return content1 == content2
        if isinstance(content1, dict) and isinstance(content2, dict):
            return content1.get("perception") == content2.get("perception")
        return False

    def _broadcast(self, bid):
        """
        Broadcast winning content to all modules.

        This is the KEY INSIGHT of Global Workspace Theory:

        "Unconscious modules can only interact when content becomes
        conscious and is broadcast to the entire system."

        When content wins the competition, it enters the "spotlight"
        and is visible to all modules simultaneously. This enables:
        - Integration of information from different sources
        - Coordination of processing across modules
        - Creation of coherent conscious experience

        Example: When the VISION module wins, its perception of a
        battery is broadcast. The MOTOR module sees it and can plan
        action. The SPATIAL module sees it and updates the map.

        BIOLOGICAL CORRELATE:
        ----------------------
        Broadcasting may correspond to neural synchronization (gamma
        oscillations ~40Hz) that temporarily links distributed
        cortical regions.

        Reference: Singer, W. (1999). Neuronal synchrony: A versatile
        code for the definition of relations? Neuron, 24(1), 49-65.

        Args:
            bid: The winning bid containing content, context, intensity
        """
        for module in self.modules:
            if module != bid["module"]:
                module.receive_broadcast(
                    bid["content"], bid["context"], bid["intensity"]
                )

    def get_conscious_state(self):
        """
        Return current conscious state for display/debugging.

        Returns:
            dict: Current conscious content, context, and recent history

        This method is primarily for debugging and visualization. It
        shows what the system is currently conscious of.
        """
        return {
            "content": self.conscious_content,
            "context": self.conscious_context,
            "recent_episodes": self.episode_history[-5:]
            if self.episode_history
            else [],
        }

class GWTModule:
    """
    ============================================================================
    GWT MODULE - Specialized Unconscious Processor
    ============================================================================

    Base class for all modules in the GWT architecture.

    In Baars' Global Workspace Theory, the brain contains many specialized
    processors (modules) that operate unconsciously in parallel. These modules
    compete for access to a limited-capacity workspace where their processing
    can become conscious and be broadcast to all other modules.

    MODULE CHARACTERISTICS:
    ----------------------
    1. PARALLEL PROCESSING: Modules run simultaneously, each specializing
       in a specific type of processing (vision, motor, spatial, etc.)

    2. UNCONSCIOUS OPERATION: Modules process information without
       conscious awareness - they are "zombies" in the theatre audience

    3. COMPETITION FOR ACCESS: When a module has important information,
       it bids for workspace access. The most urgent/intense bid wins.

    4. BROADCAST RECEPTION: Modules can receive broadcasts from the
       workspace, allowing them to respond to conscious content.

    5. CONTEXT-SENSITIVE: Module behavior is modulated by recent
       broadcasts (context from other modules).

    BIOLOGICAL CORRELATES:
    ----------------------
    - Visual cortex for VisionModule
    - Hippocampal formation for SpatialModule
    - Basal ganglia for MotorModule
    - Prefrontal cortex for integration

    Attributes:
        name: Module identifier (e.g., "VISION", "MOTOR")
        salience: Base importance weight for bids (0-1)
        workspace: Reference to GlobalWorkspace instance
        recent_broadcasts: Last 10 broadcasts received
        bid_cooldown: Cycles to wait before bidding again
    """

    def __init__(self, name, salience=1.0):
        """
        Initialize a GWT module.

        Args:
            name: Module identifier (e.g., "VISION")
            salience: Base importance weight (1.0 = normal, higher = more important)
        """
        self.name = name
        self.salience = salience  # How important is this module (baseline)
        self.workspace = None
        self.recent_broadcasts = []
        self.bid_cooldown = 0

    def process(self, data):
        """
        Process input data and generate bids.

        This is the main entry point for module processing. Subclasses
        implement specific processing logic (e.g., scanning vision for
        objects, computing path plans, etc.)

        Args:
            data: Module-specific input data

        Returns:
            Any: Module-specific processing result

        Note: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def compute_bid(self, data):
        """
        Compute bid intensity for current data.

        Bid intensity represents how urgently the module wants its
        processing to become conscious. Factors include:
        - Novelty of information
        - Goal relevance
        - Urgency (threat/opportunity)
        - Confidence (how sure is the module)

        Args:
            data: Current module state/data

        Returns:
            tuple: (bid_intensity, content, context)
                - bid_intensity: How urgent (0-1, >0.3 wins)
                - content: What to broadcast
                - context: Additional context for interpretation
        """
        raise NotImplementedError

    def receive_broadcast(self, content, context, intensity):
        """
        Receive broadcast from workspace.

        When content wins the workspace competition, it is broadcast
        to ALL modules. This allows unconscious modules to respond
        to conscious content.

        Example: When VISION broadcasts "BATTERY_NEAR", MOTOR can
        respond by planning approach actions.

        Args:
            content: The broadcasted content (module-specific dict)
            context: Additional context from broadcasting module
            intensity: Broadcast strength (from competition score)
        """
        self.recent_broadcasts.append(
            {"content": content, "context": context, "intensity": intensity}
        )
        # Limit history to prevent memory overflow
        if len(self.recent_broadcasts) > 10:
            self.recent_broadcasts.pop(0)

    def bid(self, content, context, intensity):
        """
        Submit bid to workspace.

        The module offers its current processing result for conscious
        access. The workspace will include this bid in the competition.

        Args:
            content: What the module wants to broadcast
            context: Additional context for interpretation
            intensity: Urgency of the bid (0-1)

        Returns:
            bool: True if bid was accepted (queued for competition)
        """
        if self.bid_cooldown > 0:
            self.bid_cooldown -= 1
            return False
        if self.workspace:
            return self.workspace.receive_bid(self, content, context, intensity)
        return False
        if self.workspace:
            return self.workspace.receive_bid(self, content, context, intensity)
        return False


class VisionModule(GWTModule):
    """
    ============================================================================
    VISION MODULE - Long-Range Perceptual Processor
    ============================================================================

    The vision module processes what the robot perceives in its environment.

    KEY INNOVATION: LONG-RANGE PERCEPTION
    ---------------------------------------
    Unlike the original GL5 which only saw a 3x3 grid (1 cell in each
    direction), this module sees the ENTIRE MAZE. This is a crucial
    enhancement that enables:

    1. SPATIAL MAPPING: The robot can build a complete cognitive map
       of the maze topology.

    2. EFFICIENT NAVIGATION: No longer needs to "bump into walls" to
       learn the layout - it can see walls from afar.

    3. PLANNING: Can plan routes to goals before executing them.

    4. INFERENCE: Perceives patterns (corridors, rooms) that would be
       invisible at close range.

    BIOLOGICAL CORRELATE:
    ---------------------
    This is analogous to the "foveal vs. peripheral vision" distinction:
    - Close range = foveal (detailed, but narrow)
    - Far range = peripheral (broader spatial awareness)

    The robot's vision combines both - seeing everything but with
    full maze topology.

    THEORY REFERENCES:
    ------------------
    - Gibson, J.J. (1979). The Ecological Approach to Visual Perception.
      The concept of "affordances" - what the environment offers.

    - O'Keefe, J. & Nadel, L. (1978). The Hippocampus as a Cognitive Map.
      How spatial perception enables navigation.

    Attributes:
        env: Environment (maze grid)
        robot: Robot instance
        max_range: Maximum vision distance (default: entire maze)
        last_perception: Most recent maze scan result
        attended_objects: Objects that were previously attended (for novelty)
    """

    def __init__(self, env, robot, max_range=None):
        """
        Initialize the Vision Module.

        Args:
            env: Environment instance containing the maze grid
            robot: Robot instance for position/direction
            max_range: Maximum vision distance (None = full maze)
        """
        super().__init__("VISION", salience=1.0)
        self.env = env
        self.robot = robot
        # Full maze visibility - this is the KEY DIFFERENCE from GL5
        # In GL5, max_range was 1 (3x3 grid). Here it's the full maze.
        self.max_range = max_range or max(GRID_W, GRID_H)
        self.last_perception = None
        # Track attended objects for novelty detection
        self.attended_objects = set()

    def process(self, other_bot=None):
        """
        Process visual perception of the entire maze.

        This is the main entry point - scans the full maze and submits
        a bid for consciousness based on what was seen.

        Args:
            other_bot: Optional other robot for detection

        Returns:
            dict: Complete maze perception with all objects and distances
        """
        perception = self._scan_maze(other_bot)
        self.last_perception = perception

        # Compute bid based on perception content
        bid_intensity, content, context = self.compute_bid(perception)

        # Submit bid to workspace
        self.bid(content, context, bid_intensity)

        return perception

    def _scan_maze(self, other_bot=None):
        """
        Perform a comprehensive scan of the entire maze.

        ALGORITHM:
        ---------
        For each of the 4 cardinal directions:
        1. Cast a "ray" from the robot's position
        2. Step outward until hitting a wall or boundary
        3. Record all cells seen, with their types

        This is similar to raycasting in video games (like Wolfenstein 3D)
        but simplified for a 2D grid.

        MAZE VIEW STRUCTURE:
        --------------------
        {
            'walls': [(x1,y1), (x2,y2), ...],    # Wall positions
            'batteries': [...],                    # Battery positions
            'mirrors': [...],                     # Mirror positions
            'other_bot': (x,y) or None,          # Other robot position
            'distances': {(x,y): dist, ...},     # Distance map
            'robot_pos': (x,y),                  # Current position
            'explored': set(),                    # All seen cells
            'nearest_battery': (x,y),            # Closest battery
            'nearest_battery_dist': int,         # Distance to it
        }

        Args:
            other_bot: Other robot to detect

        Returns:
            dict: Complete maze view
        """
        x, y = self.robot.x, self.robot.y
        direction = self.robot.direction

        maze_view = {
            "walls": [],
            "batteries": [],
            "empty": [],
            "mirrors": [],
            "other_bot": None,
            "distances": {},
            "robot_pos": (x, y),
            "robot_dir": direction,
            "explored": set(),
            "visible_cells": [],
        }

        # Scan in 4 cardinal directions
        directions = [(0, -1, "N"), (1, 0, "E"), (0, 1, "S"), (-1, 0, "W")]

        for dx, dy, dir_name in directions:
            # Ray casting: step outward until wall or boundary
            for dist in range(1, self.max_range + 1):
                tx, ty = x + dx * dist, y + dy * dist

                # Out of bounds = stop
                if not (0 <= tx < GRID_W and 0 <= ty < GRID_H):
                    break

                cell = self.env.get_at(tx, ty)
                maze_view["visible_cells"].append((tx, ty))
                maze_view["explored"].add((tx, ty))
                maze_view["distances"][(tx, ty)] = dist

                # Walls block vision (can't see past them)
                if cell == WALL_ID:
                    maze_view["walls"].append((tx, ty))
                    break
                elif cell == BATTERY_ID:
                    maze_view["batteries"].append((tx, ty))
                elif cell == MIRROR_ID:
                    maze_view["mirrors"].append((tx, ty))
                elif cell == RESET_BUTTON_ID:
                    maze_view["reset_button"] = (tx, ty)

        # Check for other bot visibility
        if other_bot:
            dist = abs(x - other_bot.x) + abs(y - other_bot.y)
            if dist <= self.max_range:
                if self._has_line_of_sight(x, y, other_bot.x, other_bot.y):
                    maze_view["other_bot"] = (other_bot.x, other_bot.y)

        # Find nearest battery (for goal-directed behavior)
        if maze_view["batteries"]:
            nearest = min(
                maze_view["batteries"], key=lambda p: abs(p[0] - x) + abs(p[1] - y)
            )
            maze_view["nearest_battery"] = nearest
            maze_view["nearest_battery_dist"] = abs(nearest[0] - x) + abs(
                nearest[1] - y
            )

        return maze_view

    def _has_line_of_sight(self, x1, y1, x2, y2):
        """
        Check if there's a clear line of sight between two points.

        Uses Bresenham's line algorithm to trace the path between
        points and check for walls.

        This is used to determine if the robot can "see" the other
        robot (important for social learning and avoidance).

        Args:
            x1, y1: Starting position
            x2, y2: Target position

        Returns:
            bool: True if line of sight is clear
        """
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            if x1 == x2 and y1 == y2:
                return True
            if self.env.get_at(x1, y1) == WALL_ID:
                return False

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return True

    def compute_bid(self, perception):
        """
        Compute bid intensity based on what was seen.

        BID INTENSITY FACTORS:
        ---------------------
        1. BATTERY PROXIMITY: Closer batteries = higher urgency
           - Distance 1-2: +2.0 intensity
           - Distance 3-5: +1.5 intensity
           - Distance 6+: +1.0 intensity

        2. OTHER BOT: Social stimuli are highly salient
           - +1.0 intensity when other bot visible

        3. NOVELTY: Unexplored areas attract attention
           - +0.5 intensity when >5 new cells seen

        4. RECENCY: First scan has priority
           - ×1.5 boost if no recent broadcasts

        THEORY REFERENCE:
        -----------------
        This follows the "salience map" model from Itti & Baldi (2009)
        "Bayesian Surprise Attracts Human Attention" - surprising
        stimuli (novel, goal-relevant) are more likely to be attended.

        Args:
            perception: Maze scan result

        Returns:
            tuple: (bid_intensity, content, context)
        """
        intensity = 0.5  # Base intensity
        content = None
        context = {}

        # Battery proximity: primary goal
        if "nearest_battery_dist" in perception:
            dist = perception["nearest_battery_dist"]
            # Closer = more urgent (inversely proportional)
            intensity += max(0, 2.0 - dist * 0.3)

            content = {
                "type": "BATTERY_GOAL",
                "target": perception["nearest_battery"],
                "distance": dist,
            }
            context["goal"] = "seek_battery"

        # Other bot: social salience
        if perception.get("other_bot"):
            intensity += 1.0
            content = {"type": "OTHER_AGENT", "position": perception["other_bot"]}
            context["social"] = True

        # Novelty: unexplored areas
        unexplored = len(
            [c for c in perception["visible_cells"] if c not in self.attended_objects]
        )
        if unexplored > 5:
            intensity += 0.5
            context["exploration"] = unexplored

        # First scan priority
        if not self.recent_broadcasts:
            intensity *= 1.5

        return intensity, content, context


class SpatialModule(GWTModule):
    """
    ============================================================================
    SPATIAL MODULE - Cognitive Map and Episodic Memory
    ============================================================================

    The spatial module maintains the robot's cognitive map and spatial awareness.

    BIOLOGICAL CORRELATE:
    ---------------------
    This module implements the function of the hippocampal formation:

    1. PLACE CELLS (O'Keefe, 1971): Fire when the animal is in a specific
       location. Our cognitive_map models these - each position has a
       "visit count" like place cell firing rate.

    2. GRID CELLS (Moser et al., 2008): Provide metric spatial information
       through hexagonal firing patterns. Our distance calculations model this.

    3. EPISODIC MEMORY: Records "what happened where." Our position history
       enables reconstruction of past experiences.

    4. COGNITIVE MAP (Tolman, 1930): Internal representation of environment
       topology for flexible navigation. Our landmarks map this.

    THEORY REFERENCES:
    ------------------
    - O'Keefe, J. & Nadel, L. (1978). The Hippocampus as a Cognitive Map.
      The foundational theory of hippocampal spatial representation.

    - Moser, E.I. et al. (2008). Place cells, grid cells, and the brain's
      spatial representation system. Nature Neuroscience.

    - Tolman, E.C. (1930). Cognitive maps in rats and men. Psychological Review.
      The original concept of mental maps for navigation.

    WHY LONG-RANGE VISION MATTERS:
    ------------------------------
    With GL5's 3x3 vision, the robot learned the maze by "bumping into walls."
    With full maze vision, the spatial module can:
    - See walls before touching them
    - Build complete topology quickly
    - Plan routes without trial-and-error
    - Recognize spatial patterns (corridors, rooms)

    Attributes:
        memory: Memory subsystem for persistence
        cognitive_map: Position -> visit count (like place cell activity)
        landmarks: Position -> landmark type (WALL, BATTERY, etc.)
        last_position: Previous position (for movement tracking)
    """

    def __init__(self, memory):
        """
        Initialize the Spatial Module.

        Args:
            memory: Memory subsystem for storing spatial information
        """
        super().__init__("SPATIAL", salience=0.8)
        self.memory = memory
        self.cognitive_map = {}  # Position -> visited count
        self.landmarks = {}  # Position -> landmark type
        self.last_position = None

    def process(self, maze_view, robot_pos):
        """
        Process spatial information from vision and update cognitive map.

        This is called each cycle with the vision module's output.
        It integrates the maze view into the cognitive map.

        INTEGRATION PROCESS:
        -------------------
        1. Update position history (like place cell firing)
        2. Extract landmarks from vision
        3. Compute spatial context (coverage, visits)
        4. Submit bid for attention if needed

        Args:
            maze_view: Full maze perception from VisionModule
            robot_pos: Current (x, y) position

        Returns:
            dict: Spatial context with map statistics
        """
        # Update position history (incremental learning)
        if self.last_position != robot_pos:
            # Each visit increases "firing rate"
            self.cognitive_map[robot_pos] = self.cognitive_map.get(robot_pos, 0) + 1
            self.last_position = robot_pos

        # Extract landmarks from vision
        for wall_pos in maze_view.get("walls", []):
            self.landmarks[wall_pos] = "WALL"
        for batt_pos in maze_view.get("batteries", []):
            self.landmarks[batt_pos] = "BATTERY"

        # Compute spatial context for bidding
        context = {
            "position": robot_pos,
            "map_coverage": len(self.cognitive_map) / (GRID_W * GRID_H),
            "landmarks": len(self.landmarks),
            "visits": self.cognitive_map.get(robot_pos, 0),
        }

        # Compute and submit bid
        bid_intensity, content, _ = self.compute_bid(context)
        self.bid(content, context, bid_intensity)

        return context

    def compute_bid(self, context):
        """
        Compute bid based on spatial state.

        BID INTENSITY FACTORS:
        ----------------------
        1. EXPLORATION NEED: Low map coverage means unexplored areas
           - Coverage < 50%: +0.5 intensity

        2. STUCK DETECTION: Repeated visits to same cell
           - Visits > 3: +0.8 intensity (need to escape)

        3. LANDMARK DISCOVERY: New landmark is noteworthy
           - New landmark seen: +0.3 intensity

        THEORY REFERENCE:
        ------------------
        The "coverage" metric relates to the hippocampus's role in
        novelty detection. Novel environments activate the hippocampus
        more strongly (Kumaran & Maguire, 2006).

        Args:
            context: Spatial context from process()

        Returns:
            tuple: (bid_intensity, content, context)
        """
        intensity = 0.4  # Base salience

        # Exploration needed: map is incomplete
        if context["map_coverage"] < 0.5:
            intensity += 0.5
            content = {"type": "EXPLORATION_NEEDED"}

        # Stuck detection: been here too many times
        elif context["visits"] > 3:
            intensity += 0.8
            content = {"type": "STUCK_DETECTED"}

        else:
            content = {"type": "SPATIAL_UPDATE"}

        return intensity, content, context

    def get_path_to_goal(self, goal_pos, robot_pos):
        """
        Compute shortest path to goal using BFS.

        Uses the cognitive map and landmarks to find a path that
        avoids walls. This is a simplified version of how the
        hippocampus supports navigation.

        ALGORITHM: BREADTH-FIRST SEARCH
        --------------------------------
        BFS guarantees the shortest path in an unweighted grid:
        1. Start from robot position
        2. Explore neighbors level by level
        3. First time reaching goal = shortest path

        COMPLEXITY: O(V + E) where V = cells, E = edges

        BIOLOGICAL CORRELATE:
        ---------------------
        This models the hippocampus's "goal-directed navigation" function.
        The entorhinal cortex (grid cells) provides the metric
        information; the hippocampus provides the topological map.

        Reference: Spiers, H.J. & Barry, C. (2015). Neural activity
        in the hippocampus during navigation. Handbook of Neurology.

        Args:
            goal_pos: Target (x, y) position
            robot_pos: Starting (x, y) position

        Returns:
            list: Path as list of (x, y) coordinates, empty if no path
        """
        from collections import deque

        if goal_pos == robot_pos:
            return []

        visited = {robot_pos}
        queue = deque([(robot_pos, [])])

        while queue:
            pos, path = queue.popleft()

            if pos == goal_pos:
                return path

            x, y = pos
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                # Bounds check
                if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
                    continue

                if (nx, ny) in visited:
                    continue

                # Wall check (using landmarks from vision)
                cell_type = self.landmarks.get((nx, ny))
                if cell_type == "WALL":
                    continue

                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

        return []  # No path found (shouldn't happen in valid maze)


class MotorModule(GWTModule):
    """
    ============================================================================
    MOTOR MODULE - Action Selection and Procedural Memory
    ============================================================================

    The motor module manages action selection and execution, based on the
    basal ganglia's role in action selection.

    BIOLOGICAL CORRELATE:
    ---------------------
    The basal ganglia is often called the "action selection organ" of the
    brain. It receives inputs from all cortical areas and selects which
    actions to execute through a competitive process.

    KEY STRUCTURES:
    ---------------
    1. STRIATUM (Input): Receives from cortex, contains D1 (Go) and
       D2 (NoGo) neurons for action facilitation/inhibition

    2. GLOBUS PALLIDUS (Output): Inhibits thalamus, preventing unwanted
       actions

    3. SUBSTANTIA NIGRA: Provides dopamine signals for learning

    MOTOR MODULE FUNCTIONS:
    -----------------------
    1. ACTION CANDIDATE GENERATION: Proposes possible actions based on
       current conscious content (goal, context)

    2. ACTION SELECTION: Competes with other modules for attention
       when action is uncertain

    3. PROCEDURAL MEMORY: Stores learned action sequences (motor programs)

    4. MOTOR CHUNKING: Groups actions into hierarchical sequences

    THEORY REFERENCES:
    -----------------
    - Graybiel, A.M. (2008). Habits, rituals, and the evaluative brain.

    - Mink, J.W. (1996). The basal ganglia: focused selection and
      inhibition of competing motor programs. Progress in Neurobiology.

    MOTOR CHUNKING (Graybiel, 1998):
    --------------------------------
    The basal ganglia chunk motor sequences:
    - Individual actions → micro-chunks (~3-4 actions)
    - Micro-chunks → macro-chunks (habits)
    """

    def __init__(self):
        super().__init__("MOTOR", salience=1.2)
        self.pending_actions = []
        self.action_confidence = 0.5

    def process(self, conscious_content, conscious_context, action_options):
        """
        Process action options and compete for attention if needed.
        """
        context = {
            "conscious_type": conscious_content.get("type")
            if isinstance(conscious_content, dict)
            else None,
            "options": action_options,
            "confidence": self.action_confidence,
        }

        if self.action_confidence < 0.6:
            intensity = (0.6 - self.action_confidence) * 2
            self.bid({"type": "ACTION_UNCERTAINTY"}, context, intensity)

        return context

    def compute_bid(self, context):
        """Compute motor bid based on action confidence."""
        intensity = 0.3

        if context.get("confidence", 1.0) < 0.5:
            intensity += 0.7

        return intensity, {"type": "MOTOR_PLAN"}, context


class GWTIntegrator:
    """
    ============================================================================
    GWT INTEGRATOR - Main Cognitive Architecture Orchestrator
    ============================================================================

    The GWTIntegrator orchestrates all modules and runs the complete cognitive
    cycle based on Baars' Global Workspace Theory.

    COGNITIVE CYCLE:
    ----------------
    1. PARALLEL UNCONSCIOUS PROCESSING
       - Vision scans the maze
       - Spatial updates the cognitive map
       - Motor processes current goals
       - Each module generates bids

    2. COMPETITION
       - All bids are collected
       - Highest-intensity bid wins
       - Winner enters consciousness

    3. BROADCAST
       - Winner content is broadcast to all modules
       - Modules can respond to conscious content

    4. UPDATE
       - Modules update based on broadcast
       - Cycle completes

    INTEGRATION WITH GL5.1:
    ----------------------
    The GWT Integrator connects to:
    - Learner (cognitive engine)
    - Memory (storage)
    - Environment (maze)
    - Robot (agent)
    """

    def __init__(self, env, robot, memory):
        self.workspace = GlobalWorkspace()

        # Create modules
        self.vision = VisionModule(env, robot)
        self.spatial = SpatialModule(memory)
        self.motor = MotorModule()

        # Register with workspace
        self.workspace.add_module(self.vision)
        self.workspace.add_module(self.spatial)
        self.workspace.add_module(self.motor)

        self.env = env
        self.robot = robot
        self.memory = memory

        # Cycle tracking
        self.cycle_count = 0

    def run_cycle(self, other_bot=None, action_options=None):
        """
        Run one complete GWT cognitive cycle.

        Returns:
            dict: Result of the cycle including conscious content
        """
        self.cycle_count += 1

        # Phase 1: Parallel unconscious processing
        maze_view = self.vision.process(other_bot)
        spatial_context = self.spatial.process(maze_view, (self.robot.x, self.robot.y))
        motor_context = self.motor.process(
            self.workspace.conscious_content,
            self.workspace.conscious_context,
            action_options or [],
        )

        # Phase 2: Competition
        winner = self.workspace.run_competition()

        # Phase 3: Get final conscious state
        conscious_state = self.workspace.get_conscious_state()
        # Build integrated result
        result = {
            "cycle": self.cycle_count,
            "conscious": conscious_state,
            "vision": {
                "nearest_battery": maze_view.get("nearest_battery"),
                "other_bot": maze_view.get("other_bot"),
                "visible_count": len(maze_view.get("visible_cells", [])),
            },
            "spatial": spatial_context,
            "winner": winner["module"].name if winner else None,
        }

        return result

    def get_plan_to_goal(self, goal_type="BATTERY"):
        """
        Get a plan to reach a goal using spatial module.
        """
        # Get goal position from current vision
        if goal_type == "BATTERY":
            maze_view = self.vision.last_perception
            if maze_view and "nearest_battery" in maze_view:
                goal_pos = maze_view["nearest_battery"]
                return self.spatial.get_path_to_goal(
                    goal_pos, (self.robot.x, self.robot.y)
                )
        return []

    def get_conscious_summary(self):
        """Get summary of current conscious state for display."""
        state = self.workspace.get_conscious_state()
        return {
            "conscious_type": state["content"].get("type")
            if state["content"]
            else None,
            "context": state["context"],
            "recent_winners": [e["winner"] for e in state["recent_episodes"][-3:]],
        }
