#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for P5-2 Tools
=========================
Tests for:
- ToolCodeGenerator
- DeploymentValidator
- GitAutoCommitter

Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import unittest
from pathlib import Path
import tempfile
import shutil
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TestToolCodeGenerator(unittest.TestCase):
    """Test ToolCodeGenerator class."""

    def setUp(self):
        from tool_code_generator import ToolCodeGenerator
        self.test_dir = tempfile.mkdtemp()
        self.generator = ToolCodeGenerator(self.test_dir)

        # Sample hypothesis
        self.sample_hypothesis = {
            "id": "HYP-TEST-001",
            "title": "Test Innovation Tool",
            "description": "A test tool for validation",
            "implementation_complexity": "medium",
            "required_tools": [],
            "test_criteria": [
                "Criterion 1: Basic functionality",
                "Criterion 2: Performance"
            ]
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test generator initialization."""
        self.assertIsNotNone(self.generator.workspace_dir)
        self.assertTrue(self.generator.templates_dir.exists())

    def test_title_to_class_name(self):
        """Test class name conversion."""
        result = self.generator._title_to_class_name("Test Innovation Tool")
        self.assertEqual(result, "TestInnovationTool")

        result = self.generator._title_to_class_name("My Tool v2.0")
        self.assertEqual(result, "MyToolV20")

    def test_title_to_module_name(self):
        """Test module name conversion."""
        result = self.generator._title_to_module_name("Test Innovation Tool")
        self.assertEqual(result, "test_innovation_tool")

        result = self.generator._title_to_module_name("My Tool v2.0")
        self.assertEqual(result, "my_tool_v20")

    def test_generate_tool(self):
        """Test tool generation."""
        output_file = self.generator.generate_tool(self.sample_hypothesis)

        # Verify file exists
        self.assertTrue(Path(output_file).exists())

        # Verify content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("TestInnovationTool", content)
            self.assertIn("A test tool for validation", content)
            self.assertIn("def execute", content)
            self.assertIn("if __name__", content)

    def test_generate_test_scaffold(self):
        """Test test scaffold generation."""
        # First generate a tool
        tool_file = self.generator.generate_tool(self.sample_hypothesis)

        # Then generate test scaffold
        test_file = self.generator.generate_test_scaffold(tool_file)

        # Verify test file exists
        self.assertTrue(Path(test_file).exists())

        # Verify content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("TestTestInnovationTool", content)
            self.assertIn("def test_initialization", content)
            self.assertIn("def test_execute", content)
            self.assertIn("if __name__", content)

    def test_generate_complex_tool(self):
        """Test generation with high complexity."""
        hypothesis = self.sample_hypothesis.copy()
        hypothesis["implementation_complexity"] = "high"

        tool_file = self.generator.generate_tool(hypothesis)

        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("def optimize", content)
            self.assertIn("def validate", content)


class TestDeploymentValidator(unittest.TestCase):
    """Test DeploymentValidator class."""

    def setUp(self):
        from deployment_validator import DeploymentValidator
        self.test_dir = Path(tempfile.mkdtemp())
        self.validator = DeploymentValidator(str(self.test_dir))

        # Create a simple test tool
        self.test_tool = self.test_dir / "simple_tool.py"
        self.test_tool.write_text('''#!/usr/bin/env python3
import sys
from pathlib import Path

def main():
    print("Simple tool works!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''', encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator.workspace_dir)
        self.assertTrue(self.validator.backup_dir.exists())

    def test_check_syntax_valid(self):
        """Test syntax check with valid code."""
        is_valid, error = self.validator.check_syntax(self.test_tool)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_check_syntax_invalid(self):
        """Test syntax check with invalid code."""
        invalid_file = self.test_dir / "invalid.py"
        invalid_file.write_text("def broken(", encoding='utf-8')

        is_valid, error = self.validator.check_syntax(invalid_file)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_test_import(self):
        """Test import testing."""
        is_valid, error = self.validator.test_import(self.test_tool)
        self.assertTrue(is_valid)

    def test_basic_execution(self):
        """Test basic execution."""
        is_valid, error = self.validator.test_basic_execution(self.test_tool)
        self.assertTrue(is_valid)

    def test_validate_tool_success(self):
        """Test successful validation."""
        result = self.validator.validate_tool(self.test_tool, run_tests=False)

        self.assertTrue(result['success'])
        self.assertTrue(result['results']['syntax_check'])
        self.assertTrue(result['results']['import_check'])
        self.assertTrue(result['results']['execution_check'])
        self.assertTrue(result['results']['overall'])

    def test_create_backup(self):
        """Test backup creation."""
        backup_path = self.validator.create_backup(self.test_tool)

        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())

    def test_rollback(self):
        """Test rollback functionality."""
        # Create backup
        backup_path = self.validator.create_backup(self.test_tool)

        # Modify original
        self.test_tool.write_text("# Modified", encoding='utf-8')

        # Rollback
        success = self.validator.rollback(backup_path, self.test_tool)
        self.assertTrue(success)

        # Verify content restored
        content = self.test_tool.read_text(encoding='utf-8')
        self.assertIn("def main", content)


class TestIntegration(unittest.TestCase):
    """Integration tests for P5-2 workflow."""

    def setUp(self):
        from tool_code_generator import ToolCodeGenerator
        from deployment_validator import DeploymentValidator

        self.test_dir = Path(tempfile.mkdtemp())
        self.generator = ToolCodeGenerator(str(self.test_dir))
        self.validator = DeploymentValidator(str(self.test_dir))

        self.sample_hypothesis = {
            "id": "HYP-INT-001",
            "title": "Integration Test Tool",
            "description": "Integration testing",
            "implementation_complexity": "medium"
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_full_workflow(self):
        """Test complete generate-validate workflow."""
        # 1. Generate tool
        tool_file = self.generator.generate_tool(self.sample_hypothesis)
        self.assertTrue(Path(tool_file).exists())

        # 2. Generate test scaffold
        test_file = self.generator.generate_test_scaffold(tool_file)
        self.assertTrue(Path(test_file).exists())

        # 3. Validate tool
        result = self.validator.validate_tool(tool_file, run_tests=False)
        self.assertTrue(result['success'])

        # 4. Create backup
        backup_path = self.validator.create_backup(Path(tool_file))
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())

    def test_batch_generation(self):
        """Test batch tool generation."""
        hypotheses = [
            {"id": "HYP-001", "title": "Tool One", "description": "First tool", "complexity": "low"},
            {"id": "HYP-002", "title": "Tool Two", "description": "Second tool", "complexity": "medium"},
            {"id": "HYP-003", "title": "Tool Three", "description": "Third tool", "complexity": "high"}
        ]

        generated_files = []
        for hyp in hypotheses:
            tool_file = self.generator.generate_tool(hyp)
            generated_files.append(tool_file)
            self.assertTrue(Path(tool_file).exists())

        # Verify all files have different class names
        expected_names = ["ToolOne", "ToolTwo", "ToolThree"]
        for file, expected_name in zip(generated_files, expected_names):
            content = Path(file).read_text(encoding='utf-8')
            self.assertIn(expected_name, content)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestToolCodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDeploymentValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" *70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" *70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
