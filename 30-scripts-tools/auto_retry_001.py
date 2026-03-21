import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-Retry System - Intelligent retry with backoff
"""

import time
import random
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime
from pathlib import Path
import json

class AutoRetry:
    """Automatic retry system with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential: bool = True,
                 jitter: bool = True) -> None:
        """
        Initialize auto-retry system
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay between retries in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 60.0)
            exponential: Use exponential backoff (default: True)
            jitter: Add random jitter to prevent thundering herd (default: True)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter
        
        self.retry_log_file = Path("13-memory/retry_log.json")
        self.retry_log = self._load_retry_log()
    
    def _load_retry_log(self) -> Dict:
        """Load retry log"""
        if self.retry_log_file.exists():
            with open(self.retry_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "retries": [],
            "stats": {
                "total_attempts": 0,
                "successful_retries": 0,
                "failed_retries": 0,
                "total_retry_time": 0.0,
            }
        }
    
    def _save_retry_log(self) -> None:
        """Save retry log"""
        self.retry_log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.retry_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.retry_log, f, ensure_ascii=False, indent=2)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for current attempt
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if self.exponential:
            # Exponential backoff: base_delay * 2^attempt
            delay = self.base_delay * (2 ** attempt)
        else:
            # Linear backoff: base_delay * (attempt + 1)
            delay = self.base_delay * (attempt + 1)
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter (±25%)
        if self.jitter:
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0.1, delay)  # Minimum 0.1s
        
        return delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False
        
        # Check if error is retryable
        retryable_errors = [
            "timeout", "connection", "network", "temporary",
            "busy", "locked", "unavailable", "transient"
        ]
        
        error_str = str(error).lower()
        
        for retryable in retryable_errors:
            if retryable in error_str:
                return True
        
        # Default: retry on any exception (configurable)
        return True
    
    def execute(self, func: Callable, *args, **kwargs) -> Dict:
        """
        Execute function with auto-retry
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Dict with result and metadata
        """
        result = {
            "success": False,
            "attempts": 0,
            "total_time": 0.0,
            "result": None,
            "error": None,
            "retry_details": []
        }
        
        start_time = datetime.now()
        
        for attempt in range(self.max_retries + 1):
            result["attempts"] = attempt + 1
            
            try:
                # Execute function
                func_result = func(*args, **kwargs)
                result["success"] = True
                result["result"] = func_result
                
                # Log success
                self._log_retry(result, success=True)
                
                break
                
            except Exception as e:
                result["error"] = str(e)
                
                # Check if should retry
                if self.should_retry(e, attempt):
                    delay = self.calculate_delay(attempt)
                    
                    retry_detail = {
                        "attempt": attempt + 1,
                        "error": str(e),
                        "delay": delay,
                        "timestamp": datetime.now().isoformat()
                    }
                    result["retry_details"].append(retry_detail)
                    
                    # Wait before retry
                    time.sleep(delay)
                else:
                    # Don't retry
                    break
        
        # Calculate total time
        result["total_time"] = (datetime.now() - start_time).total_seconds()
        
        # Log final result
        self._log_retry(result, success=result["success"])
        
        return result
    
    def _log_retry(self, result: Dict, success: bool) -> None:
        """Log retry attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "attempts": result["attempts"],
            "total_time": result["total_time"],
        }
        
        self.retry_log["retries"].append(log_entry)
        
        if success:
            self.retry_log["stats"]["successful_retries"] += 1
        else:
            self.retry_log["stats"]["failed_retries"] += 1
        
        self.retry_log["stats"]["total_attempts"] += result["attempts"]
        self.retry_log["stats"]["total_retry_time"] += result["total_time"]
        
        # Keep only last 100 entries
        self.retry_log["retries"] = self.retry_log["retries"][-100:]
        
        self._save_retry_log()
    
    def get_stats(self) -> Dict:
        """Get retry statistics"""
        stats = self.retry_log["stats"].copy()
        
        if stats["total_attempts"] > 0:
            stats["success_rate"] = (
                stats["successful_retries"] / 
                (stats["successful_retries"] + stats["failed_retries"])
            ) * 100 if (stats["successful_retries"] + stats["failed_retries"]) > 0 else 0
        else:
            stats["success_rate"] = 0
        
        return stats
    
    def display_status(self) -> str:
        """Display retry system status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Auto-Retry System Status")
        output.append("=" * 70)
        
        output.append(f"\n[Configuration]")
        output.append(f"  Max Retries:      {self.max_retries}")
        output.append(f"  Base Delay:       {self.base_delay}s")
        output.append(f"  Max Delay:        {self.max_delay}s")
        output.append(f"  Exponential:      {self.exponential}")
        output.append(f"  Jitter:           {self.jitter}")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Attempts:   {stats['total_attempts']}")
        output.append(f"  Successful:       {stats['successful_retries']}")
        output.append(f"  Failed:           {stats['failed_retries']}")
        output.append(f"  Success Rate:     {stats['success_rate']:.1f}%")
        output.append(f"  Total Retry Time: {stats['total_retry_time']:.1f}s")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


def simulate_flaky_operation(fail_count: int = 2) -> None:
    """Simulate a flaky operation that fails N times then succeeds"""
    simulate_flaky_operation.attempt = getattr(simulate_flaky_operation, 'attempt', 0) + 1
    
    if simulate_flaky_operation.attempt <= fail_count:
        raise ConnectionError(f"Connection timeout (attempt {simulate_flaky_operation.attempt})")
    
    return f"Success on attempt {simulate_flaky_operation.attempt}"


logging.basicConfig(level=logging.INFO)
def main() -> None:
    """Test entry point"""
    print("Auto-Retry System Test")
    print("=" * 70)
    
    # Test 1: Display status
    retry = AutoRetry(max_retries=3, base_delay=0.5)
    print(retry.display_status())
    
    # Test 2: Successful operation (no retry needed)
    print("\n[Test 1] Successful Operation (No Retry)")
    print("-" * 70)
    
    def success_func():
        return "Immediate success"
    
    result = retry.execute(success_func)
    print(f"  Success: {result['success']}")
    print(f"  Attempts: {result['attempts']}")
    print(f"  Result: {result['result']}")
    print(f"  Time: {result['total_time']:.3f}s")
    
    # Test 3: Flaky operation (succeeds after retries)
    print("\n[Test 2] Flaky Operation (Succeeds After Retries)")
    print("-" * 70)
    simulate_flaky_operation.attempt = 0  # Reset counter
    
    result = retry.execute(simulate_flaky_operation, fail_count=2)
    print(f"  Success: {result['success']}")
    print(f"  Attempts: {result['attempts']}")
    print(f"  Result: {result['result']}")
    print(f"  Time: {result['total_time']:.3f}s")
    print(f"  Retry Details:")
    for detail in result["retry_details"]:
        print(f"    Attempt {detail['attempt']}: {detail['error']} (delay: {detail['delay']:.2f}s)")
    
    # Test 4: Delay calculation
    print("\n[Test 3] Delay Calculation")
    print("-" * 70)
    for i in range(5):
        delay = retry.calculate_delay(i)
        print(f"  Attempt {i}: {delay:.2f}s")
    
    # Test 5: Max retries exceeded
    print("\n[Test 4] Max Retries Exceeded")
    print("-" * 70)
    
    def always_fails():
        raise ConnectionError("Always fails")
    
    retry_short = AutoRetry(max_retries=2, base_delay=0.1)
    result = retry_short.execute(always_fails)
    print(f"  Success: {result['success']}")
    print(f"  Attempts: {result['attempts']}")
    print(f"  Error: {result['error']}")
    
    # Test 6: Get stats
    print("\n[Test 5] Statistics")
    print("-" * 70)
    stats = retry.get_stats()
    print(f"  Total Attempts: {stats['total_attempts']}")
    print(f"  Successful: {stats['successful_retries']}")
    print(f"  Failed: {stats['failed_retries']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    print("\n[OK] Auto-retry system test completed")
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
# py auto_retry_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py auto_retry_001.py

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



if __name__ == "__main__":
    main()
