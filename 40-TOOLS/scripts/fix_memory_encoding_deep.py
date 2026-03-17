#!/usr/bin/env python3
"""
Deep Memory Encoding Fixer - Fix UTF-8 that was wrongly decoded as GBK
Strategy: Re-encode as Latin-1, then decode as UTF-8
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def fix_double_encoding(text):
    """
    Fix text that was UTF-8 but decoded as GBK/CP1252
    Pattern: Chinese characters appear as gibberish
    Solution: Encode back to bytes, then decode as UTF-8
    """
    try:
        # Step 1: Encode the garbled text back to bytes using the wrong encoding
        # This reverses the wrong decoding
        wrong_bytes = text.encode('latin-1')  # or 'cp1252'
        
        # Step 2: Decode as UTF-8 (the correct encoding)
        fixed_text = wrong_bytes.decode('utf-8')
        return fixed_text
    except Exception as e:
        print(f"  Double-encoding fix failed: {e}")
        return None

def main():
    input_file = Path("memory/MEMORY.md.backup.final")
    output_file = Path("memory/MEMORY.md.deep-fixed")
    
    print(f"📖 Reading: {input_file}")
    
    # Read as UTF-8-SIG
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    print(f"   Original: {len(content)} chars")
    
    # Check if it looks like mojibake
    # Mojibake often has high ratio of uncommon characters
    uncommon_ratio = sum(1 for c in content if ord(c) > 0xFF) / len(content)
    print(f"   Uncommon char ratio: {uncommon_ratio:.2%}")
    
    if uncommon_ratio > 0.1:  # More than 10% uncommon = likely mojibake
        print("\n🔧 Attempting deep fix (UTF-8→Latin-1→UTF-8)...")
        fixed = fix_double_encoding(content)
        
        if fixed:
            print(f"✅ Deep fix successful: {len(fixed)} chars")
            
            # Verify it looks like Chinese now
            chinese_chars = sum(1 for c in fixed if '\u4e00' <= c <= '\u9fff')
            print(f"   Chinese characters: {chinese_chars} ({chinese_chars/len(fixed)*100:.1f}%)")
            
            # Check for remaining garbled patterns
            garbled_patterns = ['锛', '鏍', '闀', '鏈', '稿']
            remaining = sum(1 for p in garbled_patterns if p in fixed)
            print(f"   Remaining garbled: {remaining}/{len(garbled_patterns)}")
            
            content = fixed
        else:
            print("❌ Deep fix failed, keeping original")
    else:
        print("✅ Text looks clean, no deep fix needed")
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n💾 Written: {output_file}")
    print(f"   Size: {output_file.stat().st_size} bytes")
    
    # Show sample
    print(f"\n📋 Sample (first 500 chars):")
    print("-" * 50)
    print(content[:500])
    print("-" * 50)

if __name__ == '__main__':
    main()
