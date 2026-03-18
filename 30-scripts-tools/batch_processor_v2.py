#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Processor v2.0 - Parallel processing with progress tracking

Features:
- Parallel processing (ThreadPoolExecutor)
- Progress bar with ETA
- Smart retry logic
- Resource management
- Result aggregation

Author: OpenClaw Team
Date: 2026-03-16
Version: 2.0
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# UTF-8 encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class BatchProcessorV2:
    """Advanced batch processor with parallel execution"""
    
    def __init__(self, max_workers: int = 4, retry_count: int = 3):
        self.max_workers = max_workers
        self.retry_count = retry_count
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def _process_item(self, item: Any, processor_func: Callable, item_id: str) -> Dict:
        """Process single item with retry logic"""
        for attempt in range(1, self.retry_count + 1):
            try:
                result = processor_func(item)
                return {
                    'id': item_id,
                    'success': True,
                    'result': result,
                    'attempts': attempt,
                    'error': None
                }
            except Exception as e:
                if attempt == self.retry_count:
                    return {
                        'id': item_id,
                        'success': False,
                        'result': None,
                        'attempts': attempt,
                        'error': str(e)
                    }
                time.sleep(1 * attempt)  # Exponential backoff
    
    def process_batch(self, 
                      items: List[Any], 
                      processor_func: Callable,
                      item_ids: Optional[List[str]] = None,
                      show_progress: bool = True) -> Dict:
        """Process batch of items in parallel"""
        
        self.start_time = datetime.now()
        self.results = []
        self.errors = []
        
        if not item_ids:
            item_ids = [f"item_{i}" for i in range(len(items))]
        
        total = len(items)
        processed = 0
        successful = 0
        failed = 0
        
        print(f"\n🔄 Starting batch processing ({total} items, {self.max_workers} workers)\n")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_id = {
                executor.submit(self._process_item, item, processor_func, item_id): item_id
                for item, item_id in zip(items, item_ids)
            }
            
            # Process results with progress bar
            if show_progress:
                with tqdm(total=total, desc="Processing", unit="item") as pbar:
                    for future in as_completed(future_to_id):
                        item_id = future_to_id[future]
                        try:
                            result = future.result()
                            self.results.append(result)
                            
                            if result['success']:
                                successful += 1
                            else:
                                failed += 1
                                self.errors.append(result)
                            
                            processed += 1
                            pbar.set_postfix({
                                'success': successful,
                                'failed': failed
                            })
                            pbar.update(1)
                            
                        except Exception as e:
                            failed += 1
                            self.errors.append({
                                'id': item_id,
                                'success': False,
                                'error': str(e)
                            })
                            processed += 1
                            pbar.update(1)
            else:
                # Without progress bar
                for future in as_completed(future_to_id):
                    item_id = future_to_id[future]
                    try:
                        result = future.result()
                        self.results.append(result)
                        
                        if result['success']:
                            successful += 1
                        else:
                            failed += 1
                            self.errors.append(result)
                            
                    except Exception as e:
                        failed += 1
                        self.errors.append({
                            'id': item_id,
                            'success': False,
                            'error': str(e)
                        })
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        stats = {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'duration_seconds': duration,
            'items_per_second': (total / duration) if duration > 0 else 0,
            'avg_attempts': sum(r.get('attempts', 1) for r in self.results) / len(self.results) if self.results else 0
        }
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 Batch Processing Summary:")
        print(f"{'='*70}")
        print(f"  Total items:      {total}")
        print(f"  Successful:       {successful} ({stats['success_rate']:.1f}%)")
        print(f"  Failed:           {failed}")
        print(f"  Duration:         {duration:.2f}s")
        print(f"  Throughput:       {stats['items_per_second']:.2f} items/s")
        print(f"  Avg attempts:     {stats['avg_attempts']:.2f}")
        print(f"{'='*70}\n")
        
        return {
            'success': True,
            'stats': stats,
            'results': self.results,
            'errors': self.errors,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
    
    def save_results(self, output_file: str, format: str = 'json'):
        """Save processing results"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'processed_at': datetime.now().isoformat(),
            'stats': {
                'total': len(self.results),
                'successful': sum(1 for r in self.results if r['success']),
                'failed': len(self.errors)
            },
            'results': self.results,
            'errors': self.errors
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
    
    def get_summary(self) -> Dict:
        """Get processing summary"""
        return {
            'total': len(self.results),
            'successful': sum(1 for r in self.results if r['success']),
            'failed': len(self.errors),
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        }


def demo():
    """Run batch processor demo"""
    print("\n⚡ Batch Processor v2.0 Demo\n")
    
    # Sample data
    items = list(range(20))
    item_ids = [f"task_{i}" for i in range(20)]
    
    # Sample processor function
    def sample_processor(item):
        time.sleep(0.5)  # Simulate work
        if item % 10 == 0:
            raise Exception(f"Simulated error for {item}")
        return item * 2
    
    # Process batch
    processor = BatchProcessorV2(max_workers=4, retry_count=2)
    results = processor.process_batch(
        items=items,
        processor_func=sample_processor,
        item_ids=item_ids,
        show_progress=True
    )
    
    # Save results
    processor.save_results('data/batch_results.json')
    
    # Show summary
    summary = processor.get_summary()
    print(f"\n📋 Summary:")
    print(f"  Total: {summary['total']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Duration: {summary['duration']:.2f}s")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch Processor v2.0')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--workers', type=int, default=4, help='Max workers')
    parser.add_argument('--retries', type=int, default=3, help='Retry count')
    args = parser.parse_args()
    
    if args.demo:
        demo()
    else:
        demo()


if __name__ == "__main__":
    main()
