"""
################################################################################
#                                                                              #
#      _      ______          _____  _   _ ______ _____                        #
#     | |    |  ____|   /\   |  __ \| \ | |  ____|  __ \                       #
#     | |    | |__     /  \  | |__) |  \| | |__  | |__) |                      #
#     | |    |  __|   / /\ \ |  _  /| . ` |  __| |  _  /                       #
#     | |____| |____ / ____ \| | \ \| |\  | |____| | \ \                       #
#     |______|______/_/    \_\_|  \_\_| \_|______|_|  \_\                      #
#                                                                              #
#      ______ _   _  _____ _____ _   _ ______                                  #
#     |  ____| \ | |/ ____|_   _| \ | |  ____|                                 #
#     | |__  |  \| | |  __  | | |  \| | |__                                    #
#     |  __| | . ` | | |_ | | | | . ` |  __|                                   #
#     | |____| |\  | |__| |_| |_| |\  | |____                                  #
#     |______|_| \_|\_____|_____|_| \_|______|                                 #
#                                                                              #
################################################################################

GENERAL LEARNER 5 (GL5) - THE COGNITIVE ENGINE
==============================================

This module implements the core 'Brain' of the agent. It is an implementation 
of the Universal Learner principle, augmented with Relational Frame Theory 
(RFT) and Global Workspace Theory (GWT).

SCIENTIFIC ARCHITECTURE:
------------------------
1. OPERANT CONDITIONING:
   Implements B.F. Skinner's (1938) principles of reinforcement. Actions 
   that lead to positive outcomes (batteries) increase in weight.
   Ref: Skinner, B. F. (1938). The Behavior of Organisms.

2. UNIVERSAL LEARNER (UL):
   Follows Walter Fritz's model: Perception -> Representation -> Choice. 
   The agent maps 'Situations' (Fuzzy Vectors) to 'Actions'.
   Ref: Fritz, W. (1989). The General Learner.

3. RELATIONAL FRAME THEORY (RFT):
   Implements Hayes' (2001) RFT for derived relational responding. Enables 
   inference without direct experience (e.g., A is like B, B does X, therefore A does X).
   Ref: Hayes, S. C., et al. (2001). Relational Frame Theory.

4. HIERARCHICAL MACRO COMPOSITION:
   Models the basal ganglia's ability to 'chunk' sequences of actions into 
   single motor programs (Macros).

5. SOCIAL LEARNING (VICARIOUS):
   Based on Albert Bandura's Social Learning Theory. Robots can observe 
   and imitate each other when in proximity.
   Ref: Bandura, A. (1977). Social Learning Theory.

Author: Marco
"""

import random
import json
import math
import time
from collections import defaultdict
from memory import Memory
from fuzzy_logic import FBN
from constants import *
from rft import RelationalFrameEngine


class Learner:
    """
    ############################################################################
    #   _      ______          _____  _   _ ______ _____                       #
    #  | |    |  ____|   /\   |  __ \| \ | |  ____|  __ \                      #
    #  | |    | |__     /  \  | |__) |  \| | |__  | |__) |                     #
    #  | |    |  __|   / /\ \ |  _  /| . ` |  __| |  _  /                      #
    #  | |____| |____ / ____ \| | \ \| |\  | |____| | \ \                      #
    #  |______|______/_/    \_\_|  \_\_| \_|______|_|  \_\                     #
    ############################################################################

    The cognitive core of the General Learner agent.

    This class orchestrates the complete cognitive loop:
    1. PERCEPTION: Scanning the environment and converting it to Fuzzy Vectors.
    2. INFERENCE: Choosing an action through the Decision Cascade (Phases A-D).
    3. PLANNING: Prospective simulation of future states (BFS over cognitive map).
    4. LEARNING: Encoding experiences and consolidating them during sleep.
    """

    def __init__(self, memory: Memory, environment=None):
        """
        Initialises the cognitive engine with all subsystems.

        Args:
            memory: The Memory subsystem (hippocampal-cortical storage)
            environment: The Environment subsystem (optional, for maze_id)
        """
        self.memory = memory
        self.environment = environment  # GL5: for maze_id in territory

        # Execution mode: 'COMMAND' (human-guided) or 'AUTONOMOUS' (self-directed)
        self.mode = "COMMAND"

        # Procedural memory: sequences of actions awaiting execution
        # Analogous to the basal ganglia's action chunking capability
        self.active_plan = []

        # Visuospatial working memory: expected future perceptions
        # Models the prefrontal cortex's prospective memory -- 'what
        # should I expect to see after this action?'
        self.agenda = []

        # Bayesian action selection toggle
        self.bayesian = True

        # Fuzzy logic processor for perceptual vectorisation
        self.fuzzy_processor = FBN()

        # Real-time cognitive state monitoring
        self.last_inference_info = {"type": "IDLE", "details": ""}

        # GL5: Debug/tracking attributes
        self.last_command_processed = ""
        self._last_tokens = []
        self._last_perception = []

        # GL5: RFT engine for derived relational reasoning
        self.rft_engine = RelationalFrameEngine()

        # GL5.1: Fuzzy Inference System for flexible reasoning
        from fuzzy_engine import FuzzyInferenceSystem, FuzzyRFTIntegrator

        self.fuzzy_engine = FuzzyInferenceSystem()
        self.fuzzy_rft = FuzzyRFTIntegrator(self.fuzzy_engine, memory)

        # Loop prevention: monitors for behavioural stagnation
        # Analogous to the brain's dopamine-mediated novelty-seeking
        # when habitual loops become unrewarding
        self.pos_history = []
        self.action_history = []

        # GL5: Learned Objectives System
        # ================================
        # The agent learns what is rewarding/punishing from experience.
        # Not hardcoded - objectives emerge from accumulated rewards.
        # Maps perception patterns to accumulated reward values.
        self.objective_values = {}
        """
        Dictionary mapping perception patterns to learned reward values.
        Positive values =pleasure seeking (goals). Negative = pain avoidance.
        """

        # Stagnation tracking
        self.stagnant = False
        self._stagnation_cooldown = 0
        self._zero_reward_streak = 0
        self._last_reward = 0

        # GL5.1: Last reinforcement and command tracking for display
        self._last_reinforcement = 0
        self._last_command_taught = None
        self._last_sleep_triggered = False

        # Caching for situational graph to prevent overload
        self._situational_graph_cache = None
        self._situational_graph_timestamp = 0

        # Per-cycle rules cache for act() method
        self._act_rules_cache = None
        self._act_rules_timestamp = 0

        # GL5.1: Vicarious Learning (Imitation) State
        # =============================================
        # Implements observational learning where one robot watches
        # and imitates another robot's actions when within proximity.
        # Based on Bandura's social learning theory.
        self.vicarious_enabled = True
        self._vicarious_observed_actions = []  # Actions seen from other bot
        self._vicarious_imitated_count = {}  # Count how many times each action was imitated
        self._vicarious_saturation = 0  # Imitation saturation level (0-100)
        self._vicarious_autonomous_streak = 0  # Consecutive autonomous actions
        self._vicarious_last_demonstrator = None  # Track who we're watching
        self._vicarious_imitation_mode = False  # Currently imitating?
        self._vicarious_current_sequence = []  # Current sequence being observed/imitated

        self._last_gwt_context = None  # GL5.1: Store last GWT context

        # GL5.1: Hearing System (Social Learning through Sound)
        # ===================================================
        # Los robots "cantan" sus acciones y se "oyen" mutuamente.
        # Este sistema procesa los sonidos escuchados y los asocia con acciones.
        self._heard_this_cycle = []  # Songs heard from other bots this cycle
        self._last_sang_action = None  # Action the robot sang last
        self._hearing_sequence = []  # Sequence of heard songs
        self._song_action_beliefs = {}  # Beliefs about song-action associations

        # GL5.1: Imagination Mode (Abstract Reasoning)
        # =============================================
        # Cuando el robot está ocioso, entra en modo imaginación
        # donde reorganiza el conocimiento para crear abstracciones.
        self._imagination_enabled = IMAGINATION_ENABLED
        self._imagination_mode = False  # Currently in imagination?
        self._imagination_cycles = 0  # Cycles spent in imagination
        self._idle_counter = 0  # Consecutive idle turns
        self._last_reward_was_positive = True  # Track reward for idle detection
        self._imagined_productions = []  # Productions created in imagination

        # GL5.1: Body State & Homeostasis
        self.energy = 100.0
        self.valence = 0.0  # Emotional tone (pleasure/pain balance)
        self.stress = 0.0  # Collision/penalty tally
        self._last_body_update = time.time()

    def act(self, robot, text_command=None, other_bot=None, gwt_context=None):
        """
        Determines the next action -- the core decision function.

        Implements a hierarchical cascade of inference pathways,
        each representing increasingly abstract cognitive processes:

        GL5 Dual-Bot: other_bot parameter enables mutual recognition
        in perception (OTHER_BOT_DETECTED concept).

        GL5.1: gwt_context provides Global Workspace Theory conscious content
        for integration with long-range vision and spatial awareness.

        PHASE A: MACRO MATCH (Basal Ganglia -- Procedural Memory)
        ---------------------------------------------------------
        The most specific cognitive pathway. Retrieves pre-learned
        action sequences (macros) from procedural memory.

        Biological analogue: The basal ganglia's habit system --
        once a behavioural sequence is learned (e.g., 'navigate
        to charger'), it executes automatically without ongoing
        cortical supervision. Represented in the brain by the
        striatum's direct pathway.

        Reference: Graybiel, A.M. (2008). Habits, rituals, and
        the evaluative brain. Annual Review of Neuroscience, 31, 359-387.

        PHASE B: TOKEN DECOMPOSITION (Broca's Area -- Compositional Processing)
        ----------------------------------------------------------------------
        Breaks complex commands into word-level components, executing
        each in sequence. Models the brain's ability to understand
        compositional semantics -- 'forward AND right' becomes two
        separate action selections.

        Biological analogue: Broca's area in the left inferior
        frontal gyrus -- responsible for syntactic parsing and
        compositional language understanding.

        Reference: Friederici, A.D. (2011). The brain's distinct
        network components for language. Nature Reviews Neuroscience, 12, 78-88.

        PHASE C: ASSOCIATIVE MEMORY (Cortex -- Semantic Retrieval)
        ----------------------------------------------------------
        General concept-to-action mappings, ignoring specific
        perceptual context. The 'semantic memory' layer -- knowing
        that 'this concept generally leads to this action'.

        Biological analogue: The neocortex's semantic memory system --
        the distributed store of learned associations, particularly
        in inferior temporal cortex for object concepts and premotor
        cortex for action concepts.

        Reference: Pulvermüller, F. (2012). Meaning and the brain:
        the semantic subsumption of conceptual knowledge. Cortex, 48(5), 641-647.

        PHASE D: RFT DERIVED INFERENCE (Prefrontal Cortex -- Abstract Reasoning)
        ------------------------------------------------------------------------
        GL5's novel contribution. When no direct experience exists,
        uses derived relational networks to infer an action.

        Example: If 'AVANZA' → FORWARD was learned, and GO is coordinate
        with AVANZA, then GO → FORWARD is inferred without direct teaching.

        Biological analogue: The prefrontal cortex's abstract relational
        reasoning -- the ability to see that 'X is like Y' without having
        directly experienced X and Y together. This is the cognitive
        capacity that distinguishes human reasoning from pure conditioning.

        Reference: Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001).
        Relational Frame Theory. Chapter 4: Derived Relational Responding.

        PHASE 1: ACTIVE PLAN EXECUTION (Striatum -- Habitual Sequence)
        --------------------------------------------------------------
        If a plan exists from prior Phase A/B decomposition, execute
        sequentially without re-evaluation. Models the automatic
        execution of learned motor programmes.

        PHASE 1.5: STAGNATION DETECTION (VTA -- Novelty/Exploration)
        -----------------------------------------------------------
        Detects behavioural loops and forces exploration. The brain's
        dopamine system tracks prediction errors -- when outcomes are
        worse than expected (or unchanged despite action), the system
        shifts from exploitation to exploration.

        PHASE 2: THOMPSON SAMPLING (Exploration/Exploitation Balance)
        ---------------------------------------------------------------
        When no plan exists and no direct rule matches, uses Bayesian
        sampling to select actions. Models the brain's exploration-
        exploitation trade-off, balancing familiar rewarding actions
        against novel possibilities.

        Args:
            robot: The Robot instance (provides get_state())
            text_command: Optional human-provided command string

        Returns:
            int: The selected action (ACT_LEFT, ACT_RIGHT, etc.)
        """
        # Get current perceptual state (pass other_bot for collision-aware perception)
        state = robot.get_state(other_bot)
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)

        # Store for debug display
        try:
            if isinstance(fuzzy_vector, list):
                self._last_perception = fuzzy_vector[:5]
            elif isinstance(fuzzy_vector, dict):
                self._last_perception = [
                    f"{k}:{list(v.keys())[0] if v else '?'}"
                    for k, v in list(fuzzy_vector.items())[:5]
                ]
            else:
                self._last_perception = []
        except (json.JSONDecodeError, KeyError, TypeError):
            self._last_perception = []

        # Cache rules for act() to avoid repeated DB queries
        current_time = time.time()
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache

        # 0. COMMAND PROCESSING PATHWAY
        # =============================
        # When a human provides a text command, the agent attempts
        # hierarchical interpretation through Phases A → D
        if text_command and text_command.strip():
            # Track command for debug display
            self.last_command_processed = text_command.strip()
            concept_ids = self.memory.tokenize(text_command)
            self._last_tokens = concept_ids  # Store for debug
            # Use cached rules instead of fetching again
            # rules = self.memory.get_rules() - REMOVED to use cache

            # --- PHASE A: MACRO MATCH ---
            # Exact command-to-sequence retrieval
            full_text_id = self.memory.get_or_create_concept_id(
                text_command.strip().upper()
            )
            for r in rules:
                if (
                    r["command_id"] == full_text_id
                    and r["is_composite"] == 1
                    and r["macro_actions"]
                ):
                    try:
                        actions = json.loads(r["macro_actions"])
                        if actions:
                            self.active_plan = actions[1:]
                            self.last_inference_info = {
                                "type": "MACRO MATCH",
                                "details": f"Command: {text_command}",
                            }
                            return actions[0]
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue

            # --- PHASE B: TOKEN DECOMPOSITION ---
            # Compositional command understanding
            if len(concept_ids) > 1:
                decomposed_plan = []
                for cid in concept_ids:
                    sub_action = self._get_action_for_concept(cid, rules)
                    if sub_action is not None:
                        decomposed_plan.append(sub_action)

                if decomposed_plan:
                    self.active_plan = decomposed_plan[1:]
                    self.last_inference_info = {
                        "type": "DECOMPOSITION",
                        "details": f"Tokens: {len(concept_ids)}",
                    }
                    return decomposed_plan[0]

            # --- PHASE C: SIMPLE CONCEPT MATCH ---
            # Context-specific + general concept retrieval
            # GL5: Priority - first check general command (any perception)
            best_action = None
            best_weight = -999

            for r in rules:
                if r["command_id"] == full_text_id:
                    # GL5: Accept both specific perception OR general command
                    # Specific match (same perception) OR general (no perception filter)
                    is_specific_match = r["perception_pattern"] == perc_id
                    has_perception = (
                        r["perception_pattern"] and r["perception_pattern"] != "None"
                    )

                    # If has perception, need match. If no perception, accept any.
                    if (is_specific_match) or (not has_perception):
                        # Weight threshold: positive = good, negative = avoid
                        if r["weight"] > best_weight:
                            best_weight = r["weight"]
                            best_action = r["target_action"]

            if best_action is not None and best_weight > -5:  # Not heavily punished
                self.last_inference_info = {
                    "type": "ASSOCIATIVE MEMORY",
                    "details": f"Command learned (w={best_weight:.1f})",
                }
                return best_action

            # --- PHASE D: RFT DERIVED INFERENCE ---
            # Only activates when Phases A-C have found no match --
            # the 'shadow reasoning' fallback of GL5
            frames = self.memory.get_frames_for_concept(full_text_id)
            for frame in frames:
                if frame["relation_type"] == "COORD":
                    partner_id = (
                        frame["concept_b"]
                        if frame["concept_a"] == full_text_id
                        else frame["concept_a"]
                    )
                    derived_action = self._get_action_for_concept(partner_id, rules)
                    if derived_action is not None:
                        self.last_inference_info = {
                            "type": "RFT DERIVED (Coord)",
                            "details": f"Frame strength: {frame['strength']:.2f}",
                        }
                        return derived_action

        # 0.5 AUTONOMOUS PLANNING (GL5)
        # ============================
        # If no command given and no active_plan, try to plan a path to goal
        # This implements prospective coding - mentally simulating future states
        if not text_command and not self.active_plan:
            plan_path, agenda_nodes = self.plan_with_agenda(perc_id, max_depth=6)
            if plan_path and agenda_nodes:
                self.active_plan = plan_path[1:] if len(plan_path) > 1 else []
                self.agenda = agenda_nodes[1:] if len(agenda_nodes) > 1 else []
                self.last_inference_info = {
                    "type": "PLANNED PATH",
                    "details": f"Steps: {len(plan_path)}, Goals: {len(agenda_nodes)}",
                }
                return plan_path[0] if plan_path else None

        # 1. PLAN EXECUTION
        # ================
        # Execute pre-loaded action sequence from Phase A/B
        if self.active_plan:
            if self.agenda:
                self.agenda.pop(0)
            self.last_inference_info = {
                "type": "Executing Plan",
                "details": f"Remaining: {len(self.active_plan)}",
            }

            # Check stagnation BEFORE executing next action in plan
            self._update_stagnation(robot)
            if self.stagnant:
                self.active_plan = []  # Abort plan on stagnation
                self.last_inference_info = {
                    "type": "PLAN ABORTED (Stagnation)",
                    "details": "Forced exploration",
                }
            else:
                return self.active_plan.pop(0)

        # 1.5 STAGNATION CHECK
        # ====================
        # Detects behavioural loops -- analogous to the brain's
        # detection of prediction error when actions produce
        # no novel outcomes
        self._update_stagnation(robot)

        # Cooldown: if we just broke a stagnation, don't re-trigger immediately
        # This prevents TOC (touch-of-contract / obsessive-compulsive loops)
        if (
            self.stagnant
            and hasattr(self, "_stagnation_cooldown")
            and self._stagnation_cooldown > 0
        ):
            self.stagnant = False
            self._stagnation_cooldown -= 1

        if self.stagnant:
            self.last_inference_info = {
                "type": "STAGNANT (Obsession)",
                "details": "Forced Loop Break",
            }

            # Break loops by forcing opposite action type
            last_act = self.action_history[-1] if self.action_history else None
            last_pos = self.pos_history[-1] if self.pos_history else None

            # Determine break action based on what got us stuck
            break_action = ACT_FORWARD
            if last_act == ACT_FORWARD:
                # Stuck moving forward (wall) -> turn
                break_action = random.choice([ACT_LEFT, ACT_RIGHT])
            elif last_act == ACT_BACKWARD:
                # Stuck moving backward -> turn
                break_action = random.choice([ACT_LEFT, ACT_RIGHT])
            elif last_act in [ACT_LEFT, ACT_RIGHT]:
                # Stuck spinning -> move forward
                break_action = ACT_FORWARD
            else:
                # No history -> random exploration
                break_action = random.choice(
                    [ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD]
                )

            # 70% forced break, 30% random exploration (reduced from 80/20 for more variety)
            if random.random() < 0.7:
                chosen = break_action
            else:
                chosen = random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

            self.action_history.append(chosen)
            self._stagnation_cooldown = (
                3  # 3 cycles before stagnation can trigger again
            )
            return chosen

        # 2. THOMPSON SAMPLING
        # ===================
        # Bayesian action selection under uncertainty
        # Use cached rules for performance
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache

        # GL5.1: Store GWT context for integration
        self._last_gwt_context = gwt_context

        # GL5.1: Use GWT conscious content to boost relevant action weights
        # If GWT reports seeing a battery nearby, boost FORWARD action
        gwt_battery_boost = 0.0
        gwt_other_bot_nearby = False
        if gwt_context and isinstance(gwt_context, dict):
            vision = gwt_context.get("vision", {})
            if vision.get("nearest_battery"):
                dist = vision.get("nearest_battery_dist", 10)
                if dist <= 3:
                    gwt_battery_boost = 2.0 * (3 - dist)  # Closer = higher boost
            if vision.get("other_bot"):
                gwt_other_bot_nearby = True

        action_options = {}
        for r in rules:
            if r["perception_pattern"] == perc_id:
                a = r["target_action"]
                if a not in action_options:
                    action_options[a] = []
                action_options[a].append(r["weight"])

        # GL5.1: RFT Integration for Autonomous Flexibility
        # If direct rules are few or weak, boost actions from coordinate concepts
        if len(action_options) < 2 or any(sum(w)/len(w) < 2.0 for w in action_options.values()):
            # Find RFT coordinate concepts for the situation if any
            # (In GL5, perceptions can be concepts too if they are labeled)
            situation_concept_id = self.memory.get_or_create_concept_id(perc_id)
            if situation_concept_id:
                frames = self.memory.get_frames_for_concept(situation_concept_id)
                for frame in frames:
                    if frame["relation_type"] == "COORD" and frame["strength"] > 0.5:
                        partner_id = frame["concept_b"] if frame["concept_a"] == situation_concept_id else frame["concept_a"]
                        # Find rules for the coordinate situation
                        for r in rules:
                            if r["command_id"] == partner_id or r["perception_pattern"] == str(partner_id):
                                a = r["target_action"]
                                if a not in action_options:
                                    action_options[a] = []
                                # Add weighted RFT influence
                                action_options[a].append(r["weight"] * frame["strength"] * 0.5)

        # GL5.1: Vicarious Learning Check
        # ================================
        # If another robot is nearby, observe their actions and potentially imitate
        vicarious_action = None
        if self.vicarious_enabled and other_bot is not None:
            vicarious_action = self._process_vicarious_learning(robot, other_bot)

        # Determine if we should use vicarious action based on saturation
        use_vicarious = False
        if vicarious_action is not None:
            saturation_prob = max(0, 100 - self._vicarious_saturation) / 100.0
            if random.random() < saturation_prob:
                use_vicarious = True

        if not action_options:
            # No learned rules - check if we should use vicarious or random
            if use_vicarious:
                self.last_inference_info = {
                    "type": "VICARIOUS (No Rules)",
                    "details": f"Imitating Bot{other_bot.self_id}: A{vicarious_action}",
                }
                self._vicarious_imitation_mode = True
                return vicarious_action
            else:
                self.last_inference_info = {
                    "type": "UNKNOWN SITUATION",
                    "details": "Random Action",
                }
                self._vicarious_autonomous_streak += 1
                self._check_vicarious_recovery()
                return random.choice([ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD])

        # Sample from posterior distribution
        best_action = None
        best_sample = -1
        for action, weights in action_options.items():
            w = sum(weights) / len(weights)

            # GL5.1: Apply GWT battery boost (forward toward battery)
            if gwt_battery_boost > 0 and action == ACT_FORWARD:
                w += gwt_battery_boost

            # GL5.1: Apply GWT avoidance boost (avoid moving toward other bot)
            if gwt_other_bot_nearby and other_bot is not None:
                if action == ACT_FORWARD:
                    w -= 1.0  # Slight penalty to avoid collision

            sample = random.betavariate(max(0.1, w + 1), 2)
            if sample > best_sample:
                best_sample = sample
                best_action = action

        # GL5.1: Override with vicarious action if conditions met
        if use_vicarious and vicarious_action is not None:
            best_action = vicarious_action
            self.last_inference_info = {
                "type": "VICARIOUS (Override)",
                "details": f"Imitating A{vicarious_action} (sat={self._vicarious_saturation})",
            }
            self._vicarious_imitation_mode = True
        elif best_action is not None:
            opts_str = ", ".join(
                [f"A{k}:{sum(v) / len(v):.1f}" for k, v in action_options.items()]
            )
            self.last_inference_info = {
                "type": "THOMPSON SAMPLING",
                "details": opts_str,
            }
            self._vicarious_imitation_mode = False
            self._vicarious_autonomous_streak += 1
            self._check_vicarious_recovery()

        if best_action is not None:
            # GL5.1: Update Body State based on result of decision
            self._update_body_state(robot)
            
            self.action_history.append(best_action)
            if len(self.action_history) > 10:
                self.action_history.pop(0)

        return best_action
            
    def _update_body_state(self, robot):
        """Updates internal body state metrics based on robot's metabolic variables."""
        # Hunger decreases energy
        self.energy = max(0.0, 100.0 - (robot.hunger * 0.5))
        
        # Valence is moving average of reward
        self.valence = (self.valence * 0.9) + (getattr(robot, 'last_action_reward', 0) * 0.1)
        
        # Stress increases with collisions
        if getattr(robot, 'last_collision', False):
            self.stress = min(100.0, self.stress + 5.0)
        else:
            self.stress = max(0.0, self.stress - 0.5)

    def _get_action_for_concept(self, concept_id, rules):
        """
        Retrieves the most strongly associated action for a concept.

        Computes total weight per action for a given conceptual ID,
        returning the highest-weighted action. This implements the
        brain's pattern completion -- given a concept, retrieve
        the most frequently reinforced associated action.

        Biological analogue: The hippocampal CA3 auto-associative
        network's pattern completion -- given a partial cue (concept),
        retrieving the most strongly associated complete pattern (action).

        Args:
            concept_id: The conceptual ID to query
            rules: Pre-fetched rules list

        Returns:
            int: The highest-weight action, or None
        """
        concept_actions = {}
        for r in rules:
            if r["command_id"] == concept_id and not r["is_composite"]:
                a = r["target_action"]
                concept_actions[a] = concept_actions.get(a, 0) + r["weight"]

        if concept_actions:
            return max(concept_actions, key=concept_actions.get)
        return None

    def plan_with_agenda(self, start_perc_id, max_depth=8):
        """
        BFS planning over the situational transition graph.

        Constructs a mental model of the world as a graph of
        perception-action-perception transitions, then searches
        for a path from the current situation to a goal state.

        Biological analogue: The prefrontal cortex's prospective
        coding -- mentally simulating future states and planning
        multi-step trajectories. The 'agenda' stores expected
        perceptual outcomes of planned actions.

        Reference: Rushworth, M.F.S. & Behrens, T.E.J. (2008).
        Choice, uncertainty and value in prefrontal and cingulate
        cortex. Nature Neuroscience, 11, 389-397.

        Args:
            start_perc_id: Starting perception pattern JSON
            max_depth: Maximum plan length

        Returns:
            tuple: (action_path, landmark_perceptions)
        """
        import time

        current_time = time.time()

        # Use cached rules for performance
        if (
            self._act_rules_cache is None
            or current_time - self._act_rules_timestamp > 1.0
        ):
            self._act_rules_cache = self.memory.get_rules()
            self._act_rules_timestamp = current_time
        rules = self._act_rules_cache
        graph = {}
        for r in rules:
            s_from = r["perception_pattern"]
            if s_from not in graph:
                graph[s_from] = []
            graph[s_from].append(
                {
                    "action": r["target_action"],
                    "next_s": r["next_perception"],
                    "weight": r["weight"],
                }
            )

        goals = {r["perception_pattern"] for r in rules if r["weight"] >= 5}
        # GL5: Also include learned objectives (perceptions with high accumulated value)
        for perc, value in self.objective_values.items():
            if value >= 3.0:  # OBJECTIVE_THRESHOLD
                goals.add(perc)
        if not goals:
            return [], []

        queue = [(start_perc_id, [], [start_perc_id])]
        visited = {start_perc_id}

        while queue:
            current_s, path, landmarks = queue.pop(0)
            if len(path) >= max_depth:
                continue

            if current_s in goals and path:
                return path, landmarks

            if current_s in graph:
                for trans in graph[current_s]:
                    next_s = trans["next_s"]
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        queue.append(
                            (next_s, path + [trans["action"]], landmarks + [next_s])
                        )

        return [], []

    def get_situational_graph(self, limit=30):
        """
        Returns the situational transition graph for visualisation.

        Used by the UI to display the agent's internal model of
        the world -- a cognitive map of perception-action links.

        Uses caching to prevent repeated heavy database queries.
        """
        import time

        current_time = time.time()

        if self._situational_graph_cache is not None:
            if current_time - self._situational_graph_timestamp < 2.0:
                return self._situational_graph_cache

        rules = self.memory.get_rules(limit=100)
        nodes = set()
        edges = []

        # First pass: collect all perception patterns as nodes
        for r in rules:
            perc = r["perception_pattern"]
            if perc:
                nodes.add(perc)

        # Second pass: create edges from transitions (sleep-cycle created)
        transition_count = 0
        for r in rules:
            if len(edges) >= limit:
                break
            s1 = r["perception_pattern"]
            s2 = r["next_perception"]
            if s1 and s2:
                nodes.add(s2)
                edges.append((s1, r["target_action"], s2, r["weight"], r["command_id"]))
                transition_count += 1

        # If no transitions (no sleep yet), show action-based associations instead
        if transition_count == 0 and nodes:
            for r in rules:
                if len(edges) >= limit:
                    break
                perc = r["perception_pattern"]
                action = r["target_action"]
                if perc:
                    # Create virtual "action node" for visualization
                    action_node = f"ACTION_{action}"
                    nodes.add(action_node)
                    edges.append(
                        (perc, action, action_node, r["weight"], r["command_id"])
                    )

        self._situational_graph_cache = (list(nodes), edges)
        self._situational_graph_timestamp = current_time
        return list(nodes), edges

    def learn(self, robot, action, reward, text_command=None, other_bot=None):
        """
        Records an experience in episodic memory.

        This is the 'encoding' function -- every perception-action-outcome
        triplet is stored in the episodic buffer for later consolidation.

        Also updates the spatial cognitive map (territory), modelling
        the hippocampal formation's dual function: what happened
        (episodic) and where it happened (spatial).

        GL5 Dual-Bot: other_bot parameter enables collision event recording.

        Biological analogue: The hippocampal CA1 region's place cells
        -- simultaneously encoding 'what' (event) and 'where' (location)
        in the same neural ensemble.

        Reference: Eichenbaum, H. (2014). Time cells in the hippocampus:
        a temporal basis for episodic memory. Hippocampus, 24(12), 1365-1379.

        Args:
            robot: The Robot instance
            action: The action performed
            reward: The reinforcement received
            text_command: Optional command that triggered action
            other_bot: Optional other robot for collision detection
        """
        state = robot.get_state(other_bot)
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)

        # Track reward for stagnation detection
        if not hasattr(self, "_last_reward"):
            self._last_reward = 0
        self._last_reward = reward
        if not hasattr(self, "_zero_reward_streak"):
            self._zero_reward_streak = 0
        if reward == 0:
            self._zero_reward_streak += 1
        else:
            self._zero_reward_streak = 0

        # GL5.1: Track for display
        self._last_reinforcement = reward
        if text_command and text_command.strip():
            self._last_command_taught = text_command.strip().upper()

        # Invalidate situational graph cache when new learning occurs
        self._situational_graph_cache = None

        # 1. Episodic encoding
        self.memory.add_chrono(fuzzy_vector, action, reward, text_command)

        # 1.1 GL5: Force command-to-action association in semantic memory
        # ================================================================
        # When a human gives a command and the robot executes an action,
        # immediately create a direct rule in semantic memory (strong association).
        # This ensures the robot learns commands quickly instead of being "stupid".
        if text_command and text_command.strip():
            cmd_id = self.memory.get_or_create_concept_id(text_command.strip().upper())

            # GL5: Learning by reinforcement (operant conditioning)
            # ====================================================
            # - reward > 0: ACCIÖN CORRECTA →-premiar (peso positivo)
            # - reward < 0: ACCIÖN INCORRECTA →castigar (peso negativo)
            # - guided_mode: reforzar más la asociación guíada

            # Base weight from actual reward (positive=reward, negative=punish)
            base_weight = reward if reward != 0 else 5.0

            # In guided mode, strengthen the association more (facilitated learning)
            is_guided = getattr(self, "_guided_this_step", False)
            if is_guided and base_weight > 0:
                base_weight = 15.0  # Guided = stronger positive
            elif is_guided and base_weight <= 0:
                base_weight = -15.0  # Guided punishment = stronger negative

            self.memory.add_rule(
                perc_id,
                action,
                weight=base_weight,
                next_perception=None,
                command_id=cmd_id,
                memory_type=MEMORY_SEMANTIC,
            )

            # GL5.1: Self-labeling - Learn action concepts without commands
            # ==========================================================
            # When executing an action (even without a command), the robot
            # creates a concept for that action. This allows self-reference
            # and the ability to compose complex plans from simple actions.
            action_names = {0: "LEFT", 1: "RIGHT", 2: "FORWARD", 3: "BACKWARD"}
            action_concept = action_names.get(action, f"ACT_{action}")

            # Create self-action concept (e.g., "I_DID_FORWARD")
            self_action_id = self.memory.get_or_create_concept_id(
                f"SELF_{action_concept}"
            )
            if self_action_id:
                # Associate self-action with the same action (meta-learning)
                self.memory.add_rule(
                    perc_id,
                    action,
                    weight=base_weight * 0.5,  # Weaker than command, but still learns
                    next_perception=None,
                    command_id=self_action_id,
                    memory_type=MEMORY_SEMANTIC,
                )

        # 1.2 GL5.1: Self-labeling for autonomous actions (no command given)
        # ===================================================================
        # When robot acts autonomously (no text command), it still learns
        # to label its own actions, enabling self-awareness and planning.
        if not text_command or not text_command.strip():
            action_names = {0: "LEFT", 1: "RIGHT", 2: "FORWARD", 3: "BACKWARD"}
            action_concept = action_names.get(action, f"ACT_{action}")

            # Create or retrieve self-action concept
            self_action_id = self.memory.get_or_create_concept_id(
                f"SELF_{action_concept}"
            )

            # Learn: in this perception, "SELF_FORWARD" means do FORWARD
            # This creates a self-referential action concept
            self.memory.add_rule(
                perc_id,
                action,
                weight=3.0,  # Moderate learning for self-actions
                next_perception=None,
                command_id=self_action_id,
                memory_type=MEMORY_SEMANTIC,
            )

            # Track action sequence for plan composition
            if not hasattr(self, "_action_sequence_buffer"):
                self._action_sequence_buffer = []
            self._action_sequence_buffer.append((perc_id, action, reward))

            # Buffer limit - keep last 10 actions
            if len(self._action_sequence_buffer) > 10:
                self._action_sequence_buffer.pop(0)

            # Compose macros from repeated patterns
            self._try_compose_macro()

        # 1.5 GL5: Learn objectives from experience
        # ==========================================
        # The agent learns what is rewarding/punishing from accumulated experience.
        # This replaces hardcoded battery goals with learned value associations.
        from constants import OBJECTIVE_LEARNING_RATE, NOVELTY_BONUS

        # Track novelty (new perception = intrinsic reward)
        is_novel = perc_id not in self.objective_values

        # Update the objective value for this perception
        if perc_id not in self.objective_values:
            self.objective_values[perc_id] = reward
        else:
            # Learning rate - gradually adjust based on new evidence
            self.objective_values[perc_id] = (
                self.objective_values[perc_id] * (1 - OBJECTIVE_LEARNING_RATE)
                + reward * OBJECTIVE_LEARNING_RATE
            )

        # Bonus for novel situations (exploration drive)
        if is_novel and reward >= 0:
            self.objective_values[perc_id] += NOVELTY_BONUS

        # 1.6 GL5: Homeostatic pain signals
        # ================================
        # The agent learns that hunger/tiredness are painful and seeks relief.
        from constants import HUNGER_PAIN, TIRED_PAIN

        # Create homeostatic state perception
        homeo_key = f"homeo_h{robot.hunger}_t{robot.tiredness}"

        if homeo_key not in self.objective_values:
            self.objective_values[homeo_key] = 0

        # Pain increases with hunger/tiredness (avoidance drive)
        pain_signal = (robot.hunger * HUNGER_PAIN / 50) + (
            robot.tiredness * TIRED_PAIN / 50
        )
        self.objective_values[homeo_key] = pain_signal

        # 1.7 GL5: Mirror Self-Recognition
        # ================================
        # The robot can recognize itself in a mirror.
        # This is the basis for self-concept and theory of mind.
        from constants import MIRROR_ID, MIRROR_RECOGNITION_REWARD

        # Check if robot sees a mirror in the 3x3 perception grid
        perception = state.get("perception", [])
        has_mirror = False
        if perception:
            for row in perception:
                for cell in row:
                    if cell == MIRROR_ID:
                        has_mirror = True
                        break
                if has_mirror:
                    break

        if has_mirror:
            # Self-recognition! The robot sees itself.
            # This reinforces the self-concept (autobiographical memory)
            self.last_inference_info = {
                "type": "SELF-RECOGNITION",
                "details": f"Mirror seen! Self-ID: {robot.self_id}",
            }

            # Learn that "seeing self" is rewarding (self-preservation)
            # But limit the learning to avoid obsessive mirror-seeking loops
            mirror_perc = f"mirror_self_{robot.self_id}"
            if mirror_perc not in self.objective_values:
                self.objective_values[mirror_perc] = 0

            # Only reinforce moderately - prevent obsessive self-admiration loops
            # The robot can enjoy seeing itself but must move on
            self.objective_values[mirror_perc] += MIRROR_RECOGNITION_REWARD * 0.05

            # Cap the mirror reward to prevent obsession
            if self.objective_values[mirror_perc] > 8.0:
                self.objective_values[mirror_perc] = 8.0

        # 1.8 GL5 Dual-Bot: Other Bot Recognition
        # =======================================
        # When a bot sees another robot in perception, it detects the
        # other bot's ID and compares it with its own self_id.
        # This enables mutual recognition and prevents self-confusion.
        OTHER_BOT_ID = 99  # Magic number for other bot in perception grid

        has_other_bot = False
        other_bot_direction = None
        if perception:
            directions = [
                (-1, -1),
                (0, -1),
                (1, -1),  # North row
                (-1, 0),
                (1, 0),  # Middle row
                (-1, 1),
                (0, 1),
                (1, 1),
            ]  # South row
            dir_names = {
                (-1, -1): "NW",
                (0, -1): "N",
                (1, -1): "NE",
                (-1, 0): "W",
                (1, 0): "E",
                (-1, 1): "SW",
                (0, 1): "S",
                (1, 1): "SE",
            }
            for dy in range(3):
                for dx in range(3):
                    if dy == 1 and dx == 1:
                        continue  # Skip center (self position)
                    if dy == 1 and dx == 1:
                        continue
                    if dy == 1 and dx == 1:
                        continue
                    if perception[dy][dx] == OTHER_BOT_ID:
                        has_other_bot = True
                        other_bot_direction = dir_names.get((dx - 1, dy - 1), "?")

        if has_other_bot and other_bot is not None:
            # Other bot detected! Compare self_id
            perceived_id = other_bot.self_id
            self_id = robot.self_id

            if perceived_id != self_id:
                # OTHER BOT RECOGNIZED - different from self
                # This is the foundation for theory of mind
                self.last_inference_info = {
                    "type": "OTHER_BOT_DETECTED",
                    "details": f"Bot{perceived_id} seen at {other_bot_direction} (I'm Bot{self_id})",
                }

                # Learn that seeing OTHER bot is different from self
                # This prevents self-confusion - important for social behavior
                other_perc_key = f"other_bot_{perceived_id}_{other_bot_direction}"
                if other_perc_key not in self.objective_values:
                    self.objective_values[other_perc_key] = 0

                # Neutral-to-slightly-positive learning from social contact
                # (not as rewarding as self-recognition, but valuable)
                self.objective_values[other_perc_key] += 0.3

                # Cap to prevent obsession
                if self.objective_values[other_perc_key] > 5.0:
                    self.objective_values[other_perc_key] = 5.0

            else:
                # This would be a bug - two bots shouldn't have same ID
                self.last_inference_info = {
                    "type": "ERROR",
                    "details": "ID collision detected!",
                }

        # 2. Spatial map update (GL5: with maze_id for multi-maze support)
        maze_id = (
            getattr(getattr(self, "environment", None), "maze_id", "default")
            if self.environment
            else "default"
        )
        self.memory.update_territory(
            robot.x,
            robot.y,
            perc_id,
            importance=reward if reward > 0 else 1.0,
            maze_id=maze_id,
        )

    def sleep_cycle(self):
        """
        The consolidation phase -- memory reprocessing during downtime.

        Called when the robot's battery is low and movement ceases.
        Triggers the 'systems consolidation' process analogous to
        slow-wave sleep in biological brains:

        1. DECAY (Synaptic downscaling)
        ---------------------------------
        All rule weights are multiplied by their decay rate. This
        models the brain's selective weakening of unused synapses
        during sleep, making room for new learning.

        Biological analogue: The 'synaptic homeostasis hypothesis'
        -- Tononi & Pedersen (2003) argue that sleep downscales
        the entire synaptic network, compensating for the day's
        net synaptic strengthening.

        Reference: Tononi, G. & Cicardone, C. (2003). Sleep and
        consolidation. Nature, 425, 594-595.

        2. MACRO INDUCTION (Chunk formation)
        -----------------------------------
        Repeated command sequences are collapsed into single macro
        actions. Models the basal ganglia's habit formation --
        converting multi-step deliberative sequences into automatic
        motor programmes.

        Reference: Graybiel, A.M. (2008). Habits, rituals, and the
        evaluative brain. Annual Review of Neuroscience, 31, 359-387.

        3. CONSOLIDATION (Episodic → Semantic)
        -----------------------------------------
        Episodic traces are strengthened into semantic rules. High-
        reward episodes are additionally promoted to semantic storage.
        Models the hippocampal-neocortical dialogue during sleep --
        the 'replay' of day's events that consolidates them into
        long-term memory.

        Reference: Rasch, B. & Born, J. (2013). About sleep's role
        in memory. Physiological Reviews, 93(2), 681-766.

        4. RFT DERIVATION (GL5 -- Abstract inference)
        ---------------------------------------------
        Runs the Relational Frame Theory engine to detect new
        coordinations, derive transitive relationships, and apply
        transformation of functions. This is the 'dreaming' phase
        in GL5 -- abstract relational reasoning occurring during
        the consolidation window.

        Reference: Hayes, S.C. et al. (2001). Relational Frame Theory.

        Returns:
            int: Number of new rules created
        """
        # 1. GL5.1: High-level reasoning (always runs during sleep cycle)
        # These don't depend on episodic history existence
        
        # GL5: RFT derivation cycle
        rft_result = self.rft_engine.run_cycle(self.memory)
        
        # GL5: Semantic Dreaming (Multimodal Synthesis)
        dream_results = self._semantic_dreaming()
        new_rules_count = dream_results.get("new_rules", 0)

        # 2. Apply forgetting
        self.memory.decay_rules()

        # Fetch episodic history
        history = self.memory.get_all_chrono()
        if not history:
            return new_rules_count

        # 3. Macro induction
        i = 0
        while i < len(history):
            # ... (rest of macro logic)
            cmd_text = history[i]["command_text"]
            if cmd_text and len(cmd_text) > 3:
                seq = []
                start_perc = history[i]["perception"]
                start_fuzzy = json.loads(start_perc)
                start_perc_id = json.dumps(start_fuzzy)

                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())

                while i < len(history) and history[i]["command_text"] == cmd_text:
                    seq.append(history[i]["action"])
                    i += 1

                if len(seq) > 1:
                    self.memory.add_rule(
                        start_perc_id,
                        seq[0],
                        weight=8.0,
                        is_composite=1,
                        macro_actions=seq,
                        command_id=cmd_id,
                        memory_type=MEMORY_EPISODIC,
                    )
                    new_rules_count += 1
            else:
                i += 1

        # 3. Standard consolidation (limited per cycle)
        max_per_cycle = MAX_RULES_PER_SLEEP_CYCLE - new_rules_count
        for i in range(len(history)):
            if new_rules_count >= MAX_RULES_PER_SLEEP_CYCLE:
                break
            record = history[i]
            perc_vector = json.loads(record["perception"])
            perc_id = json.dumps(perc_vector)
            action = record["action"]
            reward = record["reward"]
            cmd_text = record.get("command_text")

            cmd_id = None
            if cmd_text:
                cmd_id = self.memory.get_or_create_concept_id(cmd_text.upper())

            next_perc_id = None
            if i < len(history) - 1:
                next_fuzzy = json.loads(history[i + 1]["perception"])
                next_perc_id = json.dumps(next_fuzzy)

            w = 5.0 if reward > 0 else (1.0 if reward >= -5 else -2.0)

            # Episodic storage
            self.memory.add_rule(
                perc_id,
                action,
                weight=w,
                next_perception=next_perc_id,
                command_id=cmd_id,
                memory_type=MEMORY_EPISODIC,
            )

            # Semantic promotion for highly rewarding experiences
            if reward > 5:
                self.memory.add_rule(
                    perc_id,
                    action,
                    weight=w * 0.3,
                    next_perception=next_perc_id,
                    command_id=cmd_id,
                    memory_type=MEMORY_SEMANTIC,
                )

            new_rules_count += 1

        self.memory.clear_chrono()

        return new_rules_count

    def _semantic_dreaming(self):
        """
        Multimodal Synthesis phase: Analysis, Resolution, Synthesis, Generalization.
        
        This process consolidates speech and vision into a unified world model.
        """
        stats = {"new_rules": 0, "anchors": 0, "frames": 0}
        
        # 1. ANALYSIS & RESOLUTION: Find cross-modal overlaps
        pairs = self.memory.get_multimodal_pairs()
        
        for s_prod, v_prod, token in pairs:
            # 2. SYNTHESIS: Create absolute COORD frame between token and template
            # Get concept IDs for both
            v_concept_id = self.memory.get_or_create_concept_id(v_prod["name"])
            s_concept_id = self.memory.get_or_create_concept_id(token)
            
            # Create Multimodal Anchor (High-level production)
            self.memory.add_cognitive_production(
                production_type="MULTIMODAL_ANCHOR",
                name=f"LINK_{token}",
                description=json.dumps({
                    "speech_id": s_prod["id"],
                    "vision_id": v_prod["id"],
                    "token": token
                }),
                confidence=0.8,
                abstraction_level=3,
                is_imagined=True
            )
            stats["anchors"] += 1
            
            # Create RFT frame linking the visual concept to the speech response
            # This enables linguistic commands to trigger visual imagery
            self.memory.add_relational_frame(v_concept_id, "COORD", s_concept_id, 0.9)
            stats["frames"] += 1
            
        # 3. GENERALIZATION: Derive drawing rules for speech commands
        # If we have a spoken pattern with response 'X' and 'X' is a visual template,
        # create a rule for 'DRAW X' in the decision cascade.
        speech_prods = self.memory.get_cognitive_productions(production_type="SPEECH_PATTERN")
        for s in speech_prods:
            try:
                data = json.loads(s["description"])
                resp = data.get("response", "").upper()
                
                # Check if we have a visual template for this response
                v_prods = self.memory.get_cognitive_productions(production_type="VISUAL_PATTERN")
                for v in v_prods:
                    if v["name"].upper() == resp:
                        # Create a derived rule: Perception [ANY] + Command [RESP] -> DRAW TEMPLATE
                        # Note: We represent "Drawing" as a specific set of rules in GL5
                        self.memory.add_rule(
                            perception_pattern=None,
                            action=5, # Custom Action ID for 'DRAW' (if defined) or logic trigger
                            weight=5.0,
                            command_id=self.memory.get_or_create_concept_id(resp),
                            memory_type=MEMORY_DERIVED,
                            description=f"Derived drawing link for {resp}"
                        )
                        stats["new_rules"] += 1
            except:
                continue
                
        return stats

    def _update_stagnation(self, robot):
        """
        Detects behavioural loops and flags for intervention.

        Monitors three indicators of pathological behaviour:
        1. Static position -- not moving despite repeated action
        2. Oscillation -- cycling between two positions
        3. Action obsession -- repeatedly executing same action

        When detected, the system shifts to exploration mode,
        analogous to the brain's dopamine-mediated response to
        prediction error -- trying something new because the
        expected reward is not occurring.

        Biological analogue: The mesolimbic dopamine pathway's
        role in novelty-seeking and the switching between
        exploitation (current best) and exploration (new options).

        Reference: Kakade, S. & Dayan, P. (2002). Dopamine: generalisation
        and lookahead. Neural Networks, 15(4-6), 549-559.

        Args:
            robot: The Robot instance
        """
        # Track consecutive zero-reward actions (predicts stagnation risk)
        if not hasattr(self, "_zero_reward_streak"):
            self._zero_reward_streak = 0
        if not hasattr(self, "_last_reward"):
            self._last_reward = 0

        if self._last_reward == 0:
            self._zero_reward_streak += 1
        else:
            self._zero_reward_streak = 0
        self._last_reward = 0  # Reset, will be updated in learn()

        # Early warning: 5+ zero-reward cycles predicts stagnation
        if self._zero_reward_streak >= 5:
            self.stagnant = True
            return

        # Position tracking
        self.pos_history.append((robot.x, robot.y))
        if len(self.pos_history) > 15:  # Extended history
            self.pos_history.pop(0)

        if len(self.pos_history) < 8:  # More history needed
            self.stagnant = False
            return

        # Check: same action repeated 6+ times (more than 4)
        if len(self.action_history) >= 6:
            if len(set(self.action_history[-6:])) == 1:
                self.stagnant = True
                return

        # Check: oscillation between 2 positions (A-B-A-B pattern)
        last_6 = self.pos_history[-6:]
        # Check for back-and-forth between same two spots
        unique_positions = list(set(last_6))
        if len(unique_positions) == 2:
            # Check if alternating
            alternating = all(
                last_6[i] != last_6[i + 1] for i in range(len(last_6) - 1)
            )
            if alternating:
                self.stagnant = True
                return

        # Check: trapped in small area (3 positions or less in last 8)
        if len(set(self.pos_history[-8:])) <= 3:
            # But only if also taking same actions frequently
            if len(self.action_history) >= 4:
                recent_actions = self.action_history[-4:]
                if len(set(recent_actions)) <= 2:
                    self.stagnant = True
                    return

        self.stagnant = False

    def _try_compose_macro(self):
        """
        GL5.1: Attempts to compose hierarchical macros from repeated action sequences.
        Optimized to use database-backed intermediate memory for larger context.
        """
        # Fetch recent history from intermediate memory instead of just small buffer
        try:
            cur = self.memory.conn.cursor()
            cur.execute(
                "SELECT perception, action, reward FROM intermediate_memory ORDER BY id DESC LIMIT 50"
            )
            rows = cur.fetchall()
            if len(rows) < 10:
                # Fallback to in-memory buffer if not enough DB history
                if not hasattr(self, "_action_sequence_buffer") or len(self._action_sequence_buffer) < 3:
                    return
                buffer = self._action_sequence_buffer
            else:
                # Convert DB rows to buffer format (perception_id, action, reward)
                # Reverse to get chronological order (oldest first)
                buffer = [(r[0], r[1], r[2]) for r in reversed(rows)]
        except Exception:
            if not hasattr(self, "_action_sequence_buffer") or len(self._action_sequence_buffer) < 3:
                return
            buffer = self._action_sequence_buffer

        sequence_lengths = [2, 3, 4]  # Extended to length 4
        for seq_len in sequence_lengths:
            if len(buffer) < seq_len * 2:  # Need at least 2 occurrences
                continue

            sequence_counts = {}
            for i in range(len(buffer) - seq_len + 1):
                seq = tuple(a for _, a, _ in buffer[i : i + seq_len])
                rewards = [r for _, _, r in buffer[i : i + seq_len]]
                avg_reward = sum(rewards) / len(rewards) if rewards else 0
                start_perc = buffer[i][0]

                if seq not in sequence_counts:
                    sequence_counts[seq] = {"count": 0, "avg_reward": 0, "start_percs": []}
                
                sequence_counts[seq]["count"] += 1
                sequence_counts[seq]["avg_reward"] = (
                    sequence_counts[seq]["avg_reward"] * 0.7 + avg_reward * 0.3
                )
                sequence_counts[seq]["start_percs"].append(start_perc)

            for seq, data in sequence_counts.items():
                # Higher threshold for longer sequences
                min_count = 2 if seq_len <= 3 else 3
                if data["count"] >= min_count and data["avg_reward"] >= 1.0:
                    action_names = {0: "L", 1: "R", 2: "F", 3: "B"}
                    seq_str = "_".join(action_names.get(a, str(a)) for a in seq)
                    macro_name = f"MACRO_{seq_str}"

                    macro_id = self.memory.get_or_create_concept_id(macro_name)
                    actions = list(seq)
                    
                    # Create macro rules for the most frequent starting perceptions
                    for start_perc in set(data["start_percs"][:3]):
                        self.memory.add_rule(
                            start_perc,
                            actions[0],
                            weight=12.0,  # Increased weight for validated macros
                            is_composite=1,
                            macro_actions=actions,
                            command_id=macro_id,
                            memory_type=MEMORY_SEMANTIC,
                        )

                    for idx, action in enumerate(actions):
                        if idx < len(buffer):
                            step_perc = buffer[idx][0]
                            self.memory.add_rule(
                                step_perc,
                                action,
                                weight=5.0,
                                command_id=macro_id,
                                memory_type=MEMORY_EPISODIC,
                            )

    def _build_action_concept_network(self):
        """
        GL5.1: Builds a network of action concepts for self-reference and planning.
        """
        if not hasattr(self, "_action_sequence_buffer"):
            return {}

        action_names = {0: "LEFT", 1: "RIGHT", 2: "FORWARD", 3: "BACKWARD"}
        concept_actions = {}

        for _, action, _ in self._action_sequence_buffer:
            action_name = action_names.get(action, f"ACT_{action}")
            self_id = self.memory.get_or_create_concept_id(f"SELF_{action_name}")
            if self_id:
                concept_actions[f"SELF_{action_name}"] = action

        turn_id = self.memory.get_or_create_concept_id("SELF_TURN")
        if turn_id:
            concept_actions["SELF_TURN"] = {"LEFT": 0, "RIGHT": 1}

        move_id = self.memory.get_or_create_concept_id("SELF_MOVE")
        if move_id:
            concept_actions["SELF_MOVE"] = {"FORWARD": 2, "BACKWARD": 3}

        return concept_actions

    def get_composed_plans(self):
        """
        GL5.1: Returns learned composed plans for display/debugging.
        """
        rules = self.memory.get_rules(memory_type=MEMORY_SEMANTIC)
        macros = []

        for r in rules:
            if r.get("is_composite") == 1 and r.get("macro_actions"):
                try:
                    actions = json.loads(r["macro_actions"])
                    cmd_text = r.get("command_text", "UNKNOWN")
                    macros.append(
                        {
                            "name": cmd_text if cmd_text else f"Macro_{r['id']}",
                            "actions": actions,
                            "weight": r["weight"],
                        }
                    )
                except (json.JSONDecodeError, TypeError):
                    pass

        return macros

    def infer_fuzzy_action(self, robot, other_bot=None, gwt_context=None):
        """
        GL5.1: Fuzzy inference for action selection.

        Uses the fuzzy inference system to combine multiple perceptual
        variables and derive action recommendations with fuzzy strengths.

        This provides more flexible and nuanced action selection than
        hard boolean rules.

        GL5.1: gwt_context provides GWT conscious content for integration
        with long-range vision (nearest battery, other bot position).

        Args:
            robot: The Robot instance
            other_bot: Optional other robot for context
            gwt_context: Optional GWT cognitive cycle result

        Returns:
            tuple: (action, confidence) or (None, 0.0)
        """
        state = robot.get_state(other_bot)

        # Build fuzzy inputs from perception
        fuzzy_inputs = {
            "hunger": robot.hunger,
            "tiredness": robot.tiredness,
            "battery_distance": state.get("batt_distance", 15) or 15,
        }

        # GL5.1: Add GWT long-range vision inputs
        if gwt_context and isinstance(gwt_context, dict):
            vision = gwt_context.get("vision", {})
            if vision.get("nearest_battery_dist"):
                fuzzy_inputs["gwt_battery_distance"] = vision["nearest_battery_dist"]
            if vision.get("other_bot"):
                fuzzy_inputs["other_bot_visible"] = 1.0
            else:
                fuzzy_inputs["other_bot_visible"] = 0.0

        # Add wall distances
        raw_dist = state.get("raw_distances", {})
        for direction, dist in raw_dist.items():
            fuzzy_inputs[f"wall_{direction}"] = dist

        # Get reasoning trace
        trace = self.fuzzy_engine.get_fuzzy_reasoning_trace(fuzzy_inputs)

        # Build fuzzy rules from memory and RFT frames
        action_rules = []
        rules = self.memory.get_rules()

        for r in rules:
            action = r.get("target_action")
            weight = r.get("weight", 1.0)
            cmd_id = r.get("command_id")

            if action is not None:
                # Normalize weight to [0, 1]
                strength = min(1.0, max(0.0, weight / 20.0))
                action_rules.append((strength, action, strength))

        # Check RFT frames for derived rules
        frames = self.memory.get_all_frames()
        for frame in frames:
            derived_rule = self.fuzzy_rft.derive_fuzzy_rule_from_frame(frame, rules)
            if derived_rule:
                action_rules.append(
                    (
                        derived_rule.weight,
                        list(derived_rule.consequent.keys())[0],
                        derived_rule.weight,
                    )
                )

        # Fuzzy inference
        action, confidence = self.fuzzy_engine.infer_action_fuzzy(
            fuzzy_inputs, action_rules
        )

        return action, confidence

    def learn_fuzzy_relations(self):
        """
        GL5.1: Learn fuzzy relations between concepts from co-occurrence.

        Analyzes learned rules and frames to create fuzzy relations
        with continuous strength values.
        """
        rules = self.memory.get_rules()

        concept_cooccur = defaultdict(lambda: {"count": 0, "total": 0})

        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue
            action = r.get("target_action")
            weight = r.get("weight", 1.0)

            for other_r in rules:
                other_cmd = other_r.get("command_id")
                if other_cmd and other_cmd != cmd_id:
                    other_action = other_r.get("target_action")
                    if action == other_action:
                        key = tuple(sorted([cmd_id, other_cmd]))
                        concept_cooccur[key]["count"] += weight
                    concept_cooccur[key]["total"] += abs(weight)

        for (c1, c2), data in concept_cooccur.items():
            if data["total"] > 0:
                strength = data["count"] / data["total"]
                self.fuzzy_engine.add_relation(c1, c2, "SIM", strength)

    def get_fuzzy_status(self):
        """
        GL5.1: Returns fuzzy inference system status for debugging.

        Returns:
            dict: Status information about fuzzy reasoning
        """
        return {
            "fuzzy_sets": list(self.fuzzy_engine.fuzzy_sets.keys()),
            "relation_count": len(self.fuzzy_engine.relation_network),
            "rule_count": len(self.fuzzy_engine.rules),
        }

    def _process_vicarious_learning(self, robot, other_bot):
        """
        GL5.1: Processes vicarious (observational) learning when another robot is nearby.

        When within proximity threshold, the robot observes the other robot's actions
        and may imitate them. After imitating an action sequence 3 times, the robot
        transitions to autonomous execution of that learned behavior.

        The saturation mechanism ensures the robot doesn't become dependent on imitation:
        - Saturation increases each time we imitate
        - When saturation exceeds threshold, we prefer autonomous actions
        - Autonomous actions gradually reduce saturation

        Args:
            robot: The observer robot
            other_bot: The demonstrator robot (to observe)

        Returns:
            int: The action to imitate, or None if no imitation should occur
        """
        from constants import (
            VICARIOUS_PROXIMITY_THRESHOLD,
            VICARIOUS_IMITATION_REPETITIONS,
        )

        if not hasattr(other_bot, "last_action") or other_bot.last_action is None:
            return None

        dist = abs(robot.x - other_bot.x) + abs(robot.y - other_bot.y)

        if dist > VICARIOUS_PROXIMITY_THRESHOLD:
            self._vicarious_imitation_mode = False
            return None

        demonstrator_id = other_bot.self_id
        self._vicarious_last_demonstrator = demonstrator_id

        observed_action = other_bot.last_action

        if observed_action is None:
            return None

        if len(self._vicarious_observed_actions) >= VICARIOUS_ACTION_MEMORY_SIZE:
            self._vicarious_observed_actions.pop(0)
        self._vicarious_observed_actions.append(observed_action)

        if observed_action not in self._vicarious_imitated_count:
            self._vicarious_imitated_count[observed_action] = 0

        imitation_count = self._vicarious_imitated_count.get(observed_action, 0)

        if imitation_count < VICARIOUS_IMITATION_REPETITIONS:
            self._vicarious_imitated_count[observed_action] = imitation_count + 1
            self._vicarious_saturation = min(100, self._vicarious_saturation + 2)
            return observed_action

        return None

    def _check_vicarious_recovery(self):
        """
        GL5.1: Decreases imitation saturation after autonomous actions.

        Each autonomous action reduces saturation slightly. After enough
        consecutive autonomous actions, saturation fully resets, allowing
        the robot to be receptive to new demonstrations.
        """
        from constants import VICARIOUS_SATURATION_RECOVERY

        if self._vicarious_autonomous_streak >= VICARIOUS_SATURATION_RECOVERY:
            reduction = min(self._vicarious_saturation, 20)
            self._vicarious_saturation = max(0, self._vicarious_saturation - reduction)

            if self._vicarious_saturation == 0:
                self._vicarious_autonomous_streak = 0
                self._vicarious_imitated_count.clear()

    def learn_vicarious(self, robot, action, reward, other_bot):
        """
        GL5.1: Learns from vicarious (observed) experiences.

        When imitating another robot, the observer learns from the outcomes
        of those actions. Positive outcomes strengthen the tendency to imitate
        similar actions in the future.

        Args:
            robot: The observer robot
            action: The action that was taken (potentially imitated)
            reward: The outcome of the action
            other_bot: The demonstrator robot
        """
        from constants import VICARIOUS_LEARNING_RATE, VICARIOUS_IMITATION_REWARD

        if not self._vicarious_imitation_mode:
            return

        state = robot.get_state(other_bot)
        fuzzy_vector = self.fuzzy_processor.get_feature_vector(state)
        perc_id = json.dumps(fuzzy_vector)

        demonstrator_id = getattr(other_bot, "self_id", None)
        if demonstrator_id is None:
            return

        action_was_imitated = action in self._vicarious_imitated_count

        if reward > 0 and action_was_imitated:
            vicarious_reward = VICARIOUS_IMITATION_REWARD + (reward * 0.5)
            self.memory.add_rule(
                perc_id,
                action,
                weight=vicarious_reward * VICARIOUS_LEARNING_RATE,
                next_perception=None,
                command_id=None,
                memory_type=MEMORY_EPISODIC,
            )
            self.objective_values[perc_id] = (
                self.objective_values.get(perc_id, 0) + vicarious_reward * 0.1
            )

        if reward < -3:
            self._vicarious_saturation = min(100, self._vicarious_saturation + 5)

    def get_vicarious_status(self):
        """
        GL5.1: Returns the current vicarious learning status for display.

        Returns:
            dict: Status information about imitation state
        """
        return {
            "enabled": self.vicarious_enabled,
            "saturation": self._vicarious_saturation,
            "in_imitating_mode": self._vicarious_imitation_mode,
            "observed_actions": len(self._vicarious_observed_actions),
            "imitated_counts": dict(self._vicarious_imitated_count),
            "autonomous_streak": self._vicarious_autonomous_streak,
            "last_demonstrator": self._vicarious_last_demonstrator,
        }

    def get_last_activity(self):
        """
        GL5.1: Returns last reinforcement and command for display.
        """
        return {
            "last_reinforcement": getattr(self, "_last_reinforcement", 0),
            "last_command": getattr(self, "_last_command_taught", None),
            "sleep_triggered": getattr(self, "_last_sleep_triggered", False),
        }

    def reset_vicarious_state(self):
        """
        GL5.1: Resets all vicarious learning state.

        Called when switching bots or resetting the simulation to ensure
        clean state for the new robot.
        """
        self._vicarious_observed_actions.clear()
        self._vicarious_imitated_count.clear()
        self._vicarious_saturation = 0
        self._vicarious_autonomous_streak = 0
        self._vicarious_last_demonstrator = None
        self._vicarious_imitation_mode = False
        self._vicarious_current_sequence.clear()

    # =========================================================================
    # GL5.1: Hearing System (Social Learning through Sound)
    # =========================================================================

    def sing_action(self, action: int) -> str:
        """
        GL5.1: "Canta" la acción ejecutada.
        El robot produce un sonido que representa su acción.

        Args:
            action: The action performed (ACT_LEFT, ACT_RIGHT, etc.)

        Returns:
            str: The song/sound that was produced
        """
        from constants import ACTION_SONGS

        song = ACTION_SONGS.get(action, f"ACTION_{action}")
        self._last_sang_action = song
        return song

    def process_heard_songs(self, robot, other_bot) -> list:
        """
        GL5.1: Procesa los sonidos escuchados del otro robot.
        Calcula el "volumen" basado en la distancia y registra las asociaciones.

        Args:
            robot: The hearing robot (self)
            other_bot: The robot whose sounds we're hearing

        Returns:
            list: Songs heard this cycle
        """
        from constants import (
            HEARING_MAX_DISTANCE,
            HEARING_SONG_VOLUME_BASE,
            HEARING_SONG_VOLUME_DECAY,
            ACTION_SONGS,
        )

        if other_bot is None:
            return []

        dist = abs(robot.x - other_bot.x) + abs(robot.y - other_bot.y)

        if dist > HEARING_MAX_DISTANCE:
            self._heard_this_cycle = []
            return []

        volume = max(0.0, HEARING_SONG_VOLUME_BASE - dist * HEARING_SONG_VOLUME_DECAY)

        heard_song = getattr(other_bot, "_last_sang_action", None)

        if heard_song is None:
            self._heard_this_cycle = []
            return []

        self._heard_this_cycle = [(heard_song, volume)]

        self._hearing_sequence.append(heard_song)
        if len(self._hearing_sequence) > 20:
            self._hearing_sequence.pop(0)

        return [(heard_song, volume)]

    def learn_from_hearing(self, robot, action: int, reward: int, other_bot) -> None:
        """
        GL5.1: Aprende de los sonidos escuchados.
        Asocia los sonidos con acciones y resultados.

        Args:
            robot: The hearing robot
            action: Action performed
            reward: Outcome of the action
            other_bot: The bot that was heard
        """
        from constants import HEARING_LEARNING_RATE

        if not self._heard_this_cycle or other_bot is None:
            return

        for heard_song, volume in self._heard_this_cycle:
            perc = self.fuzzy_processor.get_feature_vector(robot.get_state(other_bot))
            perc_id = json.dumps(perc)

            self.memory.add_hearing_memory(
                heard_song=heard_song,
                heard_from_bot=getattr(other_bot, "self_id", 0),
                associated_action=action,
                context_perception=perc_id,
                reward_outcome=reward,
            )

            if volume > 0.3:
                belief_key = f"{heard_song}_{getattr(other_bot, 'self_id', 0)}"
                current = self._song_action_beliefs.get(belief_key, {})
                if action not in current:
                    current[action] = 0
                current[action] = min(
                    1.0, current[action] + volume * HEARING_LEARNING_RATE
                )
                self._song_action_beliefs[belief_key] = current

                self.memory.reinforce_hearing_memory(
                    heard_song, getattr(other_bot, "self_id", 0), reward
                )

    def get_heard_action_association(self, heard_song: str) -> tuple:
        """
        GL5.1: Obtiene la acción más probable asociada con un sonido.

        Args:
            heard_song: The song to look up

        Returns:
            tuple: (action, confidence) or (None, 0.0)
        """
        associations = self.memory.get_song_action_association(heard_song)
        if not associations:
            return (None, 0.0)

        best = max(associations, key=lambda x: x["association_strength"])
        return (best["associated_action"], best["association_strength"])

    def get_hearing_status(self) -> dict:
        """
        GL5.1: Retorna el estado del sistema de audición para display.

        Returns:
            dict: Hearing system status
        """
        heard_memories = self.memory.get_heard_songs(min_strength=0.3)
        return {
            "heard_this_cycle": self._heard_this_cycle,
            "sequence_length": len(self._hearing_sequence),
            "beliefs_count": len(self._song_action_beliefs),
            "total_heard_memories": len(heard_memories),
            "last_sang": self._last_sang_action,
        }

    def sing_for_other(self, robot) -> str:
        """
        GL5.1: El robot "canta" su última acción para que el otro lo oiga.

        Args:
            robot: The robot whose action to sing

        Returns:
            str: The song that was sung
        """
        if hasattr(robot, "_last_sang_action") and robot._last_sang_action:
            return robot._last_sang_action
        return None

    # =========================================================================
    # GL5.1: Imagination Mode (Abstract Reasoning)
    # =========================================================================

    def check_imagination_trigger(self, reward: int) -> bool:
        """
        GL5.1: Verifica si el robot debe entrar en modo imaginación.
        Se activa después de IDLE_THRESHOLD turnos sin reward positivo.

        Args:
            reward: Current reward

        Returns:
            bool: True if imagination mode should activate
        """
        if not self._imagination_enabled:
            return False

        if reward > 0:
            self._idle_counter = 0
            return False

        self._idle_counter += 1
        if self._idle_counter >= IMAGINATION_IDLE_THRESHOLD:
            self._idle_counter = 0
            return True

        return False

    def enter_imagination_mode(self) -> None:
        """
        GL5.1: Entra en modo imaginación.
        El robot reorganiza su conocimiento para crear abstracciones.
        """
        if not self._imagination_enabled:
            return

        self._imagination_mode = True
        self._imagination_cycles = 0
        print(f"Entering imagination mode... (idle for {self._idle_counter} turns)")
        self._idle_counter = 0

    def run_imagination_cycle(self) -> int:
        """
        GL5.1: Ejecuta un ciclo de imaginación.
        Fusiona reglas similares, generaliza patrones, y crea abstracciones.

        Returns:
            int: Number of new productions created
        """
        if not self._imagination_mode:
            return 0

        self._imagination_cycles += 1
        productions_created = 0

        if self._imagination_cycles >= IMAGINATION_CYCLE_DURATION:
            self.exit_imagination_mode()
            return productions_created

        rules = self.memory.get_rules(limit=1000)
        if len(rules) < 5:
            return 0

        # Optimization: Sort and group by action, favoring high-weight rules
        rule_groups = {}
        for r in rules:
            action = r.get("target_action")
            weight = r.get("weight", 0)
            if action is not None and weight > 2.0:  # Increased threshold for quality
                if action not in rule_groups:
                    rule_groups[action] = []
                rule_groups[action].append(r)

        for action, group in rule_groups.items():
            # Sort group by weight descending to favor successful experiences
            group.sort(key=lambda x: x.get("weight", 0), reverse=True)
            
            if len(group) >= 2 and random.random() < IMAGINATION_ABSTRACTION_RATE:
                # Pick one from top 30% and one from rest (for diversity + quality)
                top_idx = random.randint(0, max(0, len(group) // 3))
                r1 = group[top_idx]
                r2 = random.choice(group)
                
                if r1["id"] == r2["id"]:
                    continue

                perc1_raw = r1["perception_pattern"]
                perc2_raw = r2["perception_pattern"]

                if isinstance(perc1_raw, str):
                    try:
                        perc1 = json.loads(perc1_raw)
                    except json.JSONDecodeError:
                        perc1 = {}
                else:
                    perc1 = perc1_raw if perc1_raw else {}

                if isinstance(perc2_raw, str):
                    try:
                        perc2 = json.loads(perc2_raw)
                    except json.JSONDecodeError:
                        perc2 = {}
                else:
                    perc2 = perc2_raw if perc2_raw else {}

                if not isinstance(perc1, dict) or not isinstance(perc2, dict):
                    continue

                common_keys = set(perc1.keys()) & set(perc2.keys())
                if len(common_keys) >= 1:
                    fused_perc = {}
                    for key in common_keys:
                        if perc1.get(key) == perc2.get(key):
                            fused_perc[key] = perc1[key]
                        else:
                            if random.random() < IMAGINATION_GENERALIZATION_RATE:
                                fused_perc[key] = "ANY"

                    if fused_perc:
                        fused_perc_id = json.dumps(fused_perc)
                        confidence = (r1.get("weight", 1) + r2.get("weight", 1)) / 20.0

                        prod_id = self.memory.add_cognitive_production(
                            production_type="ABSTRACTION",
                            name=f"ABSTRACT_A{action}_{len(common_keys)}keys",
                            component_rules=[r1["id"], r2["id"]],
                            abstraction_level=2,
                            confidence=min(1.0, confidence),
                            is_imagined=True,
                            description=f"Fused from 2 rules with {len(common_keys)} common keys",
                        )
                        productions_created += 1
                        self._imagined_productions.append(prod_id)

        sequences = self._detect_action_sequences(rules)
        for seq in sequences:
            if len(seq["actions"]) >= 2 and seq["count"] >= 2:
                prod_id = self.memory.add_cognitive_production(
                    production_type="GENERALIZATION",
                    name=f"PATTERN_{seq['seq_str']}",
                    component_rules=[],
                    abstraction_level=1,
                    confidence=min(1.0, seq["avg_reward"] / 10.0),
                    is_imagined=True,
                    description=f"Action pattern seen {seq['count']} times",
                )
                productions_created += 1
                self._imagined_productions.append(prod_id)

        return productions_created

    def _detect_action_sequences(self, rules: list) -> list:
        """Detects common action sequences from recent history."""
        chrono = []
        try:
            cur = self.memory.conn.cursor()
            cur.execute(
                "SELECT action, reward FROM chrono_memory ORDER BY id DESC LIMIT 50"
            )
            chrono = cur.fetchall()
        except Exception:
            pass

        sequences = {}
        for i in range(len(chrono) - 1):
            action1 = chrono[i][0]
            action2 = chrono[i + 1][0]
            reward = chrono[i][1]
            seq_key = f"{action1}_{action2}"
            if seq_key not in sequences:
                sequences[seq_key] = {"count": 0, "total_reward": 0}
            sequences[seq_key]["count"] += 1
            sequences[seq_key]["total_reward"] += reward

        result = []
        for seq_key, data in sequences.items():
            actions = [int(a) for a in seq_key.split("_")]
            avg_reward = data["total_reward"] / max(1, data["count"])
            result.append(
                {
                    "seq_str": seq_key,
                    "actions": actions,
                    "count": data["count"],
                    "avg_reward": avg_reward,
                }
            )

        return result

    def exit_imagination_mode(self) -> None:
        """
        GL5.1: Sale del modo imaginación.
        """
        self._imagination_mode = False
        print(
            f"Exiting imagination mode. Created {len(self._imagined_productions)} new productions."
        )
        self._imagined_productions = []

    def get_imagination_status(self) -> dict:
        """
        GL5.1: Retorna el estado del modo imaginación para display.

        Returns:
            dict: Imagination mode status
        """
        cog_stats = self.memory.get_cognitive_stats()
        return {
            "enabled": self._imagination_enabled,
            "active": self._imagination_mode,
            "cycles": self._imagination_cycles,
            "idle_counter": self._idle_counter,
            "imagined_this_session": len(self._imagined_productions),
            "total_imagined": cog_stats.get("imagined_productions", 0),
            "total_productions": cog_stats.get("total_productions", 0),
            "avg_confidence": cog_stats.get("avg_confidence", 0),
        }
