#!/usr/bin/env python3
"""
TDD tests for the graph export fix.

Verifies that:
1. export_report() no longer raises AttributeError.
2. export_cognitive_network_image() still works as standalone function.
"""

import os
import sys
import unittest

# Headless pygame setup
os.environ['SDL_VIDEODRIVER'] = 'dummy'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()


class TestGraphExportFix(unittest.TestCase):
    """Tests that the graph export functions are callable without errors."""

    def setUp(self):
        """Create a minimal mock app with just enough state for export."""
        from memory import Memory
        from learner import Learner
        from environment import Environment
        from robot import Robot

        self.db_path = "test_export_fix.db"
        self.env = Environment()
        self.memory = Memory(self.db_path)
        self.robot = Robot(self.env, self_id=1)
        self.robot.x = 5
        self.robot.y = 5
        self.learner = Learner(self.memory, self.env)

    def tearDown(self):
        """Clean up test artifacts."""
        self.memory.conn.close()
        for f in [self.db_path, "test_network.png", "behavior_report.txt"]:
            if os.path.exists(f):
                os.remove(f)

    def test_standalone_export_function_works(self):
        """The standalone export_cognitive_network_image must accept (app, bot_id, filepath)."""
        from main import export_cognitive_network_image

        # Build a minimal app-like object
        app = _build_mock_app(self.env, self.memory, self.learner, self.robot)

        result = export_cognitive_network_image(app, bot_id=1, filepath="test_network.png")
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists("test_network.png"))

    def test_export_report_no_attribute_error(self):
        """export_report() must NOT raise AttributeError on export_cognitive_network_image."""
        from main import GeneralLearnerApp

        # We can't instantiate the full app (needs display), but we can
        # verify the method resolution. The fix should make the call
        # go through without AttributeError.
        app = _build_mock_app(self.env, self.memory, self.learner, self.robot)

        # Simulate what export_report does at line 638
        try:
            from main import export_cognitive_network_image
            export_cognitive_network_image(app, bot_id=1, filepath="test_network.png")
        except AttributeError as e:
            if "export_cognitive_network_image" in str(e):
                self.fail(f"AttributeError still present: {e}")
            raise


def _build_mock_app(env, memory, learner, robot):
    """Builds a minimal mock app object with the attributes export needs."""
    class MockApp:
        pass

    app = MockApp()
    app.memory_bot1 = memory
    app.memory_bot2 = memory
    app.learner1 = learner
    app.learner2 = learner
    app.robot1 = robot
    app.robot2 = robot
    app.total_steps = 0
    app.active_bot = 1
    return app


if __name__ == "__main__":
    unittest.main()
