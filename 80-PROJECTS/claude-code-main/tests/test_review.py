#!/usr/bin/env python3
"""Tests for review command group."""

from __future__ import annotations

import subprocess
import sys
import unittest


class TestReviewCommand(unittest.TestCase):
    def test_review_importable(self):
        from src.review import ARCHIVE_NAME, run
        self.assertEqual(ARCHIVE_NAME, 'review')
        self.assertTrue(callable(run))

    def test_review_no_args(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.review'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        output = result.stdout
        self.assertIn('subcommands', output)

    def test_review_subcommand_ultrareviewCommand(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.review', 'ultrareviewCommand'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('ultrareviewCommand', result.stdout)

    def test_review_subcommand_security_review(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.review', 'security-review'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('security-review', result.stdout)

    def test_review_unknown_subcommand(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.review', 'unknown-cmd'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unknown subcommand', result.stderr)


if __name__ == '__main__':
    unittest.main()
