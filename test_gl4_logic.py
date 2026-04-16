#!/usr/bin/env python3
"""
TDD tests for GL4 Vision/Speech logic.

Tests both the original integration behavior AND the new
visual pattern generalization (template extraction + translation).
"""

import os
import json
import unittest

# Headless pygame setup
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

from memory import Memory
from gl4_logic import VisionWindow, SpeechWindow


class TestVisionWindowOriginal(unittest.TestCase):
    """Tests the original VisionWindow learning and recall."""

    def setUp(self):
        self.db_path = "test_vision_original.db"
        self.mem = Memory(self.db_path)
        self.vision = VisionWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_learn_stores_visual_pattern(self):
        """Learning a pattern should create a VISUAL_PATTERN production."""
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "DOT"
        self.vision._process_learning()

        prods = self.mem.get_cognitive_productions(production_type="VISUAL_PATTERN")
        self.assertEqual(len(prods), 1)
        self.assertEqual(prods[0]["name"], "DOT")

    def test_query_recalls_learned_pattern(self):
        """Querying a learned label should reconstruct the grid."""
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "DOT"
        self.vision._process_learning()

        # Clear grid, then query
        self.vision.grid = [[0]*10 for _ in range(10)]
        self.vision.cmd_box.text = "DOT"
        self.vision._process_query()

        self.assertEqual(self.vision.grid[5][5], 1)

    def test_hierarchical_decomposition(self):
        """LINE should contain POINT as a component (PART_OF frame)."""
        # Teach POINT
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "POINT"
        self.vision._process_learning()

        # Teach LINE (superset of POINT)
        self.vision.grid[5][6] = 1
        self.vision.cmd_box.text = "LINE"
        self.vision._process_learning()

        cur = self.mem.conn.cursor()
        cur.execute(
            "SELECT * FROM relational_frames WHERE relation_type='PART_OF'"
        )
        frames = cur.fetchall()
        self.assertGreater(len(frames), 0)


class TestTemplateExtraction(unittest.TestCase):
    """Tests the new _extract_template helper."""

    def setUp(self):
        self.db_path = "test_vision_template.db"
        self.mem = Memory(self.db_path)
        self.vision = VisionWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_extract_template_single_pixel(self):
        """A single pixel at (5,5) has template [(0,0)]."""
        flat = [0] * 100
        flat[5 * 10 + 5] = 1  # pixel at (5,5)
        template = self.vision._extract_template(flat)

        self.assertEqual(len(template), 1)
        self.assertEqual(template, [(0, 0)])

    def test_extract_template_cross_shape(self):
        """A cross centered at (5,5) should produce 5 offsets."""
        flat = [0] * 100
        # Cross: center + 4 arms
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            flat[(5 + dy) * 10 + (5 + dx)] = 1

        template = self.vision._extract_template(flat)
        self.assertEqual(len(template), 5)
        # All offsets should be relative to centroid (which IS center)
        self.assertIn((0, 0), template)
        self.assertIn((1, 0), template)
        self.assertIn((-1, 0), template)
        self.assertIn((0, 1), template)
        self.assertIn((0, -1), template)

    def test_extract_template_empty_grid(self):
        """An empty grid should return an empty template."""
        flat = [0] * 100
        template = self.vision._extract_template(flat)
        self.assertEqual(template, [])


class TestTemplateRendering(unittest.TestCase):
    """Tests the new _render_template helper."""

    def setUp(self):
        self.db_path = "test_vision_render.db"
        self.mem = Memory(self.db_path)
        self.vision = VisionWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_render_at_default_center(self):
        """Rendering a single-pixel template at (5,5) sets grid[5][5]."""
        template = [(0, 0)]
        self.vision._render_template(template, 5, 5)
        self.assertEqual(self.vision.grid[5][5], 1)

    def test_render_at_custom_position(self):
        """Rendering a cross template at (2,3) places pixels correctly."""
        template = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        self.vision._render_template(template, 2, 3)

        self.assertEqual(self.vision.grid[3][2], 1)  # center
        self.assertEqual(self.vision.grid[3][3], 1)  # right
        self.assertEqual(self.vision.grid[3][1], 1)  # left
        self.assertEqual(self.vision.grid[4][2], 1)  # down
        self.assertEqual(self.vision.grid[2][2], 1)  # up

    def test_render_clips_to_bounds(self):
        """Pixels that fall outside the 10x10 grid are silently clipped."""
        template = [(0, 0), (-5, 0)]  # second pixel would be at (-4, 0)
        self.vision._render_template(template, 1, 0)

        self.assertEqual(self.vision.grid[0][1], 1)  # center pixel placed
        # (-4, 0) is out of bounds — no crash, no pixel set
        # All cells at x<0 should remain 0 (they aren't accessible)


class TestQueryWithPosition(unittest.TestCase):
    """Tests the enhanced _process_query with AT x,y and RANDOM."""

    def setUp(self):
        self.db_path = "test_vision_query_pos.db"
        self.mem = Memory(self.db_path)
        self.vision = VisionWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _teach_cross(self):
        """Helper: teach a cross pattern named CROSS."""
        self.vision.grid = [[0]*10 for _ in range(10)]
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            self.vision.grid[5 + dy][5 + dx] = 1
        self.vision.cmd_box.text = "CROSS"
        self.vision._process_learning()
        self.vision.grid = [[0]*10 for _ in range(10)]

    def test_query_plain_label_renders_at_center(self):
        """Querying 'CROSS' renders at default center (5,5)."""
        self._teach_cross()
        self.vision.cmd_box.text = "CROSS"
        self.vision._process_query()

        self.assertEqual(self.vision.grid[5][5], 1)

    def test_query_with_at_position(self):
        """Querying 'CROSS AT 2,3' renders cross anchored at (2,3)."""
        self._teach_cross()
        self.vision.cmd_box.text = "CROSS AT 2,3"
        self.vision._process_query()

        self.assertEqual(self.vision.grid[3][2], 1)  # center at (2,3)
        self.assertEqual(self.vision.grid[3][3], 1)  # right arm

    def test_query_with_random_renders_somewhere(self):
        """Querying 'CROSS RANDOM' renders the cross at some valid position."""
        self._teach_cross()
        self.vision.cmd_box.text = "CROSS RANDOM"
        self.vision._process_query()

        # At least 1 pixel should be set somewhere
        total_pixels = sum(sum(row) for row in self.vision.grid)
        self.assertGreater(total_pixels, 0)

    def test_query_unknown_label_shows_error(self):
        """Querying an unknown label sets status to '???'."""
        self.vision.cmd_box.text = "UNKNOWN_SHAPE"
        self.vision._process_query()
        self.assertEqual(self.vision.status_msg, "???")


class TestSpeechWindow(unittest.TestCase):
    """Tests the SpeechWindow speech pattern learning and recall."""

    def setUp(self):
        self.db_path = "test_speech.db"
        self.mem = Memory(self.db_path)
        self.speech = SpeechWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_speech_tokenizes_input(self):
        """Speech input should create concept IDs for each token."""
        self.speech._process_speech("HOLA MUNDO")

        cur = self.mem.conn.cursor()
        cur.execute(
            "SELECT value FROM conceptual_ids WHERE value IN ('HOLA', 'MUNDO')"
        )
        tokens = [r[0] for r in cur.fetchall()]
        self.assertIn("HOLA", tokens)
        self.assertIn("MUNDO", tokens)

    def test_speech_stores_history(self):
        """Speech interactions should be recorded in history."""
        self.speech._process_speech("TEST")
        self.assertGreater(len(self.speech.history), 0)

    def test_repeated_pattern_stores_echo(self):
        """'hola hola' should store pattern: stimulus=[HOLA] → response=HOLA."""
        self.speech._process_speech("hola hola")

        prods = self.mem.get_cognitive_productions(
            production_type="SPEECH_PATTERN"
        )
        self.assertEqual(len(prods), 1)

        data = json.loads(prods[0]["description"])
        self.assertEqual(data["stimulus"], ["HOLA"])
        self.assertEqual(data["response"], "HOLA")

    def test_echo_recall_after_learning(self):
        """After learning 'hola hola', typing 'hola' should respond 'HOLA'."""
        # Teach the pattern
        self.speech._process_speech("hola hola")

        # Now query with just 'hola'
        self.speech._process_speech("hola")

        # The last history entry should contain the response
        agent_msgs = [m for m in self.speech.history if "Agent:" in m]
        last_response = agent_msgs[-1]
        self.assertIn("HOLA", last_response)

    def test_multi_token_pattern(self):
        """'me llamo bot1' should store: stimulus=[ME,LLAMO] → response=BOT1."""
        self.speech._process_speech("me llamo bot1")

        prods = self.mem.get_cognitive_productions(
            production_type="SPEECH_PATTERN"
        )
        self.assertEqual(len(prods), 1)

        data = json.loads(prods[0]["description"])
        self.assertEqual(data["stimulus"], ["ME", "LLAMO"])
        self.assertEqual(data["response"], "BOT1")

    def test_recall_multi_token_pattern(self):
        """After learning 'me llamo bot1', 'me llamo' should respond 'BOT1'."""
        self.speech._process_speech("me llamo bot1")
        self.speech._process_speech("me llamo")

        agent_msgs = [m for m in self.speech.history if "Agent:" in m]
        last_response = agent_msgs[-1]
        self.assertIn("BOT1", last_response)

    def test_reinforcement_updates_confidence(self):
        """Positive reinforcement should increase pattern confidence."""
        self.speech._process_speech("hola hola")
        self.speech._process_speech("hola")  # triggers match

        # Reinforce positively
        self.speech._reinforce(0.15)

        prods = self.mem.get_cognitive_productions(
            production_type="SPEECH_PATTERN"
        )
        self.assertGreater(prods[0]["confidence"], 0.7)

    def test_creates_rft_frames_between_tokens(self):
        """Adjacent tokens should get COORD relational frames."""
        self.speech._process_speech("hola mundo")

        cur = self.mem.conn.cursor()
        cur.execute(
            "SELECT * FROM relational_frames WHERE relation_type='COORD'"
        )
        frames = cur.fetchall()
        self.assertGreater(len(frames), 0)

    def test_unknown_input_stored_for_learning(self):
        """First input with no match should store pattern for later."""
        self.speech._process_speech("adios amigo")

        # Should have stored a pattern
        prods = self.mem.get_cognitive_productions(
            production_type="SPEECH_PATTERN"
        )
        self.assertGreater(len(prods), 0)


class TestSpeechHelpers(unittest.TestCase):
    """Tests module-level speech helper functions."""

    def test_tokenize_speech(self):
        """Should split and uppercase text."""
        from gl4_logic import _tokenize_speech
        self.assertEqual(_tokenize_speech("hola mundo"), ["HOLA", "MUNDO"])

    def test_split_repeated_pattern(self):
        """Repeated tokens should split at halfway point."""
        from gl4_logic import _split_stimulus_response
        stim, resp = _split_stimulus_response(["HOLA", "HOLA"])
        self.assertEqual(stim, ["HOLA"])
        self.assertEqual(resp, "HOLA")

    def test_split_multi_token(self):
        """Multi-token should use last token as response."""
        from gl4_logic import _split_stimulus_response
        stim, resp = _split_stimulus_response(["ME", "LLAMO", "BOT1"])
        self.assertEqual(stim, ["ME", "LLAMO"])
        self.assertEqual(resp, "BOT1")

    def test_split_single_token(self):
        """Single token produces echo pattern."""
        from gl4_logic import _split_stimulus_response
        stim, resp = _split_stimulus_response(["HOLA"])
        self.assertEqual(stim, ["HOLA"])
        self.assertEqual(resp, "HOLA")

    def test_token_overlap_exact_match(self):
        """Exact match should return 1.0."""
        from gl4_logic import _compute_token_overlap
        score = _compute_token_overlap(["HOLA"], ["HOLA"])
        self.assertEqual(score, 1.0)

    def test_token_overlap_partial(self):
        """Partial match should return fraction."""
        from gl4_logic import _compute_token_overlap
        score = _compute_token_overlap(["ME", "LLAMO"], ["ME", "COMO"])
        self.assertEqual(score, 0.5)

    def test_token_overlap_no_match(self):
        """No overlap should return 0.0."""
        from gl4_logic import _compute_token_overlap
        score = _compute_token_overlap(["HOLA"], ["ADIOS"])
        self.assertEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()

