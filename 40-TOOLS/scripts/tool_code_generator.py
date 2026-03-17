#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Code Generator (P5-2)
==========================
Automatically generates Python tool code from hypotheses.

Features:
- Scaffold generation from hypothesis
- Class structure creation
- Method stub generation
- Import dependency resolution
- Docstring generation
- Type hint support

Version: 5.2.0
Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import json

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class ToolCodeGenerator:
    """Generate Python tool code from hypotheses."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
        self.templates_dir = self.workspace_dir / "30-scripts-tools" / "templates"
        self.output_dir = self.workspace_dir / "30-scripts-tools"
        
        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Template cache
        self.templates = {}
    
    def generate_tool(self, hypothesis: Dict, output_file: str = None) -> str:
        """Generate complete tool from hypothesis."""
        
        # Extract hypothesis info
        title = hypothesis.get('title', 'NewTool')
        description = hypothesis.get('description', 'Auto-generated tool')
        complexity = hypothesis.get('implementation_complexity', 'medium')
        
        # Generate class name from title
        class_name = self._title_to_class_name(title)
        module_name = self._title_to_module_name(title)
        
        # Generate code sections
        imports = self._generate_imports(hypothesis)
        class_def = self._generate_class_definition(class_name, description)
        methods = self._generate_methods(hypothesis, complexity)
        main_func = self._generate_main_function(class_name)
        
        # Assemble complete code
        code = self._assemble_code(imports, class_def, methods, main_func, module_name)
        
        # Determine output file
        if not output_file:
            output_file = self.output_dir / f"{module_name}.py"
        else:
            output_file = Path(output_file)
        
        # Write to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return str(output_file)
    
    def _title_to_class_name(self, title: str) -> str:
        """Convert title to CamelCase class name."""
        # Remove special chars and split
        words = re.sub(r'[^a-zA-Z0-9\s]', '', title).split()
        # CamelCase
        return ''.join(word.capitalize() for word in words)
    
    def _title_to_module_name(self, title: str) -> str:
        """Convert title to snake_case module name."""
        # Lowercase and replace spaces/special chars with underscores
        module = title.lower()
        module = re.sub(r'[^a-z0-9\s]', '', module)
        module = '_'.join(module.split())
        return module
    
    def _generate_imports(self, hypothesis: Dict) -> str:
        """Generate import statements."""
        imports = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '"""',
            f"{hypothesis.get('title', 'Auto-generated Tool')}",
            '=' * len(hypothesis.get('title', 'Auto-generated Tool')),
            '',
            f"Auto-generated from hypothesis: {hypothesis.get('id', 'unknown')}",
            f"Description: {hypothesis.get('description', 'N/A')}",
            '',
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'Author: Claw 🐾 (AI Agent)',
            '"""',
            '',
            'import sys',
            'import os',
            'import json',
            'import logging',
            'from pathlib import Path',
            'from datetime import datetime',
            'from typing import Dict, List, Any, Optional, Tuple',
            '',
            '# Windows UTF-8 encoding fix',
            'if sys.platform == "win32":',
            '    try:',
            '        sys.stdout.reconfigure(encoding="utf-8")',
            '    except Exception:',
            '        pass',
            '',
            '# Configure logging',
            'logging.basicConfig(',
            '    level=logging.INFO,',
            '    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"',
            ')',
            'logger = logging.getLogger(__name__)',
            '',
            ''
        ]
        
        # Add hypothesis-specific imports
        required_tools = hypothesis.get('required_tools', [])
        if 'pattern' in str(required_tools).lower():
            imports.insert(12, 'import re')
        
        return '\n'.join(imports)
    
    def _generate_class_definition(self, class_name: str, description: str) -> str:
        """Generate class definition."""
        class_def = f'''
class {class_name}:
    """
    {description}
    
    Auto-generated by Tool Code Generator (P5-2).
    Review and refine implementation before production use.
    """
    
    def __init__(self, workspace_dir: str = None):
        """Initialize the tool."""
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
        self.data_dir = self.workspace_dir / "data" / "{class_name.lower()}"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state from file."""
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {{}}
    
    def _save_state(self):
        """Save state to file."""
        state_file = self.data_dir / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False, default=str)
    
'''
        return class_def
    
    def _generate_methods(self, hypothesis: Dict, complexity: str) -> str:
        """Generate method stubs based on complexity."""
        methods = []
        
        # Core method (always included)
        methods.append('''
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the main functionality.
        
        Args:
            **kwargs: Configuration parameters
            
        Returns:
            Dict containing results and status
        """
        logger.info(f"Executing {self.__class__.__name__}")
        
        # TODO: Implement core logic
        result = {
            "status": "success",
            "message": "Execution completed",
            "data": None
        }
        
        return result
''')
        
        # Additional methods based on complexity
        if complexity in ['medium', 'high']:
            methods.append('''
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Analyze input data.
        
        Args:
            data: Input data to analyze
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing data")
        
        # TODO: Implement analysis logic
        return {
            "metrics": {},
            "insights": []
        }
''')
        
        if complexity == 'high':
            methods.append('''
    def optimize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize configuration.
        
        Args:
            config: Current configuration
            
        Returns:
            Optimized configuration
        """
        logger.info("Optimizing configuration")
        
        # TODO: Implement optimization logic
        return config
    
    def validate(self, input_data: Any) -> Tuple[bool, str]:
        """
        Validate input data.
        
        Args:
            input_data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info("Validating input")
        
        # TODO: Implement validation logic
        return True, ""
''')
        
        # Add test criteria as methods
        test_criteria = hypothesis.get('test_criteria', [])
        for i, criterion in enumerate(test_criteria[:2]):  # Max 2 criteria methods
            method_name = f"test_criterion_{i+1}"
            methods.append(f'''
    def {method_name}(self) -> bool:
        """
        Test criterion: {criterion[:50]}
        
        Returns:
            True if criterion is met
        """
        # TODO: Implement test
        return True
''')
        
        return '\n'.join(methods)
    
    def _generate_main_function(self, class_name: str) -> str:
        """Generate main function and CLI."""
        main_func = f'''
def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="{class_name}")
    parser.add_argument("--execute", action="store_true", help="Execute main function")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    parser.add_argument("--workspace", type=str, default=None, help="Workspace directory")
    
    args = parser.parse_args()
    
    tool = {class_name}(args.workspace)
    
    if args.execute:
        result = tool.execute()
        print(f"Result: {{result}}")
        return 0
    elif args.test:
        # Basic self-test
        print(f"Testing {{class_name}}...")
        try:
            result = tool.execute()
            print(f"✓ Execute: {{result.get('status', 'unknown')}}")
            print("All tests passed!")
            return 0
        except Exception as e:
            print(f"✗ Test failed: {{e}}")
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
'''
        return main_func
    
    def _assemble_code(self, imports: str, class_def: str, methods: str, 
                       main_func: str, module_name: str) -> str:
        """Assemble all code sections."""
        code = f'''{imports}
{class_def}
{methods}
{main_func}
'''
        return code
    
    def generate_test_scaffold(self, tool_file: str, output_file: str = None) -> str:
        """Generate test scaffold for a tool."""
        tool_path = Path(tool_file)
        module_name = tool_path.stem
        
        # Extract class name from tool
        with open(tool_path, 'r', encoding='utf-8') as f:
            content = f.read()
            class_match = re.search(r'class\s+(\w+):', content)
            class_name = class_match.group(1) if class_match else module_name.title().replace('_', '')
        
        test_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for {class_name}
{'=' * (17 + len(class_name))}

Auto-generated test scaffold.
Implement actual tests based on requirements.
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class Test{class_name}(unittest.TestCase):
    """Test {class_name} class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from {module_name} import {class_name}
        self.test_dir = tempfile.mkdtemp()
        self.tool = {class_name}(self.test_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test tool initialization."""
        self.assertIsNotNone(self.tool.workspace_dir)
        self.assertTrue(self.tool.data_dir.exists())
    
    def test_execute(self):
        """Test execute method."""
        result = self.tool.execute()
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'success')
    
    def test_load_state_new(self):
        """Test state loading for new instance."""
        self.assertIsInstance(self.tool.state, dict)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def setUp(self):
        """Set up integration test."""
        from {module_name} import {class_name}
        self.test_dir = tempfile.mkdtemp()
        self.tool = {class_name}(self.test_dir)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete workflow."""
        # Execute
        result = self.tool.execute()
        
        # Verify
        self.assertEqual(result['status'], 'success')


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(Test{class_name}))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\\n" + "="*70)
    print(f"Tests run: {{result.testsRun}}")
    print(f"Failures: {{len(result.failures)}}")
    print(f"Errors: {{len(result.errors)}}")
    print(f"Success: {{result.wasSuccessful()}}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
'''
        
        if not output_file:
            output_file = self.output_dir / f"test_{module_name}.py"
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        return str(output_file)


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool Code Generator (P5-2)")
    parser.add_argument("--generate", type=str, help="Generate tool from hypothesis JSON file")
    parser.add_argument("--test-scaffold", type=str, help="Generate test scaffold for tool")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--workspace", type=str, default=None, help="Workspace directory")
    
    args = parser.parse_args()
    
    generator = ToolCodeGenerator(args.workspace)
    
    if args.generate:
        # Load hypothesis from JSON
        with open(args.generate, 'r', encoding='utf-8') as f:
            hypothesis = json.load(f)
        
        output_file = generator.generate_tool(hypothesis, args.output)
        print(f"Generated tool: {output_file}")
        
        # Also generate test scaffold
        test_file = generator.generate_test_scaffold(output_file)
        print(f"Generated test scaffold: {test_file}")
        
        return 0
    
    elif args.test_scaffold:
        test_file = generator.generate_test_scaffold(args.test_scaffold, args.output)
        print(f"Generated test scaffold: {test_file}")
        return 0
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
