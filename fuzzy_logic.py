import math
from constants import *


class FBN:
    """
    Translates raw numerical sensory data into fuzzy linguistic labels.
    Zero-dependency implementation.
    """

    @staticmethod
    def triangular(x, a, b, c):
        """Triangular membership function."""
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        if b < x < c:
            return (c - x) / (c - b)
        return 0.0

    @staticmethod
    def trapezoidal(x, a, b, c, d):
        """Trapezoidal membership function."""
        if x <= a or x >= d:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        if b < x <= c:
            return 1.0
        if c < x < d:
            return (d - x) / (d - c)
        return 0.0

    def __init__(self):
        pass

    def fuzzify_distance(self, dist):
        """Fuzzification of wall distance."""
        return {
            "NEAR": self.trapezoidal(dist, 0, 0, 1.2, 2.5),
            "FAR": self.trapezoidal(dist, 4, 6, 20, 20),
            "VERY_NEAR": self.trapezoidal(dist, 0, 0, 0.8, 1.5),
            "MIDDLE": self.trapezoidal(dist, 1.5, 3.0, 4.0, 6.0),
        }

    def fuzzify_hunger(self, val):
        """Fuzzification of internal needs (hunger/tiredness)."""
        return {
            "LOW": self.trapezoidal(val, 0, 0, 30, 60),
            "MEDIUM": self.triangular(val, 40, 75, 110),
            "HIGH": self.trapezoidal(val, 90, 120, 200, 200),
        }

    def fuzzify_battery(self, dist):
        """Fuzzification of battery distance."""
        if dist is None or dist > 15:
            return {
                "NEAR": 0,
                "FAR": 0,
                "ABSENT": 1.0,
                "MUY_CERCA": 0,
                "LEJOS": 0,
                "AUSENTE": 1.0,
            }
        return {
            "VERY_NEAR": self.trapezoidal(dist, 0, 0, 1.5, 3.0),
            "FAR": self.trapezoidal(dist, 2.0, 5.0, 20, 20),
            "NEAR": self.trapezoidal(dist, 0, 0, 3.0, 5.0),
            "MUY_CERCA": self.trapezoidal(dist, 0, 0, 1.5, 3.0),
            "LEJOS": self.trapezoidal(dist, 2.0, 5.0, 20, 20),
            "AUSENTE": 0.0,
        }

    def process_state(self, robot_state):
        """
        Converts full robot state into a vector of fuzzy membership degrees.
        Returns a dictionary of dictionaries.
        """
        raw_perception = robot_state["raw_distances"]  # To be implemented in robot.py
        hunger = robot_state["needs"]["hunger"]
        tiredness = robot_state["needs"]["tiredness"]
        batt_dist = robot_state["batt_distance"]

        fuzzy_state = {}

        # Wall Distances in 4 directions
        for direction, dist in raw_perception.items():
            direction_map = {"N": "NORTH", "E": "EAST", "S": "SOUTH", "W": "WEST"}
            fuzzy_state[f"SENSE_{direction_map.get(direction, direction)}"] = (
                self.fuzzify_distance(dist)
            )

        # GL5: Mirror detection - check if mirror is in any direction
        perception = robot_state.get("perception", [])
        if perception:
            has_mirror = False
            has_reset = False
            for row in perception:
                for cell in row:
                    if cell == MIRROR_ID:
                        has_mirror = True
                    if cell == RESET_BUTTON_ID:
                        has_reset = True
            fuzzy_state["MIRROR"] = {
                "NEAR": 1.0 if has_mirror else 0.0,
                "FAR": 0.0 if has_mirror else 1.0,
            }
            fuzzy_state["RESET_BUTTON"] = {
                "NEAR": 1.0 if has_reset else 0.0,
                "FAR": 0.0 if has_reset else 1.0,
            }
        else:
            fuzzy_state["MIRROR"] = {"NEAR": 0.0, "FAR": 1.0}
            fuzzy_state["RESET_BUTTON"] = {"NEAR": 0.0, "FAR": 1.0}

        fuzzy_state["NEED_ENERGY"] = self.fuzzify_hunger(hunger)
        fuzzy_state["NEED_REST"] = self.fuzzify_hunger(tiredness)
        fuzzy_state["TARGET_OBJECT"] = self.fuzzify_battery(batt_dist)

        return fuzzy_state

    def get_fuzzy_vector(self, robot_state):
        """
        Returns a flat list of (feature_name:label) for rules.
        Only returns features with membership > 0.
        """
        f_state = self.process_state(robot_state)
        vector = []
        for category, memberships in f_state.items():
            for label, degree in memberships.items():
                if degree > 0:
                    vector.append(f"{category}:{label}")
        return sorted(vector)

    def get_feature_vector(self, robot_state):
        """Alias for compatibility."""
        return self.get_fuzzy_vector(robot_state)
