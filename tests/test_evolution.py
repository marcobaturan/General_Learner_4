import unittest
import sys
import os
import json
import sqlite3

# Adjust path to import from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory import Memory
from fuzzy_logic import FBN
from constants import *


class TestCognitiveEvolution(unittest.TestCase):
    def setUp(self):
        # Use a temporary test database
        self.db_path = "test_memory.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.memory = Memory(db_path=self.db_path)
        self.fbn = FBN()

    def tearDown(self):
        self.memory.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_conceptual_ids(self):
        # Test tokenization
        text = "MOVE FORWARD"
        tokens = self.memory.tokenize(text)
        # Should be ['MOVE', ' ', 'FORWARD'] as IDs (3 tokens)
        self.assertEqual(len(tokens), 3)

        # Verify IDs are consistent
        tokens2 = self.memory.tokenize("MOVE")
        self.assertEqual(tokens[0], tokens2[0])

        # Verify space token
        space_id = self.memory.get_or_create_concept_id(" ")
        self.assertEqual(tokens[1], space_id)

    def test_fuzzy_logic(self):
        # Test membership functions
        # 0.5 is 'MUY_CERCA' in triangular(0, 0, 2) check:
        # triangular(0.5, 0, 0, 2) -> (2 - 0.5)/(2-0) = 1.5/2 = 0.75
        mu = self.fbn.triangular(0.5, 0, 0, 2)
        self.assertEqual(mu, 0.75)

        # Test vector generation
        state = {
            "raw_distances": {"N": 1, "E": 10, "S": 10, "W": 10},
            "needs": {"hunger": 0, "tiredness": 50},
            "batt_distance": None,
        }
        vector = self.fbn.get_fuzzy_vector(state)
        # SENSE_NORTH:NEAR should be in there (dist 1)
        self.assertIn("SENSE_NORTH:NEAR", vector)
        self.assertIn("SENSE_EAST:FAR", vector)
        self.assertIn("NEED_REST:LOW", vector)

    def test_asymptotic_decay(self):
        # Add a rule with weight 10.0
        p_id = json.dumps(["TEST"])
        # Memory type EPISODIC = 0
        self.memory.add_rule(p_id, ACT_FORWARD, weight=10.0, memory_type=0)

        # Verify it exists
        rules = self.memory.get_rules()
        self.assertEqual(rules[0]["weight"], 10.0)

        # Apply decay
        self.memory.decay_rules()
        decayed_rules = self.memory.get_rules()
        # 10.0 * DECAY_RATE_EPISODIC (0.9 in constants usually)
        self.assertLess(decayed_rules[0]["weight"], 10.0)
        self.assertAlmostEqual(decayed_rules[0]["weight"], 10.0 * DECAY_RATE_EPISODIC)

    def test_territory_mapping(self):
        self.memory.update_territory(5, 5, "SIT_TEST", importance=1.5)
        self.memory.update_territory(5, 5, "SIT_TEST", importance=1.5)

        territory = self.memory.get_territory()
        self.assertEqual(len(territory), 1)
        self.assertEqual(territory[0]["x"], 5)
        self.assertEqual(territory[0]["visits"], 2)
        self.assertEqual(territory[0]["importance"], 1.5)


if __name__ == "__main__":
    unittest.main()
