import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Typing Indicator - Show activity during long operations
"""

import sys
import time
import threading
from datetime import datetime
from typing import Optional, Callable

class TypingIndicator:
    """Display typing/activity indicator during long operations"""
    
    def __init__(self, delay_seconds: float = 2.0, update_interval: float = 5.0) -> None:
        """
        Initialize typing indicator
        
        Args:
            delay_seconds: Wait this long before showing indicator (default: 2s)
            update_interval: Update indicator message every N seconds (default: 5s)
        """
        self.delay_seconds = delay_seconds
        self.update_interval = update_interval
        self.is_running = False
        self.indicator_thread: Optional[threading.Thread] = None
        self.messages = [
            "Thinking...",
            "Working on it...",
            "Processing...",
            "Almost done...",
        ]
        self.current_message_index = 0
        self.start_time: Optional[datetime] = None
    
    def _display_indicator(self) -> None:
        """Internal method to display indicator (runs in separate thread)"""
        time.sleep(self.delay_seconds)
        
        if not self.is_running:
            return
        
        self.start_time = datetime.now()
        
        while self.is_running:
            message = self.messages[self.current_message_index % len(self.messages)]
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            # Show message with elapsed time
            sys.stdout.write(f"\r[{message} {elapsed:.1f}s] ")
            sys.stdout.flush()
            
            self.current_message_index += 1
            time.sleep(self.update_interval)
        
        # Clear the indicator line
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
    
    def start(self) -> None:
        """Start the typing indicator"""
        self.is_running = True
        self.current_message_index = 0
        self.indicator_thread = threading.Thread(target=self._display_indicator, daemon=True)
        self.indicator_thread.start()
    
    def stop(self) -> None:
        """Stop the typing indicator"""
        self.is_running = False
        if self.indicator_thread and self.indicator_thread.is_alive():
            self.indicator_thread.join(timeout=1.0)
    
    def __enter__(self) -> None:
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        self.stop()
    
    def elapsed_time(self) -> float:
        """Get elapsed time since indicator started"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0


def with_typing_indicator(func: Callable) -> None:
    """
    Decorator to automatically show typing indicator for long operations
    
    Usage:
        @with_typing_indicator
        def long_operation():
            time.sleep(5)
    """
    def wrapper(*args, **kwargs):
        indicator = TypingIndicator()
        try:
            indicator.start()
            return func(*args, **kwargs)
        finally:
            indicator.stop()
    return wrapper


def simulate_long_operation(duration: float, description: str = "Operation") -> None:
    """Simulate a long operation with typing indicator"""
    print(f"\nStarting: {description}")
    print("-" * 60)
    
    indicator = TypingIndicator(delay_seconds=1.0, update_interval=2.0)
    
    try:
        indicator.start()
        time.sleep(duration)
        result = f"Completed in {duration:.1f}s"
    finally:
        indicator.stop()
    
    print(f"{description} {result}")
    return result


logging.basicConfig(level=logging.INFO)
def main() -> None:
    """Test entry point"""
    print("Typing Indicator Test")
    print("=" * 60)
    
    # Test 1: Context manager
    print("\n[Test 1] Context Manager")
    with TypingIndicator(delay_seconds=1.0, update_interval=2.0) as indicator:
        time.sleep(5)
    print("Context manager test completed")
    
    # Test 2: Manual start/stop
    print("\n[Test 2] Manual Start/Stop")
    indicator = TypingIndicator(delay_seconds=1.0, update_interval=2.0)
    indicator.start()
    time.sleep(4)
    indicator.stop()
    print("Manual control test completed")
    
    # Test 3: Simulated operation
    print("\n[Test 3] Simulated Long Operation")
    simulate_long_operation(3.0, "Data Processing")
    
    # Test 4: Elapsed time tracking
    print("\n[Test 4] Elapsed Time Tracking")
    indicator = TypingIndicator(delay_seconds=0.5, update_interval=1.0)
    indicator.start()
    time.sleep(3)
    elapsed = indicator.elapsed_time()
    indicator.stop()
    print(f"Elapsed time: {elapsed:.2f}s")
    
    # Test 5: Quick operation (should not show indicator)
    print("\n[Test 5] Quick Operation (No Indicator)")
    print("Starting quick operation...")
    time.sleep(0.5)  # Less than delay
    print("Quick operation completed (indicator should not have shown)")
    
    print("\n[OK] Typing indicator test completed")

if __name__ == "__main__":
    main()
