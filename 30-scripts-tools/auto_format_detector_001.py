#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-Format Detector - Smart format selection based on content type
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class AutoFormatDetector:
    """Automatically detect optimal output format based on content"""
    
    def __init__(self):
        self.format_rules = self._load_format_rules()
    
    def _load_format_rules(self) -> Dict:
        """Load format detection rules"""
        return {
            "table": {
                "triggers": [
                    "comparison", "compare", "vs", "versus",
                    "table", "grid", "matrix",
                    "feature", "specification", "specs",
                    "price", "cost", "rating",
                ],
                "data_types": [list, dict],
                "min_items": 2,
                "description": "Use table for comparisons and structured data"
            },
            "list": {
                "triggers": [
                    "list", "items", "points", "steps",
                    "first", "second", "third",
                    "bullet", "numbered",
                    "recommendation", "suggestion", "option",
                ],
                "data_types": [list],
                "min_items": 1,
                "description": "Use list for sequential or enumerated items"
            },
            "code_block": {
                "triggers": [
                    "code", "script", "function", "def",
                    "import", "class", "return",
                    "example", "snippet",
                ],
                "data_types": [str],
                "patterns": [r"def\s+\w+", r"import\s+\w+", r"class\s+\w+", r"function\s+\w+"],
                "description": "Use code block for programming code"
            },
            "json": {
                "triggers": [
                    "json", "config", "configuration", "settings",
                    "object", "dictionary", "map",
                ],
                "data_types": [dict],
                "description": "Use JSON format for structured data"
            },
            "text": {
                "triggers": [],
                "data_types": [str],
                "description": "Use plain text for narrative content"
            }
        }
    
    def detect_format(self, content: Any, context: Dict = None) -> Dict:
        """
        Detect optimal format for content
        
        Args:
            content: Content to format
            context: Optional context (keywords, user preference, etc.)
            
        Returns:
            Dict with format recommendation and metadata
        """
        result = {
            "recommended_format": "text",
            "confidence": 0.5,
            "reason": "Default format",
            "alternative_formats": [],
            "format_options": {}
        }
        
        # Check data type
        content_type = type(content)
        
        # Rule 1: List data -> list format
        if isinstance(content, list):
            if len(content) >= 2:
                result["recommended_format"] = "list"
                result["confidence"] = 0.8
                result["reason"] = f"List data with {len(content)} items"
                
                # Check if it looks like a comparison
                if isinstance(content[0], dict):
                    result["recommended_format"] = "table"
                    result["confidence"] = 0.9
                    result["reason"] = "List of dictionaries (table-ready)"
                    result["format_options"] = {
                        "columns": list(content[0].keys()) if content else [],
                        "rows": len(content)
                    }
        
        # Rule 2: Dict data -> JSON or table
        elif isinstance(content, dict):
            if len(content) > 5:
                result["recommended_format"] = "json"
                result["confidence"] = 0.8
                result["reason"] = "Complex dictionary (JSON format)"
            else:
                result["recommended_format"] = "list"
                result["confidence"] = 0.7
                result["reason"] = "Simple dictionary (key-value list)"
        
        # Rule 3: String content -> check triggers
        elif isinstance(content, str):
            content_lower = content.lower()
            
            # Check for code patterns
            import re
            code_patterns = [r"def\s+\w+", r"import\s+\w+", r"class\s+\w+", r"function\s+\w+", r"#!/usr/bin"]
            for pattern in code_patterns:
                if re.search(pattern, content):
                    result["recommended_format"] = "code_block"
                    result["confidence"] = 0.95
                    result["reason"] = "Code pattern detected"
                    break
            
            # Check for table triggers
            if result["recommended_format"] != "code_block":
                for trigger in self.format_rules["table"]["triggers"]:
                    if trigger in content_lower:
                        result["recommended_format"] = "table"
                        result["confidence"] = 0.7
                        result["reason"] = f"Table trigger: '{trigger}'"
                        break
            
            # Check for list triggers
            if result["recommended_format"] == "text":
                for trigger in self.format_rules["list"]["triggers"]:
                    if trigger in content_lower:
                        result["recommended_format"] = "list"
                        result["confidence"] = 0.6
                        result["reason"] = f"List trigger: '{trigger}'"
                        break
        
        # Apply context overrides
        if context:
            if "user_preference" in context:
                result["recommended_format"] = context["user_preference"]
                result["reason"] = f"User preference override"
                result["confidence"] = 1.0
            
            if "force_format" in context:
                result["recommended_format"] = context["force_format"]
                result["reason"] = "Force format override"
                result["confidence"] = 1.0
        
        return result
    
    def format_content(self, content: Any, format_type: str = None) -> str:
        """
        Format content according to detected or specified format
        
        Args:
            content: Content to format
            format_type: Optional format override
            
        Returns:
            Formatted string
        """
        if format_type is None:
            detection = self.detect_format(content)
            format_type = detection["recommended_format"]
        
        if format_type == "table":
            return self._format_as_table(content)
        elif format_type == "list":
            return self._format_as_list(content)
        elif format_type == "json":
            return self._format_as_json(content)
        elif format_type == "code_block":
            return self._format_as_code(content)
        else:
            return str(content)
    
    def _format_as_table(self, content: Any) -> str:
        """Format as markdown table"""
        if isinstance(content, list) and content and isinstance(content[0], dict):
            headers = list(content[0].keys())
            rows = [list(item.values()) for item in content]
            
            # Calculate column widths
            widths = [len(h) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    widths[i] = max(widths[i], len(str(cell)))
            
            # Build table
            lines = []
            header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
            lines.append(header_line)
            lines.append("-+-".join("-" * w for w in widths))
            
            for row in rows:
                row_line = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
                lines.append(row_line)
            
            return "\n".join(lines)
        
        return str(content)
    
    def _format_as_list(self, content: Any) -> str:
        """Format as bullet list"""
        if isinstance(content, list):
            return "\n".join(f"  - {item}" for item in content)
        elif isinstance(content, dict):
            return "\n".join(f"  - {k}: {v}" for k, v in content.items())
        else:
            return f"  - {content}"
    
    def _format_as_json(self, content: Any) -> str:
        """Format as JSON"""
        return json.dumps(content, indent=2, ensure_ascii=False)
    
    def _format_as_code(self, content: Any) -> str:
        """Format as code block"""
        return f"```\n{content}\n```"
    
    def get_stats(self) -> Dict:
        """Get format detection statistics"""
        return {
            "format_rules": len(self.format_rules),
            "supported_formats": list(self.format_rules.keys()),
        }
    
    def display_status(self) -> str:
        """Display detector status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 60)
        output.append(" " * 15 + "Auto-Format Detector Status")
        output.append("=" * 60)
        
        output.append(f"\n[Supported Formats]")
        for fmt in stats["supported_formats"]:
            desc = self.format_rules[fmt]["description"]
            output.append(f"  {fmt:15} - {desc}")
        
        output.append(f"\n[Format Rules]")
        output.append(f"  Total rules: {stats['format_rules']}")
        
        output.append("\n" + "=" * 60 + "\n")
        
        return "\n".join(output)

def main():
    """Test entry point"""
    detector = AutoFormatDetector()
    
    print("Auto-Format Detector Test")
    print("=" * 60)
    
    # Display status
    print(detector.display_status())
    
    # Test 1: List detection
    print("\n[Test 1] List Detection")
    test_list = ["Item 1", "Item 2", "Item 3"]
    result = detector.detect_format(test_list)
    print(f"  Input: {test_list}")
    print(f"  Format: {result['recommended_format']} ({result['confidence']:.0%})")
    print(f"  Reason: {result['reason']}")
    
    # Test 2: Table detection
    print("\n[Test 2] Table Detection")
    test_table = [
        {"Name": "Alice", "Age": 30, "City": "NYC"},
        {"Name": "Bob", "Age": 25, "City": "LA"},
    ]
    result = detector.detect_format(test_table)
    print(f"  Input: {len(test_table)} records")
    print(f"  Format: {result['recommended_format']} ({result['confidence']:.0%})")
    print(f"  Reason: {result['reason']}")
    
    # Test 3: Code detection
    print("\n[Test 3] Code Detection")
    test_code = "def hello():\n    return 'world'"
    result = detector.detect_format(test_code)
    print(f"  Input: {test_code[:30]}...")
    print(f"  Format: {result['recommended_format']} ({result['confidence']:.0%})")
    print(f"  Reason: {result['reason']}")
    
    # Test 4: Formatted output
    print("\n[Test 4] Formatted Output")
    print("-" * 60)
    print("Table format:")
    print(detector.format_content(test_table))
    
    print("\nList format:")
    print(detector.format_content(["A", "B", "C"]))
    
    print("\nJSON format:")
    print(detector.format_content({"key": "value"}))
    
    print("\n[OK] Auto-format detector test completed")

if __name__ == "__main__":
    main()
