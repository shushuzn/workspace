#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deployment Validator (P5-2)
===========================
Validates auto-generated tools before deployment.

Features:
- Syntax checking
- Import testing
- Basic functionality validation
- Rollback on failure
- Safety checks

Version: 5.2.1
Author: Claw 🐾
Date: 2026-03-17
"""

import sys
import os
import ast
import importlib.util
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json
import logging

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentValidator:
    """Validate auto-generated tools before deployment."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
        self.backup_dir = self.workspace_dir / "data" / "deployment_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Validation results
        self.results = {
            'syntax_check': False,
            'import_check': False,
            'execution_check': False,
            'test_check': False,
            'overall': False
        }
    
    def validate_tool(self, tool_file: str, run_tests: bool = True) -> Dict[str, Any]:
        """
        Complete validation pipeline for a tool.
        
        Args:
            tool_file: Path to tool Python file
            run_tests: Whether to run tests
            
        Returns:
            Validation results dict
        """
        tool_path = Path(tool_file)
        
        if not tool_path.exists():
            return {
                'success': False,
                'error': f'Tool file not found: {tool_file}',
                'results': self.results
            }
        
        print(f"\n🔍 Validating: {tool_path.name}")
        print("=" * 60)
        
        # Step 1: Syntax check
        print("  [1/4] Syntax checking...")
        syntax_ok, syntax_error = self.check_syntax(tool_path)
        self.results['syntax_check'] = syntax_ok
        if not syntax_ok:
            print(f"  ✗ Syntax error: {syntax_error}")
            return self._create_result(False, f'Syntax error: {syntax_error}')
        print("  ✓ Syntax OK")
        
        # Step 2: Import check
        print("  [2/4] Import testing...")
        import_ok, import_error = self.test_import(tool_path)
        self.results['import_check'] = import_ok
        if not import_ok:
            print(f"  ✗ Import error: {import_error}")
            return self._create_result(False, f'Import error: {import_error}')
        print("  ✓ Import OK")
        
        # Step 3: Basic execution
        print("  [3/4] Basic execution...")
        exec_ok, exec_error = self.test_basic_execution(tool_path)
        self.results['execution_check'] = exec_ok
        if not exec_ok:
            print(f"  ✗ Execution error: {exec_error}")
            return self._create_result(False, f'Execution error: {exec_error}')
        print("  ✓ Execution OK")
        
        # Step 4: Run tests (if available)
        if run_tests:
            print("  [4/4] Running tests...")
            test_file = tool_path.parent / f"test_{tool_path.stem}.py"
            if test_file.exists():
                test_ok, test_error = self.run_tests(test_file)
                self.results['test_check'] = test_ok
                if not test_ok:
                    print(f"  ✗ Test failed: {test_error}")
                    return self._create_result(False, f'Test failed: {test_error}')
                print("  ✓ Tests OK")
            else:
                print("  ⚠ No test file found, skipping")
                self.results['test_check'] = True  # Don't fail if no tests
        else:
            self.results['test_check'] = True
        
        # All checks passed
        self.results['overall'] = True
        print("\n✅ All validation checks passed!")
        
        return self._create_result(True, "Validation successful")
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            ast.parse(source)
            return True, None
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def test_import(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Test if module can be imported."""
        try:
            # Use subprocess with escaped paths
            escaped_path = str(file_path).replace('\\', '/')
            parent_dir = str(file_path.parent).replace('\\', '/')
            
            import_test = f"""
import sys
sys.path.insert(0, r'{parent_dir}')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("temp_module", r'{escaped_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("Import successful")
    sys.exit(0)
except Exception as e:
    print(f"Import failed: {{e}}")
    sys.exit(1)
"""
            result = subprocess.run(
                [sys.executable, '-c', import_test],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
    
    def test_basic_execution(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Test basic execution (help command)."""
        try:
            result = subprocess.run(
                [sys.executable, str(file_path), '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Help should always work
            if result.returncode == 0:
                return True, None
            else:
                return False, f"Help command failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout executing help command"
        except Exception as e:
            return False, str(e)
    
    def run_tests(self, test_file: Path) -> Tuple[bool, Optional[str]]:
        """Run test suite."""
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=test_file.parent
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Test timeout"
        except Exception as e:
            return False, str(e)
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of file before deployment."""
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return backup_path
    
    def rollback(self, backup_path: Path, target_path: Path) -> bool:
        """Rollback to backup version."""
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        try:
            shutil.copy2(backup_path, target_path)
            logger.info(f"Rolled back to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def cleanup_old_backups(self, days: int = 7):
        """Clean up backups older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob('*.py'):
            if backup_file.stat().st_mtime < cutoff:
                try:
                    backup_file.unlink()
                    logger.info(f"Cleaned up old backup: {backup_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete {backup_file}: {e}")
    
    def _create_result(self, success: bool, message: str) -> Dict[str, Any]:
        """Create validation result dict."""
        return {
            'success': success,
            'message': message,
            'results': self.results.copy(),
            'timestamp': datetime.now().isoformat()
        }


class GitAutoCommitter:
    """Automatically commit generated tools to Git."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path(__file__).parent.parent
    
    def commit_new_tool(self, tool_file: str, test_file: str = None, 
                       message: str = None) -> bool:
        """
        Commit new tool and test to Git.
        
        Args:
            tool_file: Path to tool file
            test_file: Path to test file (optional)
            message: Commit message (auto-generated if None)
            
        Returns:
            True if successful
        """
        import subprocess
        
        tool_path = Path(tool_file)
        
        # Generate commit message if not provided
        if not message:
            module_name = tool_path.stem
            message = f"P5-2: Auto-generated {module_name} + tests"
        
        try:
            # Add files
            files_to_add = [str(tool_path)]
            if test_file and Path(test_file).exists():
                files_to_add.append(str(test_file))
            
            for file in files_to_add:
                result = subprocess.run(
                    ['git', 'add', file],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_dir
                )
                if result.returncode != 0:
                    logger.error(f"Git add failed: {result.stderr}")
                    return False
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir
            )
            
            if result.returncode != 0:
                logger.error(f"Git commit failed: {result.stderr}")
                return False
            
            logger.info(f"Committed: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Git commit error: {e}")
            return False
    
    def push(self, branch: str = 'master') -> bool:
        """Push commits to remote."""
        import subprocess
        
        try:
            result = subprocess.run(
                ['git', 'push', 'origin', branch],
                capture_output=True,
                text=True,
                cwd=self.workspace_dir
            )
            
            if result.returncode != 0:
                logger.error(f"Git push failed: {result.stderr}")
                return False
            
            logger.info(f"Pushed to origin/{branch}")
            return True
            
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return False


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment Validator (P5-2)")
    parser.add_argument("--validate", type=str, help="Validate tool file")
    parser.add_argument("--no-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--backup", type=str, help="Create backup of file")
    parser.add_argument("--cleanup", type=int, help="Clean up backups older than N days")
    parser.add_argument("--workspace", type=str, default=None, help="Workspace directory")
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.workspace)
    
    if args.validate:
        result = validator.validate_tool(args.validate, run_tests=not args.no_tests)
        
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Results: {result['results']}")
        
        return 0 if result['success'] else 1
    
    elif args.backup:
        backup_path = validator.create_backup(Path(args.backup))
        if backup_path:
            print(f"Backup created: {backup_path}")
            return 0
        else:
            print("Backup failed")
            return 1
    
    elif args.cleanup:
        validator.cleanup_old_backups(args.cleanup)
        print(f"Cleaned up backups older than {args.cleanup} days")
        return 0
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
