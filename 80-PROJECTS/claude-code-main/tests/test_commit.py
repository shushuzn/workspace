#!/usr/bin/env python3
"""Tests for the commit command port."""

from __future__ import annotations
import subprocess
import sys
import unittest

class TestCommitCommand(unittest.TestCase):
    def test_commit_module_importable(self):
        from src.commit import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, "commit")
        self.assertTrue(callable(run))

    def test_commit_entry_point(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.commit", "--dry-run"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        # --dry-run makes git commit fail gracefully (no changes), exit != 0 is ok
        output = result.stdout + result.stderr
        self.assertIn("branch", output.lower())  # git status output

if __name__ == "__main__":
    unittest.main()
