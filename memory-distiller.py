#!/usr/bin/env python3
"""
Memory Distiller - 7-Persona Evolution Engine

Extract core insights from daily notes and update MEMORY.md

Usage:
    python memory-distiller.py [--weekly] [--manual]
    
Modes:
    --weekly  Run weekly distillation (Sunday 5AM)
    --manual  Manual distillation with user confirmation
    (default) Auto mode - check if distillation needed
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

# Config
WORKSPACE = str(Path(__file__).parent.parent)
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')
MEMORY_FILE = os.path.join(WORKSPACE, 'MEMORY.md')
DISTILLER_LOG = os.path.join(WORKSPACE, 'memory-distiller.log')

# Target limits
MAX_MEMORY_LINES = 400
TARGET_LINES = 300

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open(DISTILLER_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line)

def get_daily_notes(days=7):
    """Get daily notes from last N days"""
    notes = []
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        note_path = os.path.join(MEMORY_DIR, f'{date_str}.md')
        
        if os.path.exists(note_path):
            notes.append({
                'path': note_path,
                'date': date_str,
                'content': open(note_path, 'r', encoding='utf-8').read()
            })
    
    return notes

def extract_insights(note_content, date):
    """Extract core insights from daily note"""
    insights = []
    
    # Pattern 1: Key learnings with编号
    pattern_lesson = r'\[(\w+-\d+)\]\s*(.+?)(?:\n|$)'
    lessons = re.findall(pattern_lesson, note_content)
    for lesson_id, lesson_text in lessons:
        insights.append({
            'type': 'lesson',
            'id': lesson_id,
            'content': lesson_text.strip(),
            'date': date,
            'confidence': 0.9
        })
    
    # Pattern 2: Section updates (## headers)
    pattern_section = r'^##\s+(.+?)$'
    sections = re.findall(pattern_section, note_content, re.MULTILINE)
    for section in sections[:3]:  # Max 3 sections per note
        if len(section) > 10 and len(section) < 100:
            insights.append({
                'type': 'section',
                'content': section,
                'date': date,
                'confidence': 0.7
            })
    
    # Pattern 3: TODO items
    pattern_todo = r'- \[([ x])\]\s*(.+?)(?:\n|$)'
    todos = re.findall(pattern_todo, note_content)
    pending_todos = [todo[1].strip() for todo in todos if todo[0] == ' ']
    for todo in pending_todos[:5]:  # Max 5 todos
        insights.append({
            'type': 'todo',
            'content': todo,
            'date': date,
            'confidence': 0.8
        })
    
    return insights

def check_duplicates(memory_content, new_insight):
    """Check if insight already exists in MEMORY.md"""
    # Simple duplicate detection - check for 5+ word overlap
    words = new_insight.lower().split()
    if len(words) < 5:
        return False
    
    # Check each paragraph
    paragraphs = memory_content.split('\n\n')
    for para in paragraphs:
        para_words = para.lower().split()
        overlap = len(set(words) & set(para_words))
        if overlap >= 5:
            return True
    
    return False

def generate_memory_update(insights, current_memory):
    """Generate MEMORY.md update content"""
    updates = []
    
    # Group insights by type
    lessons = [i for i in insights if i['type'] == 'lesson']
    todos = [i for i in insights if i['type'] == 'todo']
    sections = [i for i in insights if i['type'] == 'section']
    
    # Add new lessons
    for lesson in lessons:
        if not check_duplicates(current_memory, lesson['content']):
            updates.append(f"- **[{lesson['id']}]** {lesson['content']} (Added: {lesson['date']})")
    
    # Add new TODOs
    if todos:
        updates.append("\n### New TODOs")
        for todo in todos[:3]:
            updates.append(f"- [ ] {todo['content']}")
    
    return '\n'.join(updates)

def update_memory_file(updates):
    """Update MEMORY.md with new content"""
    if not updates.strip():
        log("No updates to apply")
        return False
    
    # Read current MEMORY.md
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find TODO section and insert before it
    todo_pattern = r'(## .*?待办事项追踪.*?)\n(##|\Z)'
    match = re.search(todo_pattern, content, re.DOTALL)
    
    if match:
        # Insert before TODO section
        insert_pos = match.start(1)
        new_content = content[:insert_pos] + "\n## 🆕 Recent Updates\n\n" + updates + "\n\n" + content[insert_pos:]
    else:
        # Append to end if no TODO section found
        new_content = content + "\n\n## 🆕 Recent Updates\n\n" + updates
    
    # Write updated content
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    log(f"MEMORY.md updated with {len(updates.split(chr(10)))} lines")
    return True

def run_distillation(mode='auto'):
    """Main distillation process"""
    log("=" * 60)
    log(f"Memory Distiller Started - Mode: {mode}")
    log("=" * 60)
    
    # Get daily notes
    notes = get_daily_notes(days=7)
    log(f"Found {len(notes)} daily notes from last 7 days")
    
    if not notes:
        log("No daily notes found")
        return
    
    # Extract insights
    all_insights = []
    for note in notes:
        insights = extract_insights(note['content'], note['date'])
        all_insights.extend(insights)
        log(f"  {note['date']}: {len(insights)} insights extracted")
    
    log(f"Total insights: {len(all_insights)}")
    
    # Read current MEMORY.md
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        current_memory = f.read()
    
    # Generate updates
    updates = generate_memory_update(all_insights, current_memory)
    
    if updates:
        log(f"Generated {len(updates.split(chr(10)))} lines of updates")
        
        if mode == 'manual':
            print("\n" + "=" * 60)
            print("Proposed Updates:")
            print("=" * 60)
            print(updates)
            print("=" * 60)
            response = input("Apply updates? (y/n): ")
            if response.lower() != 'y':
                log("Updates rejected by user")
                return
        
        # Apply updates
        update_memory_file(updates)
        
        # Run maintenance check
        log("Running memory maintenance check...")
        run_maintenance_check()
    else:
        log("No new insights to add")
    
    log("=" * 60)
    log("Distillation Complete")
    log("=" * 60)

def run_maintenance_check():
    """Run memory-maintenance.py check"""
    maintenance_script = os.path.join(WORKSPACE, 'memory-maintenance.py')
    if os.path.exists(maintenance_script):
        import subprocess
        result = subprocess.run(['python', maintenance_script], 
                              capture_output=True, text=True)
        log("Maintenance check output:")
        log(result.stdout)
        if result.stderr:
            log(f"Errors: {result.stderr}")

if __name__ == '__main__':
    import sys
    
    mode = 'auto'
    if '--weekly' in sys.argv:
        mode = 'weekly'
    elif '--manual' in sys.argv:
        mode = 'manual'
    
    run_distillation(mode)
