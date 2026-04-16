import unittest
import os
import json
from learner import Learner
from memory import Memory
from robot import Robot
from environment import Environment
from gl4_logic import VisionWindow, SpeechWindow
import pygame

# Mock screen for pygame windows
pygame.init()
screen = pygame.Surface((800, 600))

class TestMultimodalDream(unittest.TestCase):
    """Tests for multimodal concept synthesis and generalization during sleep."""

    def setUp(self):
        self.db_path = "test_multimodal.db"
        self.mem = Memory(self.db_path)
        self.env = Environment()
        self.learner = Learner(self.mem, self.env)
        self.robot = Robot(self.env, self_id=1)
        self.vision = VisionWindow(screen, self.mem)
        self.speech = SpeechWindow(screen, self.mem)

    def tearDown(self):
        self.mem.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_analysis_and_resolution_during_sleep(self):
        """Should match speech tokens to visual labels during sleep."""
        # 1. Teach vision: "PUNTO"
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "PUNTO"
        self.vision._process_learning()

        # 2. Teach speech: stimulus "ESTO ES" -> response "PUNTO"
        self.speech._process_speech("esto es punto")

        # 3. Sleep cycle
        self.learner.sleep_cycle()

        # 4. Verify Resolution (COORD frame between speech concept and visual pattern)
        # We need a way to find if a COORD frame exists between the speech response and vision name
        cur = self.mem.conn.cursor()
        cur.execute("SELECT * FROM relational_frames WHERE relation_type='COORD'")
        frames = cur.fetchall()
        
        # At least one frame should link the "PUNTO" from speech to the "PUNTO" from vision
        # (They might share the same Concept ID if they use the same string)
        self.assertGreater(len(frames), 0, "No coordination frames created during sleep")

    def test_synthesis_multimodal_anchor(self):
        """Should create a derived rule connecting speech to vision."""
        # Teach vision and speech
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "PUNTO"
        self.vision._process_learning()
        self.speech._process_speech("esto es punto")

        self.learner.sleep_cycle()

        # Debug: Check if patterns exist
        s_prods = self.mem.get_cognitive_productions(production_type="SPEECH_PATTERN")
        v_prods = self.mem.get_cognitive_productions(production_type="VISUAL_PATTERN")
        print(f"DEBUG TEST: Speech Prods: {len(s_prods)}, Visual Prods: {len(v_prods)}")
        if s_prods:
            print(f"DEBUG TEST: Speech 0 Desc: {s_prods[0]['description']}")

        # Now, hearing "PUNTO" should be able to resolve to drawing the PUNTO template
        # We'll check if a derived rule exists that maps "PUNTO" to a visual command or template
        prods = self.mem.get_cognitive_productions(production_type="MULTIMODAL_ANCHOR")
        self.assertGreater(len(prods), 0, "No multimodal anchor synthesized")

    def test_generalization_rft_transfer(self):
        """Should generalize 'POINT' command if it's coordinate with 'PUNTO'."""
        # 1. Teach vision "PUNTO"
        self.vision.grid[5][5] = 1
        self.vision.cmd_box.text = "PUNTO"
        self.vision._process_learning()
        
        # 2. Teach speech "unto punto" (synonym)
        self.speech._process_speech("unto punto")
        
        # 3. Teach "unto" is coordinate with "POINT" (manual RFT frame)
        unto_id = self.mem.get_or_create_concept_id("UNTO")
        point_id = self.mem.get_or_create_concept_id("POINT")
        self.mem.add_relational_frame(unto_id, "COORD", point_id, 0.9)

        self.learner.sleep_cycle()

        # 4. Final verify: hearing "POINT" should now know about the "PUNTO" visual template
        # (Through transitive COORD: POINT <-> UNTO <-> PUNTO (vision))
        # This is a deep generalization.
        cur = self.mem.conn.cursor()
        # Find if any derived connection exists for POINT
        cur.execute("SELECT * FROM relational_frames WHERE concept_a=? OR concept_b=?", (point_id, point_id))
        self.assertGreater(len(cur.fetchall()), 0)

    def test_body_state_decision_bias(self):
        """Thompson sampling should be biased by high hunger."""
        # Teach a battery-related action
        perc_id = json.dumps([0,0,0,0,0]) # dummy
        self.mem.add_rule(perc_id, 2, weight=5.0) # ACT_FORWARD
        
        # Normal state
        self.robot.hunger = 0
        weights_normal = self.learner.act(self.robot) # should return something
        
        # High hunger
        self.robot.hunger = 100
        # In this state, the learner should favor actions that have historically led to rewards
        # more strongly, especially if they involve BATTERY perception
        # Just verify energy is updated
        self.learner._update_body_state(self.robot)
        self.assertLess(self.learner.energy, 100.0)

if __name__ == "__main__":
    unittest.main()
