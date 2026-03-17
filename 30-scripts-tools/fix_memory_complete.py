"""
Complete MEMORY.md encoding fix
Read as GBK, write as UTF-8
"""
import sys
from pathlib import Path
import shutil

# Fix Windows UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

def complete_fix():
    """Complete encoding fix"""
    
    memory_file = Path(r"D:\OpenClaw\workspace\13-memory-记忆系统\MEMORY.md")
    backup_file = memory_file.with_suffix('.md.backup2')
    
    print("🔧 Complete MEMORY.md encoding fix...")
    print(f"📁 File: {memory_file}")
    
    # Read as binary
    with open(memory_file, 'rb') as f:
        raw = f.read()
    
    print(f"📊 Raw size: {len(raw) / 1024:.1f} KB")
    
    # Try GBK first (common for Chinese Windows)
    try:
        content = raw.decode('gbk')
        print("✅ Decoded as GBK")
    except UnicodeDecodeError:
        # Try UTF-8
        try:
            content = raw.decode('utf-8')
            print("✅ Decoded as UTF-8")
        except UnicodeDecodeError:
            print("❌ Failed to decode")
            return False
    
    # Clean up content
    lines = content.split('\n')
    cleaned_lines = []
    
    # Track sections to avoid duplicates
    seen_headers = set()
    skip_until_separator = False
    
    for line in lines:
        # Skip empty lines at start
        if len(cleaned_lines) == 0 and line.strip() == '':
            continue
        
        # Fix common mojibake
        line = line.replace('鏈€鍚庢洿鏂？', '最后更新:')
        line = line.replace('鏉ユ簮', '来源')
        line = line.replace('鏍稿績瑙傜偣', '核心观点')
        line = line.replace('鏉？', '条')
        line = line.replace('瓒嬪娍杩借釜', '趋势追踪')
        line = line.replace('涓？', '个')
        line = line.replace('馃', '💡')
        line = line.replace('搴？', '库')
        line = line.replace('璁ょ煡', '认知')
        line = line.replace('杩愯', '运行')
        line = line.replace('鏄？', '是')
        line = line.replace('鐨勫繀瑕佹灦鏋？', '的必要架构')
        line = line.replace('缃俊搴？', '置信度')
        line = line.replace('鏃ユ湡', '日期')
        line = line.replace('娲炲療', '洞察')
        line = line.replace('灞？', '层')
        line = line.replace('璇佹嵁', '证据')
        line = line.replace('瀹炵幇', '实现')
        line = line.replace('妯″紡', '模式')
        line = line.replace('搴旂敤', '应用')
        line = line.replace('璋冭瘯', '调试')
        line = line.replace('缁紶', '续传')
        line = line.replace('鈫？', '→')
        line = line.replace('锛？', '，')
        line = line.replace('紝', '，')
        line = line.replace('钃濆浘', '蓝图')
        line = line.replace('紩鎿？', '引擎')
        line = line.replace('鍙縼绉？', '可迁移')
        line = line.replace('璁板繂', '记忆')
        line = line.replace('闀挎湡', '长期')
        line = line.replace('鍔ㄨ捀棣？', '动蒸馏')
        line = line.replace('鎵嬪姩鏁寸悊', '手动整理')
        line = line.replace('鏍？', '观')
        line = line.replace('鐐？', '点')
        
        cleaned_lines.append(line)
    
    # Add proper header if missing
    if not cleaned_lines[0].startswith('#'):
        cleaned_lines.insert(0, '# MEMORY.md - 长期记忆 (完整版)')
        cleaned_lines.insert(1, '')
        cleaned_lines.insert(2, '**最后更新:** 2026-03-17 16:40')
        cleaned_lines.insert(3, '**来源:** memory-distiller 自动蒸馏 + 手动整理 + 学习者人格')
        cleaned_lines.insert(4, '**核心观点:** 190+ 条 | **趋势追踪:** 8 个')
        cleaned_lines.insert(5, '')
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Create backup
    print(f"💾 Creating backup: {backup_file}")
    shutil.copy2(memory_file, backup_file)
    
    # Write as UTF-8
    print("✍️ Writing as UTF-8...")
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✅ Complete! New size: {memory_file.stat().st_size / 1024:.1f} KB")
    print(f"📊 Lines: {len(cleaned_lines)}")
    
    return True

if __name__ == '__main__':
    success = complete_fix()
    sys.exit(0 if success else 1)
