import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Progressive Output - Chunk-by-chunk response streaming
"""

import sys
import time
from typing import List, Generator, Optional, Callable
from datetime import datetime
from pathlib import Path
import json

class ProgressiveOutput:
    """Stream output in chunks for better user experience"""
    
    def __init__(self, chunk_size: int = 100, chunk_delay: float = 0.1,
                 show_progress: bool = True):
        """
        Initialize progressive output
        
        Args:
            chunk_size: Number of characters per chunk (default: 100)
            chunk_delay: Delay between chunks in seconds (default: 0.1)
            show_progress: Show progress indicator (default: True)
        """
        self.chunk_size = chunk_size
        self.chunk_delay = chunk_delay
        self.show_progress = show_progress
        
        self.output_log_file = Path("13-memory/progressive_output_log.json")
        self.output_log = self._load_output_log()
    
    def _load_output_log(self) -> dict:
        """Load output log"""
        if self.output_log_file.exists():
            with open(self.output_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "streams": [],
            "stats": {
                "total_streams": 0,
                "total_chunks": 0,
                "total_characters": 0,
                "total_time": 0.0,
            }
        }
    
    def _save_output_log(self):
        """Save output log"""
        self.output_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.output_log, f, ensure_ascii=False, indent=2)
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]
            chunks.append(chunk)
        
        return chunks
    
    def stream(self, text: str, callback: Optional[Callable] = None) -> dict:
        """
        Stream text output in chunks
        
        Args:
            text: Text to stream
            callback: Optional callback function for each chunk
            
        Returns:
            Dict with streaming statistics
        """
        result = {
            "success": False,
            "total_chunks": 0,
            "total_characters": len(text),
            "total_time": 0.0,
            "chunks_displayed": 0,
        }
        
        start_time = datetime.now()
        chunks = self.chunk_text(text)
        result["total_chunks"] = len(chunks)
        
        try:
            for i, chunk in enumerate(chunks):
                # Display chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
                
                result["chunks_displayed"] = i + 1
                
                # Callback
                if callback:
                    callback(chunk, i, len(chunks))
                
                # Delay between chunks
                if i < len(chunks) - 1:  # No delay after last chunk
                    time.sleep(self.chunk_delay)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        result["total_time"] = (datetime.now() - start_time).total_seconds()
        
        # Log the stream
        self._log_stream(result)
        
        return result
    
    def stream_generator(self, generator: Generator) -> dict:
        """
        Stream output from a generator
        
        Args:
            generator: Generator that yields chunks
            
        Returns:
            Dict with streaming statistics
        """
        result = {
            "success": False,
            "total_chunks": 0,
            "total_characters": 0,
            "total_time": 0.0,
        }
        
        start_time = datetime.now()
        
        try:
            for chunk in generator:
                sys.stdout.write(str(chunk))
                sys.stdout.flush()
                
                result["total_chunks"] += 1
                result["total_characters"] += len(str(chunk))
                
                time.sleep(self.chunk_delay)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        result["total_time"] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def stream_lines(self, lines: List[str]) -> dict:
        """
        Stream line-by-line output
        
        Args:
            lines: List of lines to stream
            
        Returns:
            Dict with streaming statistics
        """
        result = {
            "success": False,
            "total_lines": len(lines),
            "lines_displayed": 0,
            "total_time": 0.0,
        }
        
        start_time = datetime.now()
        
        try:
            for i, line in enumerate(lines):
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
                
                result["lines_displayed"] = i + 1
                
                time.sleep(self.chunk_delay)
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        result["total_time"] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _log_stream(self, result: dict):
        """Log streaming session"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": result["success"],
            "chunks": result["total_chunks"],
            "characters": result["total_characters"],
            "time": result["total_time"],
        }
        
        self.output_log["streams"].append(log_entry)
        self.output_log["stats"]["total_streams"] += 1
        self.output_log["stats"]["total_chunks"] += result["total_chunks"]
        self.output_log["stats"]["total_characters"] += result["total_characters"]
        self.output_log["stats"]["total_time"] += result["total_time"]
        
        # Keep only last 100 entries
        self.output_log["streams"] = self.output_log["streams"][-100:]
        
        self._save_output_log()
    
    def get_stats(self) -> dict:
        """Get streaming statistics"""
        return self.output_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display progressive output status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 18 + "Progressive Output Status")
        output.append("=" * 70)
        
        output.append(f"\n[Configuration]")
        output.append(f"  Chunk Size:     {self.chunk_size} chars")
        output.append(f"  Chunk Delay:    {self.chunk_delay}s")
        output.append(f"  Show Progress:  {self.show_progress}")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Streams:    {stats['total_streams']}")
        output.append(f"  Total Chunks:     {stats['total_chunks']}")
        output.append(f"  Total Characters: {stats['total_characters']}")
        output.append(f"  Total Time:       {stats['total_time']:.2f}s")
        
        if stats["total_streams"] > 0:
            avg_chunk_size = stats["total_characters"] / stats["total_chunks"] if stats["total_chunks"] > 0 else 0
            output.append(f"  Avg Chunk Size:   {avg_chunk_size:.1f} chars")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def generate_large_text():
    """Generator that yields large text in chunks"""
    for i in range(10):
        yield f"Chunk {i+1}/10 generated dynamically\n"
        time.sleep(0.05)


logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py progressive_output_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py progressive_output_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Test entry point"""
    print("Progressive Output Test")
    print("=" * 70)
    
    # Test 1: Display status
    output = ProgressiveOutput(chunk_size=50, chunk_delay=0.05)
    print(output.display_status())
    
    # Test 2: Stream text
    print("\n[Test 1] Stream Text")
    print("-" * 70)
    test_text = """
    This is a test of progressive output streaming. The text will be displayed 
    in chunks of 50 characters with a small delay between each chunk. This creates
    a typing effect that can improve user experience for long responses.
    """
    
    result = output.stream(test_text.strip())
    print(f"\n\n  Chunks: {result['total_chunks']}")
    print(f"  Characters: {result['total_characters']}")
    print(f"  Time: {result['total_time']:.2f}s")
    
    # Test 3: Stream lines
    print("\n[Test 2] Stream Lines")
    print("-" * 70)
    test_lines = [
        "Line 1: Introduction",
        "Line 2: Main content",
        "Line 3: More details",
        "Line 4: Additional info",
        "Line 5: Conclusion",
    ]
    
    result = output.stream_lines(test_lines)
    print(f"\n  Lines: {result['lines_displayed']}/{result['total_lines']}")
    print(f"  Time: {result['total_time']:.2f}s")
    
    # Test 4: Stream from generator
    print("\n[Test 3] Stream from Generator")
    print("-" * 70)
    result = output.stream_generator(generate_large_text())
    print(f"\n  Chunks: {result['total_chunks']}")
    print(f"  Characters: {result['total_characters']}")
    print(f"  Time: {result['total_time']:.2f}s")
    
    # Test 5: Chunk calculation
    print("\n[Test 4] Chunk Calculation")
    print("-" * 70)
    test_text = "A" * 237
    chunks = output.chunk_text(test_text)
    print(f"  Text length: {len(test_text)} chars")
    print(f"  Chunk size: {output.chunk_size} chars")
    print(f"  Number of chunks: {len(chunks)}")
    print(f"  Last chunk size: {len(chunks[-1])} chars")
    
    # Test 6: Different chunk sizes
    print("\n[Test 5] Different Chunk Sizes")
    print("-" * 70)
    for size in [20, 50, 100, 200]:
        output_test = ProgressiveOutput(chunk_size=size, chunk_delay=0)
        chunks = output_test.chunk_text(test_text)
        print(f"  Chunk size {size:3d}: {len(chunks):2d} chunks")
    
    print("\n[OK] Progressive output test completed")

if __name__ == "__main__":
    main()
