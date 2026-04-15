"""
################################################################################
#                                                                              #
#      ______ _    _ _____ ______     __                                       #
#     |  ____| |  | |__   __|___  \    \ \                                     #
#     | |__  | |  | |  | |     / /      \ \                                    #
#     |  __| | |  | |  | |    / /        \ \                                   #
#     | |    | |__| |  | |   / /____      \ \                                  #
#     |_|     \____/   |_|  /_______|      \_\                                 #
#                                                                              #
#      ______ _   _  _____ _____ _   _ ______                                  #
#     |  ____| \ | |/ ____|_   _| \ | |  ____|                                 #
#     | |__  |  \| | |  __  | | |  \| | |__                                    #
#     |  __| | . ` | | |_ | | | | . ` |  __|                                   #
#     | |____| |\  | |__| |_| |_| |\  | |____                                  #
#     |______|_| \_|\_____|_____|_| \_|______|                                 #
#                                                                              #
################################################################################

FUZZY INFERENCE ENGINE - THE COGNITIVE REASONER
===============================================

This module implements Zadeh's (1965) Fuzzy Logic for handling perceptual 
uncertainty and relational reasoning in GL5.

SCIENTIFIC FOUNDATIONS:
-----------------------
1. FUZZY SET THEORY:
   Based on Lotfi Zadeh (1965). Instead of boolean logic (True/False), 
   concepts are defined by 'degrees of membership' [0, 1].
   Ref: Zadeh, L. A. (1965). Fuzzy Sets. Information and Control.

2. MAMDANI & SUGENO INFERENCE:
   Implements the two primary modes of fuzzy reasoning:
   - MAMDANI: Interpretable linguistic rules (IF Near AND Fast THEN Turn).
   - SUGENO: Efficient mathematical outputs for motor control.

3. COGNITIVE RELATIONS:
   Enables the 'Fuzzy RFT' layer where relationships between concepts 
   (e.g., A is SIMILAR to B) are treated as continuous strengths.

4. ADAPTIVE MEMBERSHIP:
   The engine can adjust its 'Linguistic Terms' (Near, Far, Medium) 
   based on the distribution of experienced sensory data.

Author: Marco
"""

import math
import random
from collections import defaultdict


class FuzzyMembership:
    """
    ############################################################################
    #   __  __ ______ __  __  ____  _____                                      #
    #  |  \/  |  ____|  \/  |/ __ \|  __ \                                     #
    #  | \  / | |__  | \  / | |  | | |__) |                                    #
    #  | |\/| |  __| | |\/| | |  | |  _  /                                     #
    #  | |  | | |____| |  | | |__| | | \ \                                     #
    #  |_|  |_|______|_|  |_|\____/|_|  \_\                                    #
    ############################################################################

    Collection of advanced membership functions for fuzzy sets.

    These functions define how raw sensory inputs map to linguistic 
    variables. This mimics the 'feature extraction' of the biological 
    sensory cortex.
    """

    @staticmethod
    def triangular(x, a, b, c):
        """Triangular membership function."""
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        if b < x < c:
            return (c - x) / (c - b) if c != b else 1.0
        return 0.0

    @staticmethod
    def trapezoidal(x, a, b, c, d):
        """Trapezoidal membership function."""
        if x <= a or x >= d:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        if b < x <= c:
            return 1.0
        if c < x < d:
            return (d - x) / (d - c) if d != c else 1.0
        return 0.0

    @staticmethod
    def gaussian(x, c, sigma):
        """Gaussian (bell curve) membership function."""
        if sigma == 0:
            return 1.0 if x == c else 0.0
        return math.exp(-0.5 * ((x - c) / sigma) ** 2)

    @staticmethod
    def gaussian_complement(x, c, sigma):
        """Complement of Gaussian (NOT very X)."""
        return 1.0 - FuzzyMembership.gaussian(x, c, sigma)

    @staticmethod
    def bell(x, a, b, c):
        """Generalized bell membership function.

        a: width
        b: slope
        c: center
        """
        return 1.0 / (1.0 + ((x - c) / a) ** (2 * b))

    @staticmethod
    def sigmoid(x, c, a):
        """Sigmoid membership function."""
        return 1.0 / (1.0 + math.exp(-a * (x - c)))

    @staticmethod
    def dsigmoid(x, c1, a1, c2, a2):
        """Difference of two sigmoids (looks like a hill)."""
        return max(
            0.0, FuzzyMembership.sigmoid(x, c1, a1) - FuzzyMembership.sigmoid(x, c2, a2)
        )

    @staticmethod
    def s_function(x, a, b):
        """S-shaped curve from 0 to 1."""
        if x <= a:
            return 0.0
        if x >= b:
            return 1.0
        if a < x < (a + b) / 2:
            t = (x - a) / ((b - a) / 2)
            return t * t
        else:
            t = (x - (a + b) / 2) / ((b - a) / 2)
            return 1.0 - (1.0 - t) * (1.0 - t)

    @staticmethod
    def z_function(x, a, b):
        """Z-shaped curve from 1 to 0 (complement of S)."""
        return 1.0 - FuzzyMembership.s_function(x, a, b)


class FuzzyRelation:
    """
    Represents a fuzzy relation with continuous strength [0.0, 1.0].

    Instead of binary relations (is_related / is_not_related),
    fuzzy relations allow degrees of relatedness.

    Examples:
        VERY_SIMILAR(A, B) = 0.95
        SOMEWHAT_OPPOSITE(A, B) = 0.4
        SLIGHTLY_RELATED(A, B) = 0.1
    """

    def __init__(self, concept_a, concept_b, relation_type, strength=1.0):
        self.concept_a = concept_a
        self.concept_b = concept_b
        self.relation_type = relation_type  # COORD, OPP, SIM, CAUSE, etc.
        self.strength = max(0.0, min(1.0, strength))  # Clamped to [0, 1]

    def __repr__(self):
        return f"FuzzyRel({self.concept_a} --{self.relation_type}={self.strength:.2f}-- {self.concept_b})"

    def is_similar_to(self, other):
        """Check if two relations are similar (for learning)."""
        return (
            self.concept_a == other.concept_a
            and self.concept_b == other.concept_b
            and self.relation_type == other.relation_type
        )

    def get_inverse(self):
        """Returns the inverse relation."""
        inv_type = {
            "COORD": "COORD",  # Symmetric
            "SIM": "SIM",  # Symmetric
            "OPP": "OPP",  # Symmetric
            "CAUSE": "EFFECT",
            "EFFECT": "CAUSE",
            "BEFORE": "AFTER",
            "AFTER": "BEFORE",
            "CONTAIN": "CONTAINED_BY",
            "CONTAINED_BY": "CONTAIN",
        }.get(self.relation_type, self.relation_type)
        return FuzzyRelation(self.concept_b, self.concept_a, inv_type, self.strength)


class FuzzySet:
    """
    A fuzzy set with named linguistic terms and membership functions.

    Example:
        distance = FuzzySet("distance", {
            "VERY_NEAR": {"type": "gaussian", "params": [0, 1.0]},
            "NEAR": {"type": "triangular", "params": [0, 2, 4]},
            "FAR": {"type": "gaussian", "params": [10, 3.0]},
            "VERY_FAR": {"type": "z_function", "params": [8, 15]}
        })
    """

    def __init__(self, name, terms):
        self.name = name
        self.terms = terms  # Dict of term_name -> {"type": func_type, "params": [...]}
        self.mf_cache = {}

    def get_membership(self, x, term_name):
        """Get membership degree of x in the given term."""
        if term_name not in self.terms:
            return 0.0

        term = self.terms[term_name]
        func_type = term.get("type", "triangular")
        params = term.get("params", [])

        if func_type == "triangular":
            return FuzzyMembership.triangular(x, *params[:3])
        elif func_type == "trapezoidal":
            return FuzzyMembership.trapezoidal(x, *params[:4])
        elif func_type == "gaussian":
            return FuzzyMembership.gaussian(x, *params[:2])
        elif func_type == "bell":
            return FuzzyMembership.bell(x, *params[:3])
        elif func_type == "sigmoid":
            return FuzzyMembership.sigmoid(x, *params[:2])
        elif func_type == "s":
            return FuzzyMembership.s_function(x, *params[:2])
        elif func_type == "z":
            return FuzzyMembership.z_function(x, *params[:2])
        elif func_type == "constant":
            return params[0] if params else 0.0
        else:
            return 0.0

    def fuzzify(self, x):
        """Returns dict of all term memberships for x."""
        result = {}
        for term_name in self.terms:
            result[term_name] = self.get_membership(x, term_name)
        return result


class FuzzyRule:
    """
    A fuzzy rule in IF-THEN format.

    Mamdani: IF antecedent THEN consequent (with membership)
    Sugeno: IF antecedent THEN consequent = f(inputs)

    Example:
        Mamdani: IF distance IS near AND battery IS low THEN urgency IS high
        Sugeno: IF hunger IS high THEN action = EXPLORE_BATTERY (weight 0.9)
    """

    def __init__(self, antecedent, consequent, rule_type="mamdani", weight=1.0):
        self.antecedent = antecedent  # Dict of {variable: term} or composite
        self.consequent = consequent  # For Mamdani: {variable: term}
        # For Sugeno: function or constant
        self.rule_type = rule_type  # "mamdani" or "sugeno"
        self.weight = weight
        self.fired_strength = 0.0

    def evaluate_antecedent(self, inputs):
        """
        Evaluate how much this rule fires given inputs.

        inputs: {variable_name: value}

        Returns: membership degree [0, 1]
        """
        if not self.antecedent:
            return 1.0

        # Handle different antecedent types
        if isinstance(self.antecedent, str):
            # Simple variable reference
            var_name = self.antecedent
            term = None
            for key, val in inputs.items():
                if var_name in key:
                    return val if isinstance(val, (int, float)) else 0.0

        elif isinstance(self.antecedent, dict):
            # Dict means AND (minimum) - all conditions must be met
            min_strength = 1.0
            for var, term_or_val in self.antecedent.items():
                if var not in inputs:
                    return 0.0
                input_val = inputs[var]

                if isinstance(term_or_val, str):
                    # Variable IS term
                    return 1.0  # Placeholder - actual fuzzification elsewhere
                else:
                    # Direct value
                    min_strength = min(min_strength, input_val)

            return min_strength

        return 0.0

    def __repr__(self):
        return f"FuzzyRule({self.antecedent} -> {self.consequent}, w={self.weight})"


class FuzzyInferenceSystem:
    """
    Complete fuzzy inference system with Mamdani/Sugeno engines.

    This is the main interface for fuzzy reasoning in GL5.1.
    """

    def __init__(self):
        self.fuzzy_sets = {}  # {set_name: FuzzySet}
        self.rules = []  # List of FuzzyRule
        self.composition_cache = {}  # Cached fuzzy compositions
        self.relation_network = {}  # FuzzyRelation graph

        self._init_default_sets()

    def _init_default_sets(self):
        """Initialize default linguistic variables."""

        # Distance to wall (0-15 cells)
        self.fuzzy_sets["distance"] = FuzzySet(
            "distance",
            {
                "VERY_NEAR": {"type": "gaussian", "params": [0.5, 0.5]},
                "NEAR": {"type": "triangular", "params": [0, 1.5, 3]},
                "MEDIUM": {"type": "triangular", "params": [2, 5, 8]},
                "FAR": {"type": "triangular", "params": [6, 10, 15]},
                "VERY_FAR": {"type": "gaussian", "params": [14, 2.0]},
            },
        )

        # Internal needs (0-150)
        self.fuzzy_sets["need"] = FuzzySet(
            "need",
            {
                "NONE": {"type": "z_function", "params": [0, 30]},
                "LOW": {"type": "triangular", "params": [15, 40, 60]},
                "MEDIUM": {"type": "triangular", "params": [45, 75, 100]},
                "HIGH": {"type": "triangular", "params": [85, 110, 130]},
                "CRITICAL": {"type": "s_function", "params": [120, 150]},
            },
        )

        # Battery distance (0-20)
        self.fuzzy_sets["battery_distance"] = FuzzySet(
            "battery_distance",
            {
                "ADJACENT": {"type": "gaussian", "params": [0.5, 0.3]},
                "NEAR": {"type": "triangular", "params": [0, 2, 5]},
                "MEDIUM": {"type": "triangular", "params": [3, 7, 12]},
                "FAR": {"type": "triangular", "params": [10, 15, 20]},
                "VERY_FAR": {"type": "gaussian", "params": [18, 3.0]},
            },
        )

        # Action urgency (0-1)
        self.fuzzy_sets["urgency"] = FuzzySet(
            "urgency",
            {
                "NONE": {"type": "z_function", "params": [0, 0.2]},
                "LOW": {"type": "triangular", "params": [0.1, 0.3, 0.5]},
                "MEDIUM": {"type": "triangular", "params": [0.4, 0.6, 0.8]},
                "HIGH": {"type": "s_function", "params": [0.7, 1.0]},
            },
        )

        # Similarity degree (0-1)
        self.fuzzy_sets["similarity"] = FuzzySet(
            "similarity",
            {
                "NONE": {"type": "z_function", "params": [0, 0.2]},
                "SLIGHT": {"type": "triangular", "params": [0.1, 0.3, 0.4]},
                "MODERATE": {"type": "triangular", "params": [0.35, 0.5, 0.65]},
                "STRONG": {"type": "triangular", "params": [0.6, 0.75, 0.85]},
                "VERY_STRONG": {"type": "s_function", "params": [0.8, 1.0]},
            },
        )

    def add_fuzzy_set(self, name, set_def):
        """Add a new fuzzy set."""
        self.fuzzy_sets[name] = FuzzySet(name, set_def)

    def add_rule(self, rule):
        """Add a fuzzy rule."""
        self.rules.append(rule)

    def add_relation(self, concept_a, concept_b, relation_type, strength):
        """Add a fuzzy relation between concepts."""
        key = tuple(sorted([concept_a, concept_b]))
        rel = FuzzyRelation(concept_a, concept_b, relation_type, strength)

        if key not in self.relation_network:
            self.relation_network[key] = []
        self.relation_network[key].append(rel)

    def get_relation_strength(self, concept_a, concept_b, relation_type=None):
        """Get the fuzzy relation strength between two concepts."""
        key = tuple(sorted([concept_a, concept_b]))
        if key not in self.relation_network:
            return 0.0

        best = 0.0
        for rel in self.relation_network[key]:
            if relation_type is None or rel.relation_type == relation_type:
                best = max(best, rel.strength)
        return best

    def fuzzy_compose(self, relation1, relation2, method="min"):
        """
        Compose two fuzzy relations.

        Methods:
        - min: Zadeh's composition (min of strengths)
        - product: Product composition
        - max: Max composition

        Returns: New FuzzyRelation with composed strength
        """
        if method == "min":
            strength = min(relation1.strength, relation2.strength)
        elif method == "product":
            strength = relation1.strength * relation2.strength
        elif method == "max":
            strength = max(relation1.strength, relation2.strength)
        else:
            strength = min(relation1.strength, relation2.strength)

        return FuzzyRelation(
            relation1.concept_a, relation2.concept_b, "COMPOSED", strength
        )

    def infer_relation(self, concept_a, concept_b, through_concepts=None):
        """
        Infer fuzzy relation through intermediate concepts.

        If A ~ X and X ~ B, then A ~ B (transitivity)
        """
        if through_concepts is None:
            return self.get_relation_strength(concept_a, concept_b, "COORD")

        direct = self.get_relation_strength(concept_a, concept_b, "COORD")
        if direct > 0:
            return direct

        # Try transitive inference
        path_strengths = []
        current = concept_a

        for next_concept in through_concepts:
            strength = self.get_relation_strength(current, next_concept, "COORD")
            if strength == 0:
                break
            path_strengths.append(strength)
            current = next_concept
        else:
            # Complete path found
            if current == concept_b:
                # Use minimum strength along path
                return min(path_strengths) if path_strengths else 0.0

        return 0.0

    def infer_action_fuzzy(self, inputs, action_rules):
        """
        Fuzzy inference for action selection.

        inputs: {perception_variable: value}
        action_rules: List of (condition_strength, action, confidence)

        Returns: (best_action, confidence) with fuzzy aggregation
        """
        if not action_rules:
            return None, 0.0

        action_scores = defaultdict(float)
        action_counts = defaultdict(int)

        for condition_strength, action, confidence in action_rules:
            # Weighted contribution based on condition match
            contribution = condition_strength * confidence
            action_scores[action] += contribution
            action_counts[action] += 1

        if not action_scores:
            return None, 0.0

        # Average and normalize
        best_action = None
        best_score = -1

        for action, total_score in action_scores.items():
            count = action_counts[action]
            avg_score = total_score / count
            if avg_score > best_score:
                best_score = avg_score
                best_action = action

        return best_action, best_score

    def defuzzify_centroid(self, fuzzy_output, domain):
        """
        Centroid defuzzification.

        Returns the centroid of the fuzzy output set.
        """
        if not fuzzy_output or not domain:
            return 0.0

        numerator = sum(y * x for x, y in zip(domain, fuzzy_output))
        denominator = sum(fuzzy_output)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def defuzzify_weighted(self, action_scores):
        """
        Weighted defuzzification for discrete action space.

        Returns: (action, confidence) with softmax-style weighting
        """
        if not action_scores:
            return None, 0.0

        # Softmax-style normalization
        exp_scores = {a: math.exp(s) for a, s in action_scores.items()}
        total = sum(exp_scores.values())

        if total == 0:
            return None, 0.0

        normalized = {a: exp_s / total for a, exp_s in exp_scores.items()}
        best = max(normalized.items(), key=lambda x: x[1])

        return best[0], best[1]

    def learn_membership_from_data(self, data_points, target_terms, learning_rate=0.1):
        """
        Adapt membership function parameters based on observed data.

        data_points: [(x, expected_membership), ...]
        target_terms: terms to adjust

        Uses gradient descent to minimize error.
        """
        for x, target in data_points:
            for set_name, set_def in self.fuzzy_sets.items():
                for term_name, membership_func in set_def.terms.items():
                    if term_name not in target_terms:
                        continue

                    current = set_def.get_membership(x, term_name)
                    error = target - current

                    # Simple parameter update (shift center)
                    params = membership_func.get("params", [])
                    if params and "center" not in membership_func:
                        # Shift center based on error direction
                        params[0] += learning_rate * error * 0.1
                        params[0] = max(0, params[0])

    def get_fuzzy_reasoning_trace(self, inputs):
        """
        Returns a trace of the fuzzy reasoning process for debugging.
        """
        trace = []

        for var_name, value in inputs.items():
            if var_name in self.fuzzy_sets:
                memberships = self.fuzzy_sets[var_name].fuzzify(value)
                trace.append(
                    {
                        "variable": var_name,
                        "value": value,
                        "memberships": memberships,
                        "active_terms": {k: v for k, v in memberships.items() if v > 0},
                    }
                )

        return trace


class FuzzyRFTIntegrator:
    """
    Integrates Fuzzy Inference with Relational Frame Theory.

    This allows:
    - Fuzzy relations between concepts (not just binary)
    - RFT-style reasoning over fuzzy relations
    - Derived fuzzy rules through relational inference
    """

    def __init__(self, fis=None, memory=None):
        self.fis = fis if fis else FuzzyInferenceSystem()
        self.memory = memory

    def create_fuzzy_relation_from_cooccurrence(
        self, concept_a, concept_b, cooccur_count, total_count
    ):
        """
        Create a fuzzy relation based on observed co-occurrence.

        strength = cooccur_count / total_count (fuzzy membership)
        """
        strength = cooccur_count / max(1, total_count)

        # Classify the relation strength
        if strength >= 0.8:
            relation_type = "VERY_STRONG_SIM"
        elif strength >= 0.6:
            relation_type = "STRONG_SIM"
        elif strength >= 0.4:
            relation_type = "MODERATE_SIM"
        elif strength >= 0.2:
            relation_type = "SLIGHT_SIM"
        else:
            relation_type = "WEAK_SIM"

        self.fis.add_relation(concept_a, concept_b, relation_type, strength)
        return strength

    def derive_fuzzy_rule_from_frame(self, frame, rules, weight_factor=1.0):
        """
        Create a fuzzy rule from a relational frame.

        If A COORD B with strength s, and A -> action with weight w,
        then B -> action with weight w * s * weight_factor
        """
        concept_a = frame.get("concept_a")
        concept_b = frame.get("concept_b")
        relation_type = frame.get("relation_type")
        strength = frame.get("strength", 0.5)

        if concept_a is None or concept_b is None:
            return None

        # Find rules for concept_a
        for rule in rules:
            if rule.get("command_id") == concept_a:
                action = rule.get("target_action")
                weight = rule.get("weight", 1.0)

                # Create fuzzy rule: "IF similar_to(concept_b) THEN action"
                fuzzy_rule = FuzzyRule(
                    antecedent={"similarity_to_b": strength},  # Fuzzy input
                    consequent={action: weight * strength * weight_factor},
                    rule_type="sugeno",
                    weight=strength,
                )

                return fuzzy_rule

        return None

    def fuzzy_entailment(self, concept_a, concept_b, relation_type="COORD"):
        """
        Fuzzy mutual entailment.

        If A has relation R to B with strength s,
        then properties of A transfer to B with strength s.
        """
        direct_strength = self.fis.get_relation_strength(
            concept_a, concept_b, relation_type
        )

        # Transitive closure through other concepts
        transitive_strength = self.fis.infer_relation(concept_a, concept_b)

        # Combined strength (max of direct and transitive)
        return max(direct_strength, transitive_strength)

    def transform_fuzzy_function(self, source_concept, target_concept, function_value):
        """
        Transform of fuzzy function (RFT concept).

        If source concept has fuzzy function value f,
        and source ~ target with strength s,
        then target inherits f * s.
        """
        strength = self.fuzzy_entailment(source_concept, target_concept)
        return function_value * strength

    def build_fuzzy_concept_network(self, rules, frames):
        """
        Build a network of fuzzy concepts with weighted relations.

        Returns nodes and edges with fuzzy strengths.
        """
        nodes = {}
        edges = []

        # Add nodes (concepts)
        for rule in rules:
            cmd_id = rule.get("command_id")
            if cmd_id:
                nodes[cmd_id] = {"actions": {}, "total_weight": 0}

        # Add edges (relations)
        for frame in frames:
            c1 = frame.get("concept_a")
            c2 = frame.get("concept_b")
            rel_type = frame.get("relation_type")
            strength = frame.get("strength", 0.5)

            edges.append(
                {"source": c1, "target": c2, "type": rel_type, "strength": strength}
            )

        return nodes, edges
