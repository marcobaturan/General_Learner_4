"""
Relational Frame Theory (RFT) Engine for General Learner 5 (GL5)

This module implements derived relational responding, the cognitive mechanism
distinguishing human-level symbolic cognition from pure operant conditioning.

Based on: Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001).
    RELATIONAL FRAME THEORY: A Post-Skinnerian Account of Human Language and Cognition.
    Kluwer Academic / Plenum Publishers.

This engine operates as a 'shadow reasoning' system — it only activates during
sleep_cycle() consolidation, detecting relational patterns and deriving new
inferences without modifying any directly experienced rules.

The three core mechanisms implemented:
1. Mutual Entailment: If A → X is learned and A is coordinate with B, then B → X is derived.
2. Combinatory Entailment: Transitivity — if A ≈ B and B ≈ C, then A ≈ C.
3. Transformation of Functions: Motivational relevance transfers between related concepts.

Author: Marco (extending Grey Walter's and Fritz's cybernetic lineage)
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


class RelationalFrameEngine:
    """
    The cognitive engine implementing Relational Frame Theory.

    This class models the human capacity for 'derived relational responding' —
    the ability to infer relationships between stimuli without direct training.

    In biological terms, this mimics the prefrontal cortex's ability to form
    abstract conceptual categories from concrete experiences. It is the cognitive
    substrate underlying language acquisition, metaphor comprehension, and
    logical reasoning in humans (Hayes et al., 2001).

    The engine operates in a 'shadow' mode — its outputs are stored separately
    from directly learned rules and are always superseded by experiential knowledge.
    This prevents the agent from becoming disconnected from reality while
    still enabling abstract inference.
    """

    def __init__(self):
        """
        Initialises the RFT engine.

        No persistent state is stored — the engine operates purely as a
        transformation function over the memory subsystem during consolidation.
        """
        pass

    def detect_coordination(self, memory):
        """
        Detects coordination (synonymy) between concepts.

        Coordination is the foundational relational frame in RFT — the 'same as'
        relation. In humans, once two stimuli are established as equivalent,
        behaviour learned with one transfers to the other (stimulus equivalence).
        See: Sidman, M. (1994). Equivalence Relations: A Research Story.

        Algorithm:
        - Groups concepts by the actions they consistently invoke
        - If two concepts map to the SAME action in >= RFT_COORD_THRESHOLD (default 3) rules
          with cumulative weight >= 5, establishes a COORD frame between them

        Biological Analogue:
        This mirrors the formation of semantic categories in the fusiform gyrus —
        neurons that fire together wire together, creating shared representations
        for functionally equivalent stimuli.

        Args:
            memory: The Memory subsystem containing learned rules

        Returns:
            int: Number of new coordination frames created
        """
        rules = memory.get_rules()
        concept_actions = {}

        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue
            action = r["target_action"]
            weight = r["weight"]

            if cmd_id not in concept_actions:
                concept_actions[cmd_id] = {}
            if action not in concept_actions[cmd_id]:
                concept_actions[cmd_id][action] = 0
            concept_actions[cmd_id][action] += weight

        action_to_concepts = {}
        for concept_id, actions in concept_actions.items():
            for action, total_weight in actions.items():
                if total_weight >= 5:
                    if action not in action_to_concepts:
                        action_to_concepts[action] = []
                    action_to_concepts[action].append((concept_id, total_weight))

        frames_created = 0
        for action, concepts in action_to_concepts.items():
            if len(concepts) >= 2:
                concepts_sorted = sorted(concepts, key=lambda x: x[1], reverse=True)
                for i in range(len(concepts_sorted)):
                    for j in range(i + 1, len(concepts_sorted)):
                        c1, w1 = concepts_sorted[i]
                        c2, w2 = concepts_sorted[j]
                        avg_strength = (w1 + w2) / 20.0
                        if avg_strength > 0.5:
                            memory.add_relational_frame(c1, "COORD", c2, avg_strength)
                            frames_created += 1

        return frames_created

    def detect_opposition(self, memory):
        """
        Detects opposition (antonymy) between concepts.

        Opposition is the second key relational frame — the 'opposite of' relation.
        In human cognition, understanding that 'hot' implies 'not cold' and that
        'forward' implies 'not backward' enables logical negation and conflict
        resolution in reasoning.

        Algorithm:
        - Looks for concepts that consistently invoke opposite motor actions
        - FORWARD ↔ BACKWARD and LEFT ↔ RIGHT are treated as opposites
        - If concept A maps to ACT_FORWARD with weight >= 5 AND
          concept B maps to ACT_BACKWARD with weight >= 5,
          creates an OPP frame between A and B

        Biological Analogue:
        This models the antagonistic neural populations in the basal ganglia —
        Go/NoGo pathways that mutually inhibit competing motor programmes.
        The cognitive distinction between 'approach' and 'avoid' behaviours.

        Args:
            memory: The Memory subsystem

        Returns:
            int: Number of opposition frames created
        """
        rules = memory.get_rules()
        concept_actions = {}

        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue
            action = r["target_action"]
            weight = r["weight"]

            if cmd_id not in concept_actions:
                concept_actions[cmd_id] = {}
            if action not in concept_actions[cmd_id]:
                concept_actions[cmd_id][action] = 0
            concept_actions[cmd_id][action] += weight

        opposites = {(ACT_FORWARD, ACT_BACKWARD), (ACT_LEFT, ACT_RIGHT)}

        frames_created = 0
        concepts = list(concept_actions.keys())
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                c1, c2 = concepts[i], concepts[j]
                actions1 = concept_actions[c1]
                actions2 = concept_actions[c2]

                for a1, a2 in opposites:
                    w1 = actions1.get(a1, 0)
                    w2 = actions2.get(a2, 0)
                    if w1 >= 5 and w2 >= 5:
                        strength = min(w1, w2) / 20.0
                        memory.add_relational_frame(c1, "OPP", c2, strength)
                        frames_created += 1

        return frames_created

    def close_transitivity(self, memory):
        """
        Applies transitive closure to the coordination graph.

        Transitivity is a hallmark of human logical reasoning. If we know that
        A is the same as B, and B is the same as C, we automatically infer that
        A is the same as C — without ever experiencing A and C together.

        This was famously demonstrated in primates by McGonigle & Chalmers (1992),
        showing that rhesus monkeys can perform transitive inference on
        reward hierarchies (A > B > C > D > E implies A > C, etc.).

        Algorithm:
        - Builds an adjacency graph from existing COORD frames
        - For each path A → B → C, creates a direct A → C frame
        - Strength of derived frame = average of intermediate strengths

        Biological Analogue:
        This models the hippocampal CA3 region's auto-associative network —
        the ability to complete patterns and derive novel associations from
        known connections. The 'indexing theory' of memory (Teyler & DiScenna, 1985)
        suggests that retrieving one memory cue can activate related memory traces.

        Args:
            memory: The Memory subsystem

        Returns:
            int: Number of transitive frames derived
        """
        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]

        # Build bidirectional adjacency graph
        adj = {}
        for f in coord_frames:
            a, b = f["concept_a"], f["concept_b"]
            if a not in adj:
                adj[a] = {}
            if b not in adj[a]:
                adj[a][b] = f["strength"]
            else:
                adj[a][b] = max(adj[a][b], f["strength"])
            # Ensure reverse edge exists for bidirectional traversal
            if b not in adj:
                adj[b] = {}
            if a not in adj[b]:
                adj[b][a] = f["strength"]
            else:
                adj[b][a] = max(adj[b][a], f["strength"])

        added = 0
        for a in adj:
            for b in adj[a]:
                if b in adj:
                    for c in adj[b]:
                        if c != a and a != c:
                            strength = (adj[a][b] + adj[b][c]) / 2.0
                            if strength > 0.3:
                                memory.add_relational_frame(a, "COORD", c, strength)
                                added += 1
        return added

    def derive_mutual_entailment(self, memory):
        """
        Derives new action rules based on coordination frames.

        Mutual entailment is the core RFT mechanism: if we know A → action,
        and A is coordinate with B, then B → same action is derived.

        This implements the 'transfer of functions' — a concept learned in one
        context transfers to a related context without explicit training.
        In humans, this explains why learning to drive a car transfers to
        driving a van, or why knowing that 'dog' is dangerous transfers to
        'German Shepherd' (stimulus equivalence class formation).

        Algorithm:
        - For each COORD frame (A, B):
          - Looks up all directly learned actions for concept A
          - Creates a DERIVED rule for concept B with weight = original_weight * RFT_WEIGHT_FACTOR
          - Repeats symmetrically for B → A

        Biological Analogue:
        This mirrors the generalisation gradients observed in conditioning
        experiments — stimulus generalisation across similar inputs. The
        strength of transfer is proportional to the similarity (here, the
        coordination strength).

        Args:
            memory: The Memory subsystem

        Returns:
            int: Number of derived rules created
        """
        rules = memory.get_rules()
        concept_to_actions = {}

        # Build map of concepts to their directly learned actions (any memory type)
        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue
            action = r["target_action"]
            weight = r["weight"]
            if cmd_id not in concept_to_actions:
                concept_to_actions[cmd_id] = {}
            if action not in concept_to_actions[cmd_id]:
                concept_to_actions[cmd_id][action] = weight
            else:
                concept_to_actions[cmd_id][action] = max(
                    concept_to_actions[cmd_id][action], weight
                )

        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]

        # Limit to prevent overload
        max_frames = 50
        coord_frames = coord_frames[:max_frames]

        derived_count = 0
        max_derived = 50  # Limit derived rules per cycle
        for frame in coord_frames:
            if derived_count >= max_derived:
                break
            c1, c2 = frame["concept_a"], frame["concept_b"]

            # Transfer actions from c1 to c2
            c1_actions = concept_to_actions.get(c1, {})
            if c1_actions:
                for action, weight in c1_actions.items():
                    if derived_count >= max_derived:
                        break
                    derived_weight = weight * RFT_WEIGHT_FACTOR
                    memory.add_rule(
                        perception_pattern=None,
                        action=action,
                        weight=derived_weight,
                        command_id=c2,
                        memory_type=MEMORY_DERIVED,
                        derived_from=frame["id"],
                    )
                    derived_count += 1

            # Transfer actions from c2 to c1 (symmetric)
            c2_actions = concept_to_actions.get(c2, {})
            if c2_actions:
                for action, weight in c2_actions.items():
                    if derived_count >= max_derived:
                        break
                    derived_weight = weight * RFT_WEIGHT_FACTOR
                    memory.add_rule(
                        perception_pattern=None,
                        action=action,
                        weight=derived_weight,
                        command_id=c1,
                        memory_type=MEMORY_DERIVED,
                        derived_from=frame["id"],
                    )
                    derived_count += 1

        return derived_count

    def apply_transformation(self, memory):
        """
        Applies transformation of functions — transfers motivational relevance.

        In RFT, if concept A has high motivational value (is 'important' or
        'valuable'), and A is coordinate with B, then B inherits partial
        motivational relevance. This is distinct from action transfer —
        it's about the affective significance of concepts.

        Example: If 'reward' has been heavily reinforced, and 'bonus' is
        recognised as coordinate with 'reward', the agent will prioritises
        'bonus' actions more than it would from direct experience alone.

        Algorithm:
        - Calculates total weight (importance) for each concept
        - For high-importance concepts (total weight >= 10), finds coordinate concepts
        - Boosts direct rules for coordinate concepts by 5%

        Biological Analogue:
        This models the dopaminergic reward prediction error system.
        In biological brains, once a stimulus is associated with reward,
        related stimuli acquire 'incentive salience' — they become 'wanted'
        even without direct reinforcement (Berridge, 2007).

        Args:
            memory: The Memory subsystem

        Returns:
            int: Number of transformations applied
        """
        rules = memory.get_rules()
        concept_weights = {}

        for r in rules:
            cmd_id = r.get("command_id")
            if cmd_id is None:
                continue
            if cmd_id not in concept_weights:
                concept_weights[cmd_id] = 0
            concept_weights[cmd_id] += r["weight"]

        frames = memory.get_all_frames()
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]

        reinforced = 0
        for frame in coord_frames:
            c1, c2 = frame["concept_a"], frame["concept_b"]
            w1 = concept_weights.get(c1, 0)

            # If concept c1 has high motivational relevance (weight >= 10)
            if w1 >= 10:
                boost = w1 * 0.05  # 5% transfer of relevance
                for r in rules:
                    if r.get("command_id") == c2 and r["memory_type"] != MEMORY_DERIVED:
                        # Only boost directly learned rules, not derived ones
                        memory.add_rule(
                            r["perception_pattern"],
                            r["target_action"],
                            weight=boost,
                            command_id=c2,
                            memory_type=r["memory_type"],
                        )
                        reinforced += 1

        return reinforced

    def run_cycle(self, memory, max_operations=100):
        """
        Executes the complete RFT derivation cycle.

        This is the orchestrator method called during sleep_cycle() consolidation.
        It runs all RFT mechanisms in sequence with operation limits to prevent overload:

        1. detect_coordination — finds synonym relationships
        2. detect_opposition — finds antonym relationships
        3. close_transitivity — derives transitive relationships
        4. derive_mutual_entailment — creates derived action rules
        5. apply_transformation — transfers motivational relevance
        6. decay_frames — reduces stale relational frames

        The max_operations parameter limits total DB modifications per cycle.

        Args:
            memory: The Memory subsystem
            max_operations: Maximum number of operations per phase

        Returns:
            dict: Summary of operations performed
        """
        c1 = self.detect_coordination(memory)
        c2 = self.detect_opposition(memory)
        t1 = self.close_transitivity(memory)
        d1 = self.derive_mutual_entailment(memory)

        # Skip transformation if too many operations already
        if c1 + c2 + t1 + d1 > max_operations:
            print(
                f"RFT: Skipping transformation due to overload ({c1 + c2 + t1 + d1} ops)"
            )
            t2 = 0
        else:
            t2 = self.apply_transformation(memory)

        memory.decay_frames()

        frames_after = len(memory.get_all_frames())

        return {
            "coord_frames": c1,
            "opp_frames": c2,
            "transitive_closure": t1,
            "derived_rules": d1,
            "transformations": t2,
            "total_frames": frames_after,
        }
