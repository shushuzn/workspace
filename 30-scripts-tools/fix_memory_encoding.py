#!/usr/bin/env python3
"""
Memory Encoding Fixer - Attempt to fix encoding issues in original MEMORY.md
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BACKUP_FILE = r"memory/MEMORY.md.backup.final"
OUTPUT_FILE = r"memory/MEMORY.md.fixed-encoding.md"

def try_fix_encoding(content_bytes):
    """Try multiple encoding strategies"""
    
    strategies = [
        ('utf-8', lambda b: b.decode('utf-8')),
        ('gbk', lambda b: b.decode('gbk')),
        ('utf-8-sig', lambda b: b.decode('utf-8-sig')),
        ('gb18030', lambda b: b.decode('gb18030')),
    ]
    
    results = []
    
    for encoding, decoder in strategies:
        try:
            decoded = decoder(content_bytes)
            # Check for garbled text patterns
            has_garbled = '锛' in decoded or '鏍' in decoded or 'ï' in decoded
            results.append({
                'encoding': encoding,
                'success': True,
                'garbled': has_garbled,
                'content': decoded,
                'size': len(decoded)
            })
            print(f"✅ {encoding}: {len(decoded)} chars, garbled={has_garbled}")
        except Exception as e:
            results.append({
                'encoding': encoding,
                'success': False,
                'error': str(e)
            })
            print(f"❌ {encoding}: {e}")
    
    return results

def main():
    print("🔧 Memory Encoding Fixer")
    print("="*50)
    print(f"Input: {BACKUP_FILE}")
    print()
    
    # Read as binary
    with open(BACKUP_FILE, 'rb') as f:
        content_bytes = f.read()
    
    print(f"File size: {len(content_bytes)} bytes")
    print()
    
    # Try different encodings
    print("Trying different encodings:")
    print("-"*50)
    results = try_fix_encoding(content_bytes)
    print()
    
    # Find best result
    best = None
    for result in results:
        if result['success'] and not result.get('garbled', True):
            best = result
            break
    
    if not best:
        # If all have garbled, pick utf-8 anyway
        for result in results:
            if result['success']:
                best = result
                break
    
    if best:
        print(f"Best encoding: {best['encoding']}")
        print(f"Output size: {best['size']} chars")
        
        # Write fixed version
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(best['content'])
        
        print(f"\n✅ Written to: {OUTPUT_FILE}")
        
        # Check if garbled text still present
        if '锛' in best['content'] or '鏍' in best['content']:
            print("\n⚠️  WARNING: Garbled text still present!")
            print("   The file may have mixed encoding that cannot be fully fixed.")
            print("   Manual recreation may be necessary.")
        else:
            print("\n✅ No garbled text detected!")
    else:
        print("\n❌ No successful encoding found!")

if __name__ == '__main__':
    main()
