#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Data Cleaner - Phase 4 Innovation
Automatically cleans and standardizes collected data
Features: deduplication, quality scoring, format standardization, outlier detection

Usage:
    python auto_data_cleaner.py --clean arxiv-data.json
    python auto_data_cleaner.py --scan 20-data-reports/
    python auto_data_cleaner.py --quality
    python auto_data_cleaner.py --report
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set

# Workspace root
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "20-data-reports"
CLEANED_DIR = DATA_DIR / "cleaned"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AutoDataCleaner:
    """Automatically clean and standardize data"""
    
    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'duplicates_removed': 0,
            'low_quality_removed': 0,
            'standardized': 0,
            'outliers_detected': 0
        }
    
    def load_data(self, file_path: Path) -> List[Dict]:
        """Load JSON data file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Handle wrapped data
                if 'items' in data:
                    return data['items']
                elif 'data' in data:
                    return data['data']
                else:
                    return [data]
            else:
                return []
        
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {e}")
            return []
    
    def compute_hash(self, item: Dict) -> str:
        """Compute hash for deduplication"""
        # Use key fields for hashing
        key_fields = ['title', 'url', 'id', 'DOI', 'link']
        key_values = []
        
        for field in key_fields:
            if field in item:
                key_values.append(str(item[field]).lower().strip())
        
        if not key_values:
            # Fallback: use entire item
            key_values = [json.dumps(item, sort_keys=True)]
        
        hash_input = '|'.join(key_values)
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def deduplicate(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicate items"""
        seen_hashes: Set[str] = set()
        unique_items = []
        duplicates = 0
        
        for item in data:
            item_hash = self.compute_hash(item)
            
            if item_hash not in seen_hashes:
                seen_hashes.add(item_hash)
                unique_items.append(item)
            else:
                duplicates += 1
        
        self.stats['duplicates_removed'] += duplicates
        print(f"  Removed {duplicates} duplicates")
        
        return unique_items
    
    def calculate_quality_score(self, item: Dict) -> float:
        """Calculate data quality score (0-1)"""
        score = 0.0
        max_score = 0.0
        
        # Check required fields
        required_fields = ['title', 'url', 'date', 'summary']
        for field in required_fields:
            max_score += 1.0
            if field in item and item[field]:
                score += 1.0
        
        # Check content length
        if 'summary' in item:
            summary_len = len(item['summary'])
            max_score += 1.0
            if summary_len > 100:
                score += 1.0
            elif summary_len > 50:
                score += 0.5
        
        # Check for valid URL
        if 'url' in item:
            max_score += 1.0
            if item['url'].startswith('http'):
                score += 1.0
        
        # Check date format
        if 'date' in item:
            max_score += 1.0
            try:
                datetime.fromisoformat(str(item['date']).replace('Z', '+00:00'))
                score += 1.0
            except:
                pass
        
        return score / max_score if max_score > 0 else 0.0
    
    def filter_by_quality(self, data: List[Dict], min_score: float = 0.5) -> List[Dict]:
        """Filter out low-quality items"""
        filtered = []
        low_quality = 0
        
        for item in data:
            quality_score = self.calculate_quality_score(item)
            item['_quality_score'] = quality_score  # Add score to item
            
            if quality_score >= min_score:
                filtered.append(item)
            else:
                low_quality += 1
        
        self.stats['low_quality_removed'] += low_quality
        print(f"  Removed {low_quality} low-quality items (score < {min_score})")
        
        return filtered
    
    def standardize_format(self, data: List[Dict], source_type: str = None) -> List[Dict]:
        """Standardize data format"""
        standardized = []
        
        for item in data:
            std_item = {}
            
            # Standard field mapping
            field_mappings = {
                'title': ['title', 'Title', 'name', 'Name'],
                'url': ['url', 'URL', 'link', 'Link', 'href'],
                'date': ['date', 'Date', 'published', 'created', 'timestamp'],
                'summary': ['summary', 'Summary', 'abstract', 'description', 'content'],
                'authors': ['authors', 'Authors', 'author', 'Author', 'creators'],
                'tags': ['tags', 'Tags', 'keywords', 'categories'],
                'source': ['source', 'Source', 'platform', 'collection_source']
            }
            
            # Map fields
            for std_field, possible_fields in field_mappings.items():
                for field in possible_fields:
                    if field in item:
                        std_item[std_field] = item[field]
                        break
                
                # If not found, set default
                if std_field not in std_item:
                    if std_field == 'date':
                        std_item[std_field] = datetime.now().isoformat()
                    elif std_field == 'source':
                        std_item[std_field] = source_type or 'unknown'
                    else:
                        std_item[std_field] = ''
            
            # Add metadata
            std_item['_cleaned_at'] = datetime.now().isoformat()
            std_item['_quality_score'] = item.get('_quality_score', 1.0)
            
            standardized.append(std_item)
        
        self.stats['standardized'] += len(standardized)
        print(f"  Standardized {len(standardized)} items")
        
        return standardized
    
    def detect_outliers(self, data: List[Dict]) -> List[Dict]:
        """Detect and flag outliers"""
        if not data:
            return data
        
        # Analyze summary lengths
        summary_lengths = [len(item.get('summary', '')) for item in data]
        
        if len(summary_lengths) < 3:
            return data
        
        # Calculate statistics
        avg_length = sum(summary_lengths) / len(summary_lengths)
        std_dev = (sum((x - avg_length) ** 2 for x in summary_lengths) / len(summary_lengths)) ** 0.5
        
        # Flag outliers (> 3 standard deviations)
        outliers = 0
        for item in data:
            summary_len = len(item.get('summary', ''))
            if std_dev > 0 and abs(summary_len - avg_length) > 3 * std_dev:
                item['_outlier'] = True
                item['_outlier_reason'] = 'unusual_summary_length'
                outliers += 1
            else:
                item['_outlier'] = False
        
        self.stats['outliers_detected'] += outliers
        print(f"  Detected {outliers} outliers")
        
        return data
    
    def clean_file(self, file_path: Path, min_quality: float = 0.5) -> Dict:
        """Clean a single data file"""
        print(f"[CLEAN] Processing {file_path.name}...")
        
        # Load data
        data = self.load_data(file_path)
        if not data:
            return {'error': 'No data loaded', 'file': str(file_path)}
        
        print(f"  Loaded {len(data)} items")
        self.stats['total_processed'] += len(data)
        
        # Step 1: Deduplicate
        data = self.deduplicate(data)
        
        # Step 2: Filter by quality
        data = self.filter_by_quality(data, min_quality)
        
        # Step 3: Standardize format
        source_type = file_path.stem.split('_')[0] if '_' in file_path.stem else 'unknown'
        data = self.standardize_format(data, source_type)
        
        # Step 4: Detect outliers
        data = self.detect_outliers(data)
        
        # Save cleaned data
        output_path = CLEANED_DIR / f"cleaned_{file_path.name}"
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved to {output_path}")
        
        return {
            'file': str(file_path),
            'input_count': len(data),
            'output_count': len(data),
            'output_path': str(output_path),
            'stats': self.stats.copy()
        }
    
    def scan_and_clean(self, dir_path: Path, pattern: str = "*.json") -> List[Dict]:
        """Scan directory and clean all JSON files"""
        print(f"[SCAN] Scanning {dir_path} for {pattern}...")
        
        json_files = list(dir_path.glob(pattern))
        
        # Exclude already cleaned files
        json_files = [f for f in json_files if not f.name.startswith('cleaned_')]
        
        print(f"[SCAN] Found {len(json_files)} data files")
        
        results = []
        for file_path in json_files:
            result = self.clean_file(file_path)
            results.append(result)
            
            # Reset stats for next file
            self.stats = {k: 0 for k in self.stats}
        
        return results
    
    def generate_report(self) -> str:
        """Generate cleaning report"""
        report = f"""# Data Cleaning Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Items Processed | {self.stats.get('total_processed', 0)} |
| Duplicates Removed | {self.stats.get('duplicates_removed', 0)} |
| Low Quality Removed | {self.stats.get('low_quality_removed', 0)} |
| Items Standardized | {self.stats.get('standardized', 0)} |
| Outliers Detected | {self.stats.get('outliers_detected', 0)} |

---

## Quality Distribution

"""
        
        # Analyze cleaned files
        cleaned_files = list(CLEANED_DIR.glob("cleaned_*.json"))
        
        if cleaned_files:
            quality_scores = []
            for file_path in cleaned_files[:10]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    scores = [item.get('_quality_score', 0) for item in data[:100]]
                    quality_scores.extend(scores)
            
            if quality_scores:
                avg_score = sum(quality_scores) / len(quality_scores)
                report += f"- Average Quality Score: {avg_score:.2f}/1.0\n"
                report += f"- Files Analyzed: {len(cleaned_files)}\n"
        
        report += f"""
---

## Output Location

**Cleaned Data:** `{CLEANED_DIR}`

---

*Generated by Auto Data Cleaner (Phase 4 Innovation)*
"""
        
        report_path = DATA_DIR / f"cleaning-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Auto Data Cleaner')
    parser.add_argument('--clean', type=str, help='Clean a single file')
    parser.add_argument('--scan', type=str, help='Scan directory and clean')
    parser.add_argument('--pattern', type=str, default='*.json', help='File pattern')
    parser.add_argument('--min-quality', type=float, default=0.5, help='Minimum quality score')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    cleaner = AutoDataCleaner()
    
    if args.clean:
        file_path = Path(args.clean)
        result = cleaner.clean_file(file_path, args.min_quality)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if args.scan:
        dir_path = Path(args.scan)
        results = cleaner.scan_and_clean(dir_path, args.pattern)
        print(f"\n{'=' * 60}")
        print(f"Cleaned {len(results)} files")
        print(f"{'=' * 60}")
    
    if args.report:
        report = cleaner.generate_report()
        print(report)
    
    if not any([args.clean, args.scan, args.report]):
        parser.print_help()


if __name__ == "__main__":
    main()
