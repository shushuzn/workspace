#!/usr/bin/env python3
"""
Context Compressor - Quick Session Context Compression
Compresses memory files to reduce token usage while preserving core insights.
"""
import os
import json
from datetime import datetime

# Configuration
WORKSPACE = r"C:\Users\华为\.copaw"
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")
OUTPUT_FILE = os.path.join(WORKSPACE, "data", "context_compression_report.json")

def get_file_size(filepath):
    """Get file size in KB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / 1024
    return 0

def count_lines(filepath):
    """Count non-empty lines"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for line in f if line.strip())

def extract_core_sections(filepath):
    """Extract core sections from memory file"""
    if not os.path.exists(filepath):
        return {}
    
    sections = {}
    current_section = None
    current_content = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = ''.join(current_content)
                current_section = line.strip().replace('## ', '')
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = ''.join(current_content)
    
    return sections

def compress_context():
    """Main compression function"""
    print("=" * 60)
    print("Context Compression Report")
    print("=" * 60)
    print()
    
    # Current state
    memory_size = get_file_size(MEMORY_MD)
    memory_lines = count_lines(MEMORY_MD)
    
    # Count memory files
    memory_files = []
    if os.path.exists(MEMORY_DIR):
        for f in os.listdir(MEMORY_DIR):
            if f.endswith('.md') and not f.startswith('_'):
                filepath = os.path.join(MEMORY_DIR, f)
                memory_files.append({
                    'name': f,
                    'size': get_file_size(filepath),
                    'lines': count_lines(filepath)
                })
    
    total_memory_size = sum(f['size'] for f in memory_files)
    total_lines = sum(f['lines'] for f in memory_files)
    
    # Extract sections
    sections = extract_core_sections(MEMORY_MD)
    
    # Compression recommendations
    recommendations = []
    
    if memory_size > 15:
        recommendations.append("[WARN] MEMORY.md > 15KB - Consider archiving old sections")
    
    if len(memory_files) > 20:
        recommendations.append(f"[WARN] {len(memory_files)} memory files - Consider merging old dailies")
    
    # Find largest files
    largest = sorted(memory_files, key=lambda x: x['size'], reverse=True)[:5]
    
    # Output
    print(f"Current State:")
    print(f"   MEMORY.md: {memory_size:.1f} KB ({memory_lines} lines)")
    print(f"   Daily files: {len(memory_files)} files ({total_memory_size:.1f} KB total)")
    print(f"   Total lines: {total_lines}")
    print()
    
    print(f"Largest Memory Files:")
    for f in largest:
        print(f"   - {f['name']}: {f['size']:.1f} KB ({f['lines']} lines)")
    print()
    
    print(f"MEMORY.md Sections:")
    for section, content in sections.items():
        lines = len(content.split('\n'))
        print(f"   - {section}: {lines} lines")
    print()
    
    if recommendations:
        print(f"Compression Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
        print()
    
    # Compression estimate
    estimated_savings = memory_size * 0.3  # Assume 30% compression possible
    print(f"Compression Potential:")
    print(f"   Estimated savings: ~{estimated_savings:.1f} KB (30% reduction)")
    print(f"   Target size: {memory_size - estimated_savings:.1f} KB")
    print()
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'memory_md': {
            'size_kb': memory_size,
            'lines': memory_lines,
            'sections': len(sections)
        },
        'daily_files': {
            'count': len(memory_files),
            'total_size_kb': total_memory_size,
            'total_lines': total_lines
        },
        'largest_files': largest,
        'recommendations': recommendations,
        'estimated_savings_kb': estimated_savings
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved: {OUTPUT_FILE}")
    print("=" * 60)
    
    return report

if __name__ == "__main__":
    compress_context()
