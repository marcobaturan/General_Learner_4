import unittest
import os
import tempfile
from memory import Memory
from rft import RelationalFrameEngine
from constants import MEMORY_DERIVED, MEMORY_SEMANTIC, ACT_FORWARD, ACT_BACKWARD


class TestRFTEngine(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix=".db")
        self.memory = Memory(self.db_path)
        self.rft = RelationalFrameEngine()

    def tearDown(self):
        self.memory.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_coordination_detection(self):
        id_avanza = self.memory.get_or_create_concept_id("AVANZA")
        id_go = self.memory.get_or_create_concept_id("GO")

        for _ in range(3):
            self.memory.add_rule(
                None,
                ACT_FORWARD,
                weight=8,
                command_id=id_avanza,
                memory_type=MEMORY_SEMANTIC,
            )
        for _ in range(3):
            self.memory.add_rule(
                None,
                ACT_FORWARD,
                weight=8,
                command_id=id_go,
                memory_type=MEMORY_SEMANTIC,
            )

        result = self.rft.detect_coordination(self.memory)
        frames = self.memory.get_frames_for_concept(id_avanza)

        self.assertGreater(result, 0)
        coord_frames = [f for f in frames if f["relation_type"] == "COORD"]
        self.assertGreater(len(coord_frames), 0)

    def test_mutual_entailment(self):
        id_a = self.memory.get_or_create_concept_id("A")
        id_b = self.memory.get_or_create_concept_id("B")

        self.memory.add_rule(
            None, ACT_FORWARD, weight=10, command_id=id_a, memory_type=MEMORY_SEMANTIC
        )

        self.memory.add_relational_frame(id_a, "COORD", id_b, strength=0.8)

        derived_count = self.rft.derive_mutual_entailment(self.memory)

        derived_rules = self.memory.get_derived_rules(id_b)
        self.assertGreater(len(derived_rules), 0)
        self.assertEqual(derived_rules[0]["target_action"], ACT_FORWARD)

    def test_transitivity_closure(self):
        id_a = self.memory.get_or_create_concept_id("A")
        id_b = self.memory.get_or_create_concept_id("B")
        id_c = self.memory.get_or_create_concept_id("C")

        self.memory.add_relational_frame(id_a, "COORD", id_b, strength=0.8)
        self.memory.add_relational_frame(id_b, "COORD", id_c, strength=0.8)

        added = self.rft.close_transitivity(self.memory)

        frames = self.memory.get_all_frames()
        transitivos = [
            f for f in frames if f["concept_a"] == id_a and f["concept_b"] == id_c
        ]
        self.assertGreater(len(transitivos), 0)

    def test_opposition_frame(self):
        id_forward = self.memory.get_or_create_concept_id("FORWARD")
        id_back = self.memory.get_or_create_concept_id("BACK")

        for _ in range(3):
            self.memory.add_rule(
                None,
                ACT_FORWARD,
                weight=8,
                command_id=id_forward,
                memory_type=MEMORY_SEMANTIC,
            )
        for _ in range(3):
            self.memory.add_rule(
                None,
                ACT_BACKWARD,
                weight=8,
                command_id=id_back,
                memory_type=MEMORY_SEMANTIC,
            )

        result = self.rft.detect_opposition(self.memory)

        frames = self.memory.get_all_frames()
        opp_frames = [f for f in frames if f["relation_type"] == "OPP"]
        self.assertGreater(len(opp_frames), 0)

    def test_no_interference_with_direct_rules(self):
        id_a = self.memory.get_or_create_concept_id("A")

        self.memory.add_rule(
            None, ACT_FORWARD, weight=10, command_id=id_a, memory_type=MEMORY_SEMANTIC
        )
        self.memory.add_rule(
            None, ACT_FORWARD, weight=4, command_id=id_a, memory_type=MEMORY_DERIVED
        )

        rules = self.memory.get_rules()
        direct = [
            r
            for r in rules
            if r["command_id"] == id_a and r["memory_type"] == MEMORY_SEMANTIC
        ]
        derived = [
            r
            for r in rules
            if r["command_id"] == id_a and r["memory_type"] == MEMORY_DERIVED
        ]

        self.assertEqual(direct[0]["weight"], 10)
        self.assertEqual(derived[0]["weight"], 4)

    def test_run_cycle(self):
        id_a = self.memory.get_or_create_concept_id("A")
        id_b = self.memory.get_or_create_concept_id("B")

        self.memory.add_rule(
            None, ACT_FORWARD, weight=10, command_id=id_a, memory_type=MEMORY_SEMANTIC
        )
        for _ in range(3):
            self.memory.add_rule(
                None,
                ACT_FORWARD,
                weight=8,
                command_id=id_b,
                memory_type=MEMORY_SEMANTIC,
            )

        result = self.rft.run_cycle(self.memory)

        self.assertIn("total_frames", result)
        self.assertGreater(result["total_frames"], 0)


if __name__ == "__main__":
    unittest.main()
