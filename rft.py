"""
################################################################################
#                                                                              #
#      _____  ______ _______                                                   #
#     |  __ \|  ____|__   __|                                                  #
#     | |__) | |__     | |                                                     #
#     |  _  /|  __|    | |                                                     #
#     | | \ \| |       | |                                                     #
#     |_|  \_\_|       |_|                                                     #
#                                                                              #
#      ______ _   _  _____ _____ _   _ ______                                  #
#     |  ____| \ | |/ ____|_   _| \ | |  ____|                                 #
#     | |__  |  \| | |  __  | | |  \| | |__                                    #
#     |  __| | . ` | | |_ | | | | . ` |  __|                                   #
#     | |____| |\  | |__| |_| |_| |\  | |____                                  #
#     |______|_| \_|\_____|_____|_| \_|______|                                 #
#                                                                              #
################################################################################

RELATIONAL FRAME THEORY (RFT) ENGINE
====================================

This module implements derived relational responding, the cognitive mechanism 
that enables language and symbolic cognition. It is the core reason why 
GL5 can understand "GO" if it only learned "AVANZA" (given they are COORD).

SCIENTIFIC FOUNDATIONS:
-----------------------
1. RELATIONAL FRAME THEORY (RFT):
   Based on Hayes, Barnes-Holmes, and Roche (2001). RFT is a post-Skinnerian 
   account of human language and cognition.
   Ref: Hayes, S. C. et al. (2001). Relational Frame Theory.

2. CORE RELATIONAL PROCESSES:
   - MUTUAL ENTAILMENT: If A relates to B, then B relates to A.
   - COMBINATORY ENTAILMENT: If A relates to B and B to C, then A relates to C.
   - TRANSFORMATION OF FUNCTIONS: If A is a goal, and A is like B, then B 
     becomes a goal.

3. OPTIMIZED COGNITIVE PROCESSING:
   Implements a performance-optimized version of the RFT engine to run 
   during the 'Sleep Cycle' without exhausting computational resources.

Author: Marco
"""

import json
from constants import (
    MEMORY_DERIVED,
    RFT_WEIGHT_FACTOR,
    RFT_COORD_THRESHOLD,
    ACT_FORWARD,
    ACT_BACKWARD,
    ACT_LEFT,
    ACT_RIGHT,
)

# ================================================================================
# PERFORMANCE LIMITS - Tune these for speed vs. completeness
# ================================================================================

MAX_COORD_FRAMES = 30  # Max frames created per cycle
MAX_OPP_FRAMES = 20  # Max opposition frames
MAX_TRANSITIVE_FRAMES = 50  # Max transitive closures
MAX_DERIVED_RULES = 25  # Max rules derived from frames
MAX_TRANSFORMATIONS = 30  # Max motivational boosts
MAX_RULES_TO_PROCESS = 200  # Max rules to load per cycle
EARLY_STOP_ON_OVERLOAD = True  # Skip remaining phases if overloaded


class RelationalFrameEngine:
    """
    ############################################################################
    #   _____  ______ _______                                                  #
    #  |  __ \|  ____|__   __|                                                 #
    #  | |__) | |__     | |                                                    #
    #  |  _  /|  __|    | |                                                    #
    #  | | \ \| |       | |                                                    #
    #  |_|  \_\_|       |_|                                                    #
    ############################################################################

    The cognitive engine implementing Relational Frame Theory.

    THE THREE CORE MECHANISMS:
    ---------------------------
    1. MUTUAL ENTAILMENT: Symmetric transfer of meaning.
    2. COMBINATORY ENTAILMENT: Logical inference (transitivity).
    3. TRANSFORMATION OF FUNCTIONS: Inheritance of reinforcement value.
    """

    def __init__(self):
        """
        Initialize the RFT engine with empty caches.

        The engine is stateless - it operates purely as a transformation
        function over the memory subsystem during consolidation.
        """
        self._cache = {}
        self._last_run_stats = None

    def _get_cached_rules(self, memory, force_refresh=False):
        """
        Get rules from memory with caching to avoid repeated queries.

        This is a major optimization: instead of querying the database
        multiple times per cycle, we cache the results.

        Args:
            memory: Memory subsystem
            force_refresh: Force reload even if cached

        Returns:
            list: Cached rules
        """
        cache_key = id(memory)
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        rules = memory.get_rules(limit=MAX_RULES_TO_PROCESS)
        self._cache[cache_key] = rules
        return rules

    def _build_concept_maps(self, rules):
        """
        Build hash maps for O(1) concept lookups.

        Instead of iterating through all rules for each concept,
        we build lookup tables once and reuse them.

        Args:
            rules: List of rule dictionaries

        Returns:
            tuple: (concept_to_actions, concept_weights, concept_texts)
        """
        concept_to_actions = {}
        concept_weights = {}
        concept_texts = {}

        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue

            action = r["target_action"]
            weight = r["weight"]
            cmd_text = r.get("command_text", "")

            # Track concept -> actions mapping
            if cmd_id not in concept_to_actions:
                concept_to_actions[cmd_id] = {}
                concept_texts[cmd_id] = cmd_text

            if action not in concept_to_actions[cmd_id]:
                concept_to_actions[cmd_id][action] = weight
            else:
                concept_to_actions[cmd_id][action] = max(
                    concept_to_actions[cmd_id][action], weight
                )

            # Track total concept weight (for transformation of functions)
            if cmd_id not in concept_weights:
                concept_weights[cmd_id] = 0
            concept_weights[cmd_id] += weight

        return concept_to_actions, concept_weights, concept_texts

    def detect_coordination(self, memory):
        """
        =========================================================================
        DETECT COORDINATION (SYNONYMY) - OPTIMIZED
        =========================================================================

        Finds pairs of concepts that invoke the SAME action, indicating they
        are functionally equivalent (coordinate/synonymous).

        Algorithm (Optimized):
        ----------------------
        1. Build concept->actions map (O(n) once)
        2. Invert to action->concepts (O(m) where m = actions)
        3. For each action, pair concepts and create frames (O(k²) for k concepts)
        4. Limit to top N pairs by strength

        Performance: O(n + m + k²) instead of O(n × m)

        Args:
            memory: Memory subsystem

        Returns:
            int: Number of coordination frames created (max MAX_COORD_FRAMES)
        """
        rules = self._get_cached_rules(memory)
        concept_maps = self._build_concept_maps(rules)
        concept_to_actions = concept_maps[0]
        concept_texts = concept_maps[2]

        # Invert: action -> [(concept, weight), ...]
        action_to_concepts = {}
        for concept_id, actions in concept_to_actions.items():
            for action, total_weight in actions.items():
                # Only consider significant associations
                if total_weight >= 3:
                    if action not in action_to_concepts:
                        action_to_concepts[action] = []
                    action_to_concepts[action].append((concept_id, total_weight))

        frames_created = 0

        # Process each action's concept pairs
        for action, concepts in action_to_concepts.items():
            if frames_created >= MAX_COORD_FRAMES:
                break

            if len(concepts) < 2:
                continue

            # Sort by weight descending (greedy - take best first)
            concepts_sorted = sorted(concepts, key=lambda x: x[1], reverse=True)

            # Only consider top 5 concepts per action to limit pairs
            for c1, w1 in concepts_sorted[:5]:
                if frames_created >= MAX_COORD_FRAMES:
                    break

                for c2, w2 in concepts_sorted[5:]:
                    if frames_created >= MAX_COORD_FRAMES:
                        break
                    if c1 == c2:
                        continue

                    avg_strength = (w1 + w2) / 20.0

                    # Boost SELF connections
                    t1 = concept_texts.get(c1, "").lower()
                    t2 = concept_texts.get(c2, "").lower()
                    if "self_" in t1 or "self_" in t2:
                        avg_strength = min(1.0, avg_strength * 1.5)

                    if avg_strength > 0.3:
                        memory.add_relational_frame(c1, "COORD", c2, avg_strength)
                        frames_created += 1

        return frames_created

    def detect_opposition(self, memory):
        """
        =========================================================================
        DETECT OPPOSITION (ANTONYMY) - OPTIMIZED
        =========================================================================

        Finds pairs of concepts that invoke OPPOSITE actions (FORWARD/BACKWARD,
        LEFT/RIGHT), indicating antonymous relations.

        Algorithm: O(n) instead of O(n²)

        Args:
            memory: Memory subsystem

        Returns:
            int: Number of opposition frames created (max MAX_OPP_FRAMES)
        """
        rules = self._get_cached_rules(memory)
        concept_maps = self._build_concept_maps(rules)
        concept_to_actions = concept_maps[0]
        concept_texts = concept_maps[2]

        opposites = [(ACT_FORWARD, ACT_BACKWARD), (ACT_LEFT, ACT_RIGHT)]
        frames_created = 0

        concept_ids = list(concept_to_actions.keys())

        # O(m × c²) where m = opposite pairs, c = concepts
        for a1, a2 in opposites:
            if frames_created >= MAX_OPP_FRAMES:
                break

            for i, c1 in enumerate(concept_ids):
                if frames_created >= MAX_OPP_FRAMES:
                    break

                actions1 = concept_to_actions.get(c1, {})

                for c2_id in concept_ids[i + 1 :]:
                    if frames_created >= MAX_OPP_FRAMES:
                        break

                    actions2 = concept_to_actions.get(c2_id, {})

                    w1 = actions1.get(a1, 0)
                    w2 = actions2.get(a2, 0)

                    # Threshold: lower for SELF concepts
                    t1 = (concept_texts.get(c1) or "").lower()
                    t2 = (concept_texts.get(c2_id) or "").lower()
                    threshold = 3 if "self_" in t1 or "self_" in t2 else 5

                    if w1 >= threshold and w2 >= threshold:
                        strength = min(w1, w2) / 20.0
                        memory.add_relational_frame(c1, "OPP", c2_id, strength)
                        frames_created += 1

        return frames_created

    def detect_deictic_relations(self, memory):
        """
        =========================================================================
        DETECT DEICTIC RELATIONS (SELF-OTHER) - NEW
        =========================================================================
        Implements deictic framing (I-YOU, HERE-THERE). 
        Essential for social perspective taking and Theory of Mind.
        """
        rules = self._get_cached_rules(memory)
        _, _, concept_texts = self._build_concept_maps(rules)
        
        self_id = None
        other_id = None
        
        for cid, text in concept_texts.items():
            if "self" in text.lower(): self_id = cid
            if "other" in text.lower() or "bot" in text.lower(): other_id = cid
            
        if self_id and other_id:
            # Create a deictic frame (Distinction/Opposition in perspective)
            memory.add_relational_frame(self_id, "OPP", other_id, 0.9)
            return 1
        return 0

    def close_opposition_combinatorial(self, memory):
        """
        =========================================================================
        COMBINATORIAL ENTAILMENT FOR OPPOSITION - NEW
        =========================================================================
        If A is opposite to B, and B is opposite to C, then A is coordinate to C.
        (The enemy of my enemy is my friend).
        """
        frames = memory.get_all_frames()
        opp_frames = [f for f in frames if f["relation_type"] == "OPP"]
        
        if len(opp_frames) < 2: return 0
        
        added = 0
        # Build adjacency for opposition
        opp_map = {}
        for f in opp_frames:
            a, b = f["concept_a"], f["concept_b"]
            if a not in opp_map: opp_map[a] = set()
            if b not in opp_map: opp_map[b] = set()
            opp_map[a].add(b)
            opp_map[b].add(a)
            
        for a in opp_map:
            for b in opp_map[a]:
                for c in opp_map.get(b, []):
                    if a != c:
                        # Combinatorial Entailment: OPP + OPP -> COORD
                        memory.add_relational_frame(a, "COORD", c, 0.7)
                        added += 1
                        if added >= MAX_TRANSITIVE_FRAMES: return added
        return added

    def derive_mutual_entailment(self, memory):
        """
        =========================================================================
        MUTUAL ENTAILMENT (ACTION TRANSFER) - OPTIMIZED
        =========================================================================

        If concept A → action X and A ≈ B, then B → X.

        This is the core RFT mechanism for derived learning:
        knowledge transfers between related concepts.

        Optimization: Uses cached concept maps, limits frames processed,
        early termination on overload.

        Args:
            memory: Memory subsystem

        Returns:
            int: Number of derived rules created (max MAX_DERIVED_RULES)
        """
        rules = self._get_cached_rules(memory)
        concept_maps = self._build_concept_maps(rules)
        concept_to_actions = concept_maps[0]
        concept_texts = concept_maps[2]

        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]

        derived_count = 0

        # Limit frames to process
        for frame in coord_frames[:MAX_COORD_FRAMES]:
            if derived_count >= MAX_DERIVED_RULES:
                break

            c1, c2 = frame["concept_a"], frame["concept_b"]
            strength = frame["strength"]

            # Weight factor: higher for SELF frames
            t1 = concept_texts.get(c1, "").lower()
            t2 = concept_texts.get(c2, "").lower()
            weight_factor = (
                RFT_WEIGHT_FACTOR * 1.5
                if "self_" in t1 or "self_" in t2
                else RFT_WEIGHT_FACTOR
            )

            # Transfer actions c1 -> c2
            c1_actions = concept_to_actions.get(c1, {})
            for action, weight in c1_actions.items():
                if derived_count >= MAX_DERIVED_RULES:
                    break

                derived_weight = weight * weight_factor * strength
                memory.add_rule(
                    perception_pattern=None,
                    action=action,
                    weight=derived_weight,
                    command_id=c2,
                    memory_type=MEMORY_DERIVED,
                    derived_from=frame.get("id"),
                )
                derived_count += 1

            # Transfer actions c2 -> c1 (symmetric)
            if derived_count >= MAX_DERIVED_RULES:
                break

            c2_actions = concept_to_actions.get(c2, {})
            for action, weight in c2_actions.items():
                if derived_count >= MAX_DERIVED_RULES:
                    break

                derived_weight = weight * weight_factor * strength
                memory.add_rule(
                    perception_pattern=None,
                    action=action,
                    weight=derived_weight,
                    command_id=c1,
                    memory_type=MEMORY_DERIVED,
                    derived_from=frame.get("id"),
                )
                derived_count += 1

        return derived_count

    def apply_transformation(self, memory):
        """
        =========================================================================
        TRANSFORMATION OF FUNCTIONS (MOTIVATIONAL TRANSFER) - OPTIMIZED
        =========================================================================

        If concept A has high value and A ≈ B, then B inherits partial value.

        This models how motivation transfers between related concepts without
        direct reinforcement (e.g., "bonus" inherits incentive value of "reward").

        Optimization: Only processes high-value concepts, limits boosts.

        Args:
            memory: Memory subsystem

        Returns:
            int: Number of transformations applied (max MAX_TRANSFORMATIONS)
        """
        rules = self._get_cached_rules(memory)
        concept_maps = self._build_concept_maps(rules)
        concept_weights = concept_maps[1]

        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]

        reinforced = 0

        # Only high-value concepts transfer motivation
        high_value_concepts = {
            c: w
            for c, w in concept_weights.items()
            if w >= 10  # Threshold for "important" concept
        }

        for frame in coord_frames:
            if reinforced >= MAX_TRANSFORMATIONS:
                break

            c1, c2 = frame["concept_a"], frame["concept_b"]
            w1 = high_value_concepts.get(c1, 0)
            w2 = high_value_concepts.get(c2, 0)

            # Transfer from high-value to related concept
            source = c1 if w1 >= 10 else (c2 if w2 >= 10 else None)
            target = c2 if source == c1 else c1

            if source and reinforced < MAX_TRANSFORMATIONS:
                boost = w1 * 0.05 if source == c1 else w2 * 0.05

                for r in rules:
                    if reinforced >= MAX_TRANSFORMATIONS:
                        break
                    if (
                        r.get("command_id") == target
                        and r.get("memory_type") != MEMORY_DERIVED
                    ):
                        memory.add_rule(
                            r["perception_pattern"],
                            r["target_action"],
                            weight=boost,
                            command_id=target,
                            memory_type=r["memory_type"],
                        )
                        reinforced += 1

        return reinforced

    def run_cycle(self, memory, max_operations=100):
        """
        =========================================================================
        MAIN RFT CYCLE - OPTIMIZED WITH EARLY TERMINATION
        =========================================================================

        Executes the complete RFT derivation cycle with operation limits.

        If EARLY_STOP_ON_OVERLOAD is True and a phase exceeds its limit,
        subsequent phases are skipped to ensure bounded execution time.

        Execution Order:
        ----------------
        1. Coordination detection (synonyms)
        2. Opposition detection (antonyms)
        3. Transitive closure (A≈B, B≈C → A≈C)
        4. Mutual entailment (action transfer)
        5. Transformation of functions (motivation transfer)
        6. Frame decay

        Args:
            memory: Memory subsystem
            max_operations: Deprecated, kept for compatibility

        Returns:
            dict: Summary of operations performed
        """
        import time

        start_time = time.time()

        # Force cache refresh
        self._get_cached_rules(memory, force_refresh=True)

        total_ops = 0
        overloaded = False

        # Phase 1: Coordination & Deictics
        coord_count = self.detect_coordination(memory)
        deictic_count = self.detect_deictic_relations(memory)
        total_ops += (coord_count + deictic_count)

        if EARLY_STOP_ON_OVERLOAD and coord_count >= MAX_COORD_FRAMES:
            overloaded = True

        # Phase 2: Opposition (skip if overloaded)
        opp_count = 0
        if not overloaded:
            opp_count = self.detect_opposition(memory)
            opp_comb_count = self.close_opposition_combinatorial(memory)
            total_ops += (opp_count + opp_comb_count)

        # Phase 3: Transitive closure (skip if overloaded)
        trans_count = 0
        if not overloaded:
            trans_count = self.close_transitivity(memory)
            total_ops += trans_count

            if EARLY_STOP_ON_OVERLOAD and trans_count >= MAX_TRANSITIVE_FRAMES:
                overloaded = True

        # Phase 4: Mutual entailment (skip if overloaded)
        derived_count = 0
        if not overloaded:
            derived_count = self.derive_mutual_entailment(memory)
            total_ops += derived_count

            if EARLY_STOP_ON_OVERLOAD and derived_count >= MAX_DERIVED_RULES:
                overloaded = True

        # Phase 5: Transformation of functions (skip if overloaded)
        transform_count = 0
        if not overloaded:
            transform_count = self.apply_transformation(memory)

        # Phase 6: Frame decay
        memory.decay_frames()

        # Get final frame count
        frames_after = len(memory.get_all_frames())

        elapsed = time.time() - start_time

        self._last_run_stats = {
            "coord_frames": coord_count,
            "opp_frames": opp_count,
            "transitive_closure": trans_count,
            "derived_rules": derived_count,
            "transformations": transform_count,
            "total_frames": frames_after,
            "elapsed_ms": round(elapsed * 1000, 2),
            "overloaded": overloaded,
        }

        return self._last_run_stats

    def get_last_stats(self):
        """Get statistics from last run cycle."""
        return self._last_run_stats

    def close_transitivity(self, memory):
        """
        =========================================================================
        COMBINATORIAL ENTAILMENT (TRANSITIVITY) - GL5
        =========================================================================
        If concept A is COORD to B, and B is COORD to C, then A is COORD to C.
        """
        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]
        
        if len(coord_frames) < 2:
            return 0
            
        added = 0
        # Build adjacency for coordination
        adj = {}
        for f in coord_frames:
            a, b = f["concept_a"], f["concept_b"]
            if a not in adj: adj[a] = set()
            if b not in adj: adj[b] = set()
            adj[a].add((b, f["strength"]))
            adj[b].add((a, f["strength"]))
            
        # One-step transitivity
        for a in adj:
            for b, s1 in adj[a]:
                for c, s2 in adj.get(b, []):
                    if a != c:
                        strength = s1 * s2 * 0.9  # Slight decay
                        if strength > 0.3:
                            memory.add_relational_frame(a, "COORD", c, strength)
                            added += 1
                            if added >= MAX_TRANSITIVE_FRAMES:
                                return added
        return added

    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
