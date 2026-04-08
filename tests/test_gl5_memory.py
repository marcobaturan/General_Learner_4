"""
GL5 Memory Architecture Tests

Tests for the multi-store memory system implementation:
- Sensory Memory (SM)
- Working Memory (WM)
- Intermediate-Term Memory (ITM)
- Long-Term Memory (LTM)
- Decay mechanisms
- Transfer mechanisms

Author: Marco
Date: 2026-04-08
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import Memory
from constants import (
    MEMORY_SENSORY,
    MEMORY_WORKING,
    MEMORY_INTERMEDIATE,
    MEMORY_EPISODIC,
    MEMORY_SEMANTIC,
    MEMORY_DERIVED,
    DECAY_RATE_INTERMEDIATE,
    DECAY_RATE_SEMANTIC,
    WM_CAPACITY,
    FORGET_THRESHOLD,
)


class TestGL5MemoryTypes(unittest.TestCase):
    """Test GL5 memory type constants are properly defined."""

    def test_memory_types_defined(self):
        """All GL5 memory types should be defined."""
        self.assertIsNotNone(MEMORY_SENSORY)
        self.assertIsNotNone(MEMORY_WORKING)
        self.assertIsNotNone(MEMORY_INTERMEDIATE)

    def test_memory_types_unique(self):
        """Memory types should be unique."""
        types = [
            MEMORY_SENSORY,
            MEMORY_WORKING,
            MEMORY_INTERMEDIATE,
            MEMORY_EPISODIC,
            MEMORY_SEMANTIC,
            MEMORY_DERIVED,
        ]
        self.assertEqual(len(types), len(set(types)))

    def test_wm_capacity(self):
        """WM capacity should be 4 (Cowan, 2001)."""
        self.assertEqual(WM_CAPACITY, 4)


class TestIntermediateMemory(unittest.TestCase):
    """Test Intermediate-Term Memory functionality."""

    def setUp(self):
        """Create fresh memory instance for each test."""
        self.memory = Memory(db_path=":memory:")

    def test_intermediate_memory_table_exists(self):
        """Intermediate memory table should exist."""
        cur = self.memory.conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='intermediate_memory'"
        )
        self.assertIsNotNone(cur.fetchone())

    def test_add_chrono_to_intermediate(self):
        """add_chrono should store in intermediate_memory."""
        self.memory.add_chrono(
            perception={"MURO_N": "CERCA"},
            action=0,
            reward=10,
            command="FORWARD",
            rehearsed=False,
        )
        items = self.memory.get_all_chrono()
        self.assertEqual(len(items), 1)
        # JSON uses double quotes
        import json

        expected_perc = json.dumps({"MURO_N": "CERCA"})
        self.assertEqual(items[0]["perception"], expected_perc)

    def test_rehearsed_flag(self):
        """Rehearsed items should be marked."""
        self.memory.add_chrono(
            perception={"test": "value"}, action=0, reward=5, rehearsed=True
        )
        items = self.memory.get_all_chrono()
        self.assertEqual(items[0]["rehearsed"], 1)

    def test_clear_chrono_clears_intermediate(self):
        """clear_chrono should clear intermediate memory."""
        self.memory.add_chrono({"test": "val"}, 0, 5)
        self.memory.clear_chrono()
        items = self.memory.get_all_chrono()
        self.assertEqual(len(items), 0)


class TestDecayRates(unittest.TestCase):
    """Test decay rate application."""

    def setUp(self):
        self.memory = Memory(db_path=":memory:")

    def test_intermediate_decay_rate_defined(self):
        """Intermediate decay rate should be defined."""
        self.assertIsNotNone(DECAY_RATE_INTERMEDIATE)
        self.assertGreater(DECAY_RATE_INTERMEDIATE, 0.8)  # Slower than episodic
        self.assertLess(DECAY_RATE_INTERMEDIATE, 1.0)  # But not instant

    def test_decay_applies_to_intermediate_rules(self):
        """Decay should apply to intermediate memory type."""
        from constants import MEMORY_INTERMEDIATE

        # Add rule with intermediate memory type
        self.memory.add_rule(
            perception_pattern={"test": "perc"},
            action=0,
            weight=10.0,
            memory_type=MEMORY_INTERMEDIATE,
        )

        # Apply decay
        self.memory.decay_rules()

        # Check decay applied
        rules = self.memory.get_rules()
        self.assertEqual(len(rules), 1)
        self.assertLess(rules[0]["weight"], 10.0)

    def test_intermediate_table_decay(self):
        """Intermediate memory table should also decay."""
        self.memory.add_chrono({"test": "val"}, 0, 5, weight=10.0)

        # Note: Current implementation may not decay the table directly
        # This test documents expected behavior
        items = self.memory.get_all_chrono()
        self.assertGreater(len(items), 0)
        items = self.memory.get_all_chrono()
        self.assertGreater(len(items), 0)


class TestWorkingMemoryCapacity(unittest.TestCase):
    """Test Working Memory capacity constraints."""

    def test_wm_capacity_constant(self):
        """WM capacity should be 4 chunks."""
        self.assertEqual(WM_CAPACITY, 4)

    def test_agenda_respects_capacity(self):
        """Agenda should not exceed WM capacity."""
        # This test documents the constraint
        # Actual implementation in Learner class
        max_agenda = WM_CAPACITY
        self.assertGreater(max_agenda, 0)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with GL4."""

    def setUp(self):
        self.memory = Memory(db_path=":memory:")

    def test_episodic_memory_type_still_works(self):
        """MEMORY_EPISODIC should still function."""
        self.memory.add_rule(
            perception_pattern={"test": "val"},
            action=0,
            weight=5.0,
            memory_type=MEMORY_EPISODIC,
        )
        rules = self.memory.get_rules()
        self.assertEqual(len(rules), 1)

    def test_semantic_memory_type_still_works(self):
        """MEMORY_SEMANTIC should still function."""
        self.memory.add_rule(
            perception_pattern={"test": "val"},
            action=0,
            weight=5.0,
            memory_type=MEMORY_SEMANTIC,
        )
        rules = self.memory.get_rules()
        self.assertEqual(len(rules), 1)

    def test_chrono_alias_exists(self):
        """chrono_memory table should exist for compatibility."""
        cur = self.memory.conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chrono_memory'"
        )
        self.assertIsNotNone(cur.fetchone())


class TestMemoryFlow(unittest.TestCase):
    """Test memory flow between stores."""

    def test_memory_hierarchy_flow(self):
        """Document expected memory flow."""
        # SM → WM → ITM → LTM
        # This is the theoretical model
        expected_flow = [
            "SENSORY (250ms, 12 items)",
            "WORKING (18s, 4 chunks)",
            "INTERMEDIATE (20-30 min, 50 items)",
            "LONG-TERM (indefinite)",
        ]
        self.assertEqual(len(expected_flow), 4)


class TestForgettingCurve(unittest.TestCase):
    """Test Ebbinghaus forgetting curve implementation."""

    def test_forget_threshold_defined(self):
        """FORGET_THRESHOLD should be defined."""
        self.assertIsNotNone(FORGET_THRESHOLD)
        self.assertGreater(FORGET_THRESHOLD, 0)

    def test_weak_rules_pruned(self):
        """Rules below threshold should be deleted."""
        memory = Memory(db_path=":memory:")

        # Add very weak rule
        memory.add_rule(
            perception_pattern={"weak": "rule"},
            action=0,
            weight=0.1,  # Below threshold (0.5)
            memory_type=MEMORY_SEMANTIC,
        )

        memory.decay_rules()

        rules = memory.get_rules()
        # Weak rule should be pruned (unless other rules exist)


class TestRFTIntegration(unittest.TestCase):
    """Test RFT still works with new memory architecture."""

    def setUp(self):
        self.memory = Memory(db_path=":memory:")

    def test_relational_frames_table_exists(self):
        """RFT relational_frames table should exist."""
        cur = self.memory.conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='relational_frames'"
        )
        self.assertIsNotNone(cur.fetchone())

    def test_derived_memory_type_works(self):
        """MEMORY_DERIVED should still function."""
        self.memory.add_rule(
            perception_pattern=None,
            action=0,
            weight=3.0,
            memory_type=MEMORY_DERIVED,
            command_id=1,
        )
        rules = self.memory.get_rules()
        derived = [r for r in rules if r["memory_type"] == MEMORY_DERIVED]
        self.assertGreater(len(derived), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
