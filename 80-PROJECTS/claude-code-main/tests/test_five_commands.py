#!/usr/bin/env python3
"""Tests for ported commands: brief, bridge-kick, addCommand, caches."""

from __future__ import annotations

import subprocess
import sys
import unittest


class TestBriefCommand(unittest.TestCase):
    def test_brief_importable(self):
        from src.brief import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, 'brief')
        self.assertTrue(callable(run))

    def test_brief_entry_point(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.brief'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        output = result.stdout + result.stderr
        self.assertIn('commit', output)  # git log output contains commit hashes


class TestBridgeKickCommand(unittest.TestCase):
    def test_bridge_kick_importable(self):
        from src.bridge_kick import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, 'bridge-kick')
        self.assertTrue(callable(run))

    def test_bridge_kick_entry_point(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.bridge_kick'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        # bridge-kick not in PATH, should fail with specific error
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)


class TestAddCommand(unittest.TestCase):
    def test_add_command_importable(self):
        from src.addCommand import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, 'addCommand')
        self.assertTrue(callable(run))

    def test_add_command_entry_point(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.addCommand', 'foo', 'bar'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('foo', result.stdout)


class TestCachesCommand(unittest.TestCase):
    def test_caches_importable(self):
        from src.caches import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, 'caches')
        self.assertTrue(callable(run))

    def test_caches_entry_point(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.caches'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        output = result.stdout
        self.assertIn('Done', output)
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
