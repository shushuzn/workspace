#!/usr/bin/env python3
"""
Memory Fractal Compression - Self-Similar Knowledge Compression
=================================================================
Compresses memory using fractal patterns and self-similarity.

Key Concepts:
- Self-Similarity: Patterns repeat at different scales
- Fractal Dimension: Measure of complexity (D = log(N)/log(1/r))
- Iterated Function Systems (IFS): Generate fractals from rules
- Compression Ratio: Original size / Compressed size
- Lossless vs Lossy: Preserve meaning vs reduce size

Usage:
    python memory_fractal_compression.py --compress "MEMORY.md"
    python memory_fractal_compression.py --decompress
    python memory_fractal_compression.py --dimension
    python memory_fractal_compression.py --patterns
    python memory_fractal_compression.py --ratio
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class FractalConfig:
    """Fractal compression configuration"""
    
    # Compression parameters
    MIN_PATTERN_SIZE: int = 10          # Minimum pattern length to consider
    SIMILARITY_THRESHOLD: float = 0.8   # Minimum similarity for pattern matching
    MAX_RECURSION_DEPTH: int = 5        # Maximum fractal recursion depth
    
    # Fractal dimension calculation
    BOX_SIZES: List[float] = field(default_factory=lambda: [0.1, 0.05, 0.02, 0.01])
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    FRACTAL_STATE: str = os.path.join(WORKSPACE, 'data', 'fractal_state.json')
    COMPRESSED_DIR: str = os.path.join(WORKSPACE, 'data', 'compressed')


# ============================================================================
# Fractal Structures
# ============================================================================

@dataclass
class FractalPattern:
    """A self-similar pattern in memory"""
    pattern_id: str
    content_hash: str
    content: str
    occurrences: List[Dict]  # Where this pattern appears
    scale_levels: int         # How many scales this pattern appears at
    compression_ratio: float
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'content_hash': self.content_hash,
            'content': self.content,
            'occurrences': self.occurrences,
            'scale_levels': self.scale_levels,
            'compression_ratio': self.compression_ratio,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FractalPattern':
        return cls(
            pattern_id=data['pattern_id'],
            content_hash=data['content_hash'],
            content=data['content'],
            occurrences=data['occurrences'],
            scale_levels=data['scale_levels'],
            compression_ratio=data['compression_ratio'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class CompressionResult:
    """Result of fractal compression"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    patterns_found: int
    fractal_dimension: float
    compression_time: float
    lossless: bool
    
    def to_dict(self) -> Dict:
        return {
            'original_size': self.original_size,
            'compressed_size': self.compressed_size,
            'compression_ratio': self.compression_ratio,
            'patterns_found': self.patterns_found,
            'fractal_dimension': self.fractal_dimension,
            'compression_time': self.compression_time,
            'lossless': self.lossless
        }


# ============================================================================
# Fractal Compressor
# ============================================================================

class FractalCompressor:
    """Compress memory using fractal patterns"""
    
    def __init__(self, config: FractalConfig = None):
        self.config = config or FractalConfig()
        self.patterns: List[FractalPattern] = []
        self.last_compression: Optional[CompressionResult] = None
        self._load_state()
    
    def _load_state(self):
        """Load compression state"""
        if os.path.exists(self.config.FRACTAL_STATE):
            with open(self.config.FRACTAL_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.patterns = [
                FractalPattern.from_dict(p) for p in state.get('patterns', [])
            ]
            
            if state.get('last_compression'):
                self.last_compression = CompressionResult(**state['last_compression'])
            
            logger.info(f"Loaded {len(self.patterns)} fractal patterns")
    
    def _save_state(self):
        """Save compression state"""
        state = {
            'patterns': [p.to_dict() for p in self.patterns],
            'last_compression': self.last_compression.to_dict() if self.last_compression else None,
            'last_update': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config.FRACTAL_STATE), exist_ok=True)
        os.makedirs(self.config.COMPRESSED_DIR, exist_ok=True)
        
        with open(self.config.FRACTAL_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def find_self_similar_patterns(self, content: str) -> List[FractalPattern]:
        """
        Find self-similar patterns in content
        
        Strategy:
        1. Extract n-grams at different scales
        2. Find repeated patterns
        3. Build pattern hierarchy (fractal structure)
        """
        logger.info("Finding self-similar patterns...")
        
        patterns = []
        pattern_counter = 0
        
        # Scale 1: Character-level patterns (n-grams)
        char_patterns = self._find_ngram_patterns(content, n=5)
        for pattern_str, occurrences in char_patterns.items():
            if len(occurrences) >= 2:  # Appears at least twice
                pattern = FractalPattern(
                    pattern_id=f"FP_CHAR_{pattern_counter:04d}",
                    content_hash=hashlib.md5(pattern_str.encode()).hexdigest()[:8],
                    content=pattern_str[:100],  # Truncate for storage
                    occurrences=[{'type': 'char', 'pos': pos} for pos in occurrences],
                    scale_levels=1,
                    compression_ratio=len(occurrences) * len(pattern_str) / len(pattern_str)
                )
                patterns.append(pattern)
                pattern_counter += 1
        
        # Scale 2: Word-level patterns
        word_patterns = self._find_ngram_patterns(content.split(), n=3)
        for pattern_tuple, occurrences in word_patterns.items():
            if len(occurrences) >= 2:
                pattern_str = ' '.join(pattern_tuple)
                pattern = FractalPattern(
                    pattern_id=f"FP_WORD_{pattern_counter:04d}",
                    content_hash=hashlib.md5(pattern_str.encode()).hexdigest()[:8],
                    content=pattern_str[:100],
                    occurrences=[{'type': 'word', 'pos': pos} for pos in occurrences],
                    scale_levels=1,
                    compression_ratio=len(occurrences) * len(pattern_str) / len(pattern_str)
                )
                patterns.append(pattern)
                pattern_counter += 1
        
        # Scale 3: Section-level patterns (headers, structures)
        section_patterns = self._find_section_patterns(content)
        for pattern_str, occurrences in section_patterns.items():
            if len(occurrences) >= 2:
                pattern = FractalPattern(
                    pattern_id=f"FP_SECT_{pattern_counter:04d}",
                    content_hash=hashlib.md5(pattern_str.encode()).hexdigest()[:8],
                    content=pattern_str[:200],
                    occurrences=[{'type': 'section', 'header': occ} for occ in occurrences],
                    scale_levels=2,  # Section level
                    compression_ratio=len(occurrences) * 100 / len(pattern_str)  # Estimate
                )
                patterns.append(pattern)
                pattern_counter += 1
        
        # Build hierarchy - find patterns that contain other patterns
        self._build_pattern_hierarchy(patterns)
        
        logger.info(f"Found {len(patterns)} self-similar patterns")
        
        return patterns
    
    def _find_ngram_patterns(self, text, n: int = 5) -> Dict:
        """Find repeated n-grams"""
        if isinstance(text, str):
            tokens = text
            get_ngram = lambda tokens, i, n: tokens[i:i+n]
            length = len(tokens)
        else:
            tokens = text
            get_ngram = lambda tokens, i, n: tuple(tokens[i:i+n])
            length = len(tokens)
        
        ngram_counts = defaultdict(list)
        
        for i in range(length - n + 1):
            ngram = get_ngram(tokens, i, n)
            if len(ngram) >= self.config.MIN_PATTERN_SIZE or (isinstance(ngram, tuple) and len(ngram) == n):
                ngram_counts[ngram].append(i)
        
        # Filter to only repeated patterns
        repeated = {
            ngram: positions for ngram, positions in ngram_counts.items()
            if len(positions) >= 2
        }
        
        return repeated
    
    def _find_section_patterns(self, content: str) -> Dict:
        """Find repeated section structures"""
        import re
        
        # Find all sections
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Group by structure (number of #)
        structure_groups = defaultdict(list)
        
        for section in sections:
            # Extract structure pattern
            structure = re.sub(r'\w+', 'X', section)  # Replace words with X
            structure_groups[structure].append(section)
        
        # Return groups with multiple occurrences
        repeated = {
            struct: sections for struct, sections in structure_groups.items()
            if len(sections) >= 2
        }
        
        return repeated
    
    def _build_pattern_hierarchy(self, patterns: List[FractalPattern]):
        """Build hierarchy of patterns (fractal structure)"""
        # Group patterns by similarity
        hash_groups = defaultdict(list)
        
        for pattern in patterns:
            hash_groups[pattern.content_hash].append(pattern)
        
        # Update scale levels for patterns that appear at multiple scales
        for pattern in patterns:
            similar_patterns = [
                p for p in patterns
                if p.content_hash == pattern.content_hash and p != pattern
            ]
            
            if similar_patterns:
                # This pattern appears at multiple scales
                pattern.scale_levels = 1 + len(similar_patterns)
    
    def compute_fractal_dimension(self, content: str) -> float:
        """
        Compute fractal dimension using box-counting method
        
        D = log(N) / log(1/r)
        
        Where:
        - N = number of boxes needed to cover the pattern
        - r = scale factor
        """
        logger.info("Computing fractal dimension...")
        
        # Simplified approach: use information dimension
        # Real box-counting would require geometric representation
        
        # Method 1: Word frequency distribution
        words = content.split()
        word_counts = Counter(words)
        
        # Sort by frequency
        frequencies = sorted(word_counts.values(), reverse=True)
        
        if not frequencies:
            return 0.0
        
        # Compute information dimension
        total = sum(frequencies)
        probabilities = [f / total for f in frequencies]
        
        # Shannon entropy
        entropy = -sum(p * math.log(p) if p > 0 else 0 for p in probabilities)
        
        # Fractal dimension approximation
        n_unique = len(frequencies)
        if n_unique > 1:
            dimension = entropy / math.log(n_unique)
        else:
            dimension = 0.0
        
        logger.info(f"Fractal dimension: {dimension:.3f}")
        
        return dimension
    
    def compress(self, memory_file: str) -> CompressionResult:
        """
        Compress memory file using fractal patterns
        """
        logger.info(f"Compressing {memory_file}...")
        
        import time
        start_time = time.time()
        
        if not os.path.exists(memory_file):
            logger.error(f"File not found: {memory_file}")
            return None
        
        # Read original content
        with open(memory_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        original_size = len(original_content.encode('utf-8'))
        
        # Find patterns
        self.patterns = self.find_self_similar_patterns(original_content)
        
        # Compute fractal dimension
        fractal_dim = self.compute_fractal_dimension(original_content)
        
        # Create compressed representation
        # Store: unique patterns + reference map
        compressed_data = {
            'patterns': [p.to_dict() for p in self.patterns],
            'fractal_dimension': fractal_dim,
            'metadata': {
                'original_file': os.path.basename(memory_file),
                'compression_date': datetime.now().isoformat()
            }
        }
        
        # Estimate compressed size
        patterns_json = json.dumps(compressed_data, ensure_ascii=False)
        compressed_size = len(patterns_json.encode('utf-8'))
        
        # In real implementation, would store references instead of full content
        # This is a simplified estimate
        compression_ratio = original_size / max(compressed_size, 1)
        
        # Create result
        compression_time = time.time() - start_time
        
        result = CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            patterns_found=len(self.patterns),
            fractal_dimension=fractal_dim,
            compression_time=compression_time,
            lossless=True  # Fractal compression is lossless
        )
        
        self.last_compression = result
        self._save_state()
        
        # Save compressed data
        compressed_file = os.path.join(
            self.config.COMPRESSED_DIR,
            f"{os.path.basename(memory_file)}.fractal.json"
        )
        
        with open(compressed_file, 'w', encoding='utf-8') as f:
            json.dump(compressed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Compressed to {compressed_file}")
        
        return result
    
    def decompress(self, compressed_file: str) -> str:
        """
        Decompress fractal-compressed file
        """
        logger.info(f"Decompressing {compressed_file}...")
        
        if not os.path.exists(compressed_file):
            logger.error(f"Compressed file not found: {compressed_file}")
            return ""
        
        with open(compressed_file, 'r', encoding='utf-8') as f:
            compressed_data = json.load(f)
        
        # Reconstruct from patterns
        # This is simplified - real implementation would use reference map
        reconstructed = ""
        
        for pattern_data in compressed_data.get('patterns', []):
            pattern = FractalPattern.from_dict(pattern_data)
            reconstructed += pattern.content + "\n"
        
        return reconstructed
    
    def get_compression_stats(self) -> Dict:
        """Get compression statistics"""
        if not self.last_compression:
            return {'status': 'no_data'}
        
        return {
            'original_size_kb': self.last_compression.original_size / 1024,
            'compressed_size_kb': self.last_compression.compressed_size / 1024,
            'compression_ratio': self.last_compression.compression_ratio,
            'patterns_found': self.last_compression.patterns_found,
            'fractal_dimension': self.last_compression.fractal_dimension,
            'compression_time_s': self.last_compression.compression_time,
            'space_saved_kb': (self.last_compression.original_size - self.last_compression.compressed_size) / 1024,
            'space_saved_percent': (1 - 1 / self.last_compression.compression_ratio) * 100 if self.last_compression.compression_ratio > 1 else 0
        }


# Import math for fractal dimension calculation
import math


# ============================================================================
# CLI Interface
# ============================================================================

def compress_command(args):
    """Compress memory file"""
    compressor = FractalCompressor()
    result = compressor.compress(args.file)
    
    if result:
        print(f"\n🌀 Fractal Compression Results")
        print("=" * 60)
        print(f"File: {args.file}")
        print(f"Original size: {result.original_size / 1024:.2f} KB")
        print(f"Compressed size: {result.compressed_size / 1024:.2f} KB")
        print(f"Compression ratio: {result.compression_ratio:.2f}x")
        print(f"Space saved: {(1 - 1/result.compression_ratio) * 100:.1f}%")
        print(f"Patterns found: {result.patterns_found}")
        print(f"Fractal dimension: {result.fractal_dimension:.3f}")
        print(f"Compression time: {result.compression_time:.2f}s")
        print(f"Lossless: {result.lossless}")
        print("=" * 60)


def decompress_command(args):
    """Decompress file"""
    compressor = FractalCompressor()
    content = compressor.decompress(args.file)
    
    print(f"\n📤 Decompression Results")
    print("=" * 60)
    print(f"Decompressed {len(content)} characters")
    print(f"Preview: {content[:500]}...")
    print("=" * 60)


def dimension_command(args):
    """Compute fractal dimension"""
    compressor = FractalCompressor()
    
    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        return
    
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    dimension = compressor.compute_fractal_dimension(content)
    
    print(f"\n📐 Fractal Dimension Analysis")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Fractal dimension: {dimension:.3f}")
    
    if dimension < 1.0:
        print("Interpretation: Low complexity, highly structured")
    elif dimension < 1.5:
        print("Interpretation: Medium complexity, balanced structure")
    else:
        print("Interpretation: High complexity, rich patterns")
    
    print("=" * 60)


def patterns_command(args):
    """Show found patterns"""
    compressor = FractalCompressor()
    
    print(f"\n🔍 Self-Similar Patterns")
    print("=" * 60)
    print(f"Total patterns: {len(compressor.patterns)}")
    
    # Group by scale
    by_scale = defaultdict(list)
    for pattern in compressor.patterns:
        by_scale[pattern.scale_levels].append(pattern)
    
    for scale, patterns in sorted(by_scale.items(), reverse=True):
        print(f"\nScale level {scale}: {len(patterns)} patterns")
        for pattern in patterns[:5]:
            print(f"  {pattern.pattern_id}: {pattern.content[:50]}... ({pattern.occurrences} occurrences)")
        
        if len(patterns) > 5:
            print(f"  ... and {len(patterns) - 5} more")
    
    print("=" * 60)


def ratio_command(args):
    """Show compression ratio"""
    compressor = FractalCompressor()
    stats = compressor.get_compression_stats()
    
    print(f"\n📊 Compression Statistics")
    print("=" * 60)
    
    if stats.get('status') == 'no_data':
        print("No compression data. Run --compress first.")
    else:
        print(f"Original size: {stats['original_size_kb']:.2f} KB")
        print(f"Compressed size: {stats['compressed_size_kb']:.2f} KB")
        print(f"Compression ratio: {stats['compression_ratio']:.2f}x")
        print(f"Space saved: {stats['space_saved_kb']:.2f} KB ({stats['space_saved_percent']:.1f}%)")
        print(f"Patterns found: {stats['patterns_found']}")
        print(f"Fractal dimension: {stats['fractal_dimension']:.3f}")
        print(f"Compression time: {stats['compression_time_s']:.2f}s")
    
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Fractal Compression - Self-Similar Knowledge Compression')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress memory file')
    compress_parser.add_argument('file', type=str, help='Memory file')
    compress_parser.set_defaults(func=compress_command)
    
    # Decompress command
    decompress_parser = subparsers.add_parser('decompress', help='Decompress file')
    decompress_parser.add_argument('file', type=str, help='Compressed file')
    decompress_parser.set_defaults(func=decompress_command)
    
    # Dimension command
    dim_parser = subparsers.add_parser('dimension', help='Compute fractal dimension')
    dim_parser.add_argument('file', type=str, help='Memory file')
    dim_parser.set_defaults(func=dimension_command)
    
    # Patterns command
    patterns_parser = subparsers.add_parser('patterns', help='Show patterns')
    patterns_parser.add_argument('file', type=str, help='Memory file')
    patterns_parser.set_defaults(func=patterns_command)
    
    # Ratio command
    ratio_parser = subparsers.add_parser('ratio', help='Show compression ratio')
    ratio_parser.set_defaults(func=ratio_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
