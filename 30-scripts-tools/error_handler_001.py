import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Friendly Error Handler - User-friendly error messages with solutions
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class FriendlyErrorHandler:
    """Convert technical errors to user-friendly messages with solutions"""
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.log_file = Path("13-memory/error_log.json")
        self.error_log = self._load_error_log()
    
    def _load_error_patterns(self) -> Dict:
        """Load error pattern library"""
        return {
            # Git errors
            "git_network": {
                "patterns": [
                    r"fatal: Could not read from remote repository",
                    r"fatal: unable to access.*Could not resolve host",
                    r"error: RPC failed.*curl.*GnuTLS",
                    r"fatal: The remote end hung up unexpectedly",
                ],
                "message": "Network connection issue with Git remote",
                "solution": "1. Check your internet connection\n2. Try: git remote -v to verify remote URL\n3. Retry the operation (auto-retry enabled)",
                "retryable": True,
                "category": "git"
            },
            "git_conflict": {
                "patterns": [
                    r"CONFLICT.*content conflict",
                    r"Automatic merge failed.*fix conflicts",
                    r"error: Your local changes.*would be overwritten",
                ],
                "message": "Git merge conflict detected",
                "solution": "1. Open conflicting files and resolve markers (<<<<<<, ======, >>>>>>)\n2. Run: git add <file> after fixing\n3. Run: git commit to complete merge",
                "retryable": False,
                "category": "git"
            },
            "git_auth": {
                "patterns": [
                    r"fatal: Authentication failed",
                    r"error: Permission denied.*publickey",
                    r"fatal: Could not read username.*password",
                ],
                "message": "Git authentication failed",
                "solution": "1. Verify credentials are correct\n2. Check SSH keys: ssh-add -l\n3. For HTTPS: git config --global credential.helper store",
                "retryable": False,
                "category": "git"
            },
            
            # Python errors
            "python_syntax": {
                "patterns": [
                    r"SyntaxError: invalid syntax",
                    r"SyntaxError: unexpected EOF",
                    r"SyntaxError: EOL while scanning string literal",
                ],
                "message": "Python syntax error detected",
                "solution": "1. Check for missing colons, parentheses, or quotes\n2. Verify indentation (use 4 spaces)\n3. Look for unclosed brackets/strings",
                "retryable": False,
                "category": "python"
            },
            "python_indentation": {
                "patterns": [
                    r"IndentationError: expected an indented block",
                    r"IndentationError: unexpected indent",
                    r"TabError: inconsistent use of tabs and spaces",
                ],
                "message": "Python indentation error",
                "solution": "1. Use consistent indentation (4 spaces, no tabs)\n2. Check if/for/while/def/class blocks\n3. Configure editor to convert tabs to spaces",
                "retryable": False,
                "category": "python"
            },
            "python_import": {
                "patterns": [
                    r"ModuleNotFoundError: No module named",
                    r"ImportError: cannot import name",
                    r"ModuleNotFoundError: No module named '.*'",
                ],
                "message": "Python module not found",
                "solution": "1. Install missing module: pip install <module_name>\n2. Check virtual environment is activated\n3. Verify module name spelling",
                "retryable": False,
                "category": "python"
            },
            "python_file": {
                "patterns": [
                    r"FileNotFoundError: \[Errno 2\] No such file or directory",
                    r"PermissionError: \[Errno 13\] Permission denied",
                    r"IsADirectoryError: \[Errno 21\] Is a directory",
                ],
                "message": "File access error",
                "solution": "1. Verify file path is correct\n2. Check file permissions\n3. Ensure directory exists",
                "retryable": False,
                "category": "python"
            },
            
            # Workflow errors
            "workflow_step": {
                "patterns": [
                    r"step.*not found in workflow",
                    r"Invalid step ID",
                    r"Step.*does not exist",
                ],
                "message": "Workflow step not found",
                "solution": "1. Check step ID in workflow.json\n2. Verify workflow file is loaded\n3. Use valid step IDs from workflow definition",
                "retryable": False,
                "category": "workflow"
            },
            "workflow_config": {
                "patterns": [
                    r"workflow.json.*not found",
                    r"Invalid workflow configuration",
                    r"Missing required workflow field",
                ],
                "message": "Workflow configuration error",
                "solution": "1. Verify workflow.json exists and is valid JSON\n2. Check required fields: flow_id, total_steps, steps\n3. Validate JSON syntax",
                "retryable": False,
                "category": "workflow"
            },
            
            # General errors
            "timeout": {
                "patterns": [
                    r"TimeoutError",
                    r"timed out",
                    r"Connection timed out",
                    r"Request timeout",
                ],
                "message": "Operation timed out",
                "solution": "1. Increase timeout value if possible\n2. Check network connectivity\n3. Retry operation (may be temporary)",
                "retryable": True,
                "category": "general"
            },
            "memory": {
                "patterns": [
                    r"MemoryError",
                    r"out of memory",
                    r"Cannot allocate memory",
                ],
                "message": "Out of memory",
                "solution": "1. Close other applications\n2. Process data in smaller chunks\n3. Increase available memory if possible",
                "retryable": False,
                "category": "general"
            },
            "encoding": {
                "patterns": [
                    r"UnicodeEncodeError.*codec can't encode",
                    r"UnicodeDecodeError.*codec can't decode",
                    r"charmap.*can't encode",
                ],
                "message": "Character encoding error",
                "solution": "1. Use UTF-8 encoding for files\n2. Remove or replace special characters\n3. Set encoding explicitly in file operations",
                "retryable": False,
                "category": "general"
            },
        }
    
    def _load_error_log(self) -> Dict:
        """Load error log"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "errors": [],
            "stats": {
                "total_errors": 0,
                "by_category": {},
                "retryable_count": 0,
                "resolved_count": 0
            }
        }
    
    def _save_error_log(self):
        """Save error log"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.error_log, f, ensure_ascii=False, indent=2)
    
    def analyze_error(self, error_message: str) -> Dict:
        """
        Analyze error message and provide friendly response
        
        Args:
            error_message: Raw error message
            
        Returns:
            Dict with friendly message, solution, and metadata
        """
        result = {
            "original_error": error_message,
            "friendly_message": "An unexpected error occurred",
            "solution": "Please check the error details and try again",
            "category": "unknown",
            "retryable": False,
            "confidence": 0.0,
            "matched_pattern": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to match error patterns
        for error_type, error_info in self.error_patterns.items():
            for pattern in error_info["patterns"]:
                if re.search(pattern, error_message, re.IGNORECASE):
                    result["friendly_message"] = error_info["message"]
                    result["solution"] = error_info["solution"]
                    result["category"] = error_info["category"]
                    result["retryable"] = error_info["retryable"]
                    result["matched_pattern"] = error_type
                    result["confidence"] = 0.9
                    break
            
            if result["confidence"] > 0:
                break
        
        # Log the error
        self._log_error(result)
        
        return result
    
    def _log_error(self, result: Dict):
        """Log error to file"""
        self.error_log["errors"].append(result)
        self.error_log["stats"]["total_errors"] += 1
        
        category = result["category"]
        self.error_log["stats"]["by_category"][category] = \
            self.error_log["stats"]["by_category"].get(category, 0) + 1
        
        if result["retryable"]:
            self.error_log["stats"]["retryable_count"] += 1
        
        # Keep only last 100 errors
        self.error_log["errors"] = self.error_log["errors"][-100:]
        
        self._save_error_log()
    
    def get_friendly_message(self, error_message: str) -> str:
        """Get just the friendly message"""
        result = self.analyze_error(error_message)
        return result["friendly_message"]
    
    def get_solution(self, error_message: str) -> str:
        """Get just the solution"""
        result = self.analyze_error(error_message)
        return result["solution"]
    
    def should_retry(self, error_message: str) -> bool:
        """Check if error is retryable"""
        result = self.analyze_error(error_message)
        return result["retryable"]
    
    def format_error_response(self, error_message: str) -> str:
        """
        Format complete error response for user
        
        Returns:
            Formatted string with message and solution
        """
        result = self.analyze_error(error_message)
        
        output = []
        output.append("\n" + "=" * 60)
        output.append(" ERROR")
        output.append("=" * 60)
        output.append(f"\n{result['friendly_message']}")
        output.append(f"\nCategory: {result['category'].upper()}")
        output.append(f"Retryable: {'Yes' if result['retryable'] else 'No'}")
        output.append("\n" + "-" * 60)
        output.append(" Suggested Solution:")
        output.append("-" * 60)
        output.append(result["solution"])
        output.append("\n" + "=" * 60 + "\n")
        
        return "\n".join(output)
    
    def get_stats(self) -> Dict:
        """Get error statistics"""
        return self.error_log["stats"]
    
    def display_status(self) -> str:
        """Display error handler status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 60)
        output.append(" " * 15 + "Error Handler Status")
        output.append("=" * 60)
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Errors:     {stats['total_errors']}")
        output.append(f"  Retryable:        {stats['retryable_count']}")
        
        output.append(f"\n[By Category]")
        for category, count in stats.get("by_category", {}).items():
            output.append(f"  {category:15} {count}")
        
        output.append(f"\n[Error Patterns Loaded]")
        output.append(f"  Total patterns:   {sum(len(p['patterns']) for p in self.error_patterns.values())}")
        output.append(f"  Pattern types:    {len(self.error_patterns)}")
        
        output.append("\n" + "=" * 60 + "\n")
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """Test entry point"""
    handler = FriendlyErrorHandler()
    
    print("Friendly Error Handler Test")
    print("=" * 60)
    
    # Display status
    print(handler.display_status())
    
    # Test various errors
    print("\n[Testing Error Analysis]")
    
    test_errors = [
        "fatal: Could not read from remote repository",
        "SyntaxError: invalid syntax",
        "ModuleNotFoundError: No module named 'numpy'",
        "FileNotFoundError: [Errno 2] No such file or directory",
        "TimeoutError: Connection timed out",
        "Unknown error xyz",
    ]
    
    for error in test_errors:
        print(f"\n  Error: {error}")
        result = handler.analyze_error(error)
        print(f"    Message: {result['friendly_message']}")
        print(f"    Category: {result['category']}")
        print(f"    Retryable: {result['retryable']}")
        print(f"    Confidence: {result['confidence']:.0%}")
    
    # Test formatted response
    print("\n[Testing Formatted Response]")
    test_error = "fatal: Authentication failed for 'https://github.com/user/repo.git'"
    print(handler.format_error_response(test_error))
    
    print("\n[OK] Error handler test completed")

if __name__ == "__main__":
    main()
