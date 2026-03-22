#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
  UNIFIED WORKFLOW ENTRY - 统一工作流入口
  用法: py workflow.py <command> [args]
  
  Commands:
    start <task>     - 开始新任务 (自动初始化会话)
    test             - 运行测试
    save <desc>      - 保存当前进度
    end <desc>       - 结束会话并压缩
    status           - 查看当前状态
    help             - 显示帮助
==============================================================================
"""
import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
STATE_FILE = WORKSPACE / "execution-state.json"
SESSION_FILE = WORKSPACE / "session_temp.json"
MEMORY_DIR = WORKSPACE / "13-memory"

def get_state():
    """Get current session state"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return None

def save_state(state):
    """Save session state"""
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def cmd_start(task_name):
    """Start a new task session"""
    print(f"\n{'='*50}")
    print(f"  🚀 Starting: {task_name}")
    print(f"{'='*50}\n")
    
    # Create session state
    state = {
        "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "task": task_name,
        "started_at": datetime.now().isoformat(),
        "status": "active",
        "decisions": [],
        "files_modified": [],
        "tests_run": 0
    }
    save_state(state)
    
    # Create session temp file
    session_data = {
        "task": task_name,
        "start_time": datetime.now().isoformat(),
        "decisions": []
    }
    SESSION_FILE.write_text(json.dumps(session_data, indent=2))
    
    print(f"✅ Session initialized: {state['session_id']}")
    print(f"📝 Task: {task_name}")
    print(f"\nReady to work! Use these commands:")
    print(f"  - workflow.py save <desc>   - Save progress")
    print(f"  - workflow.py test          - Run tests")
    print(f"  - workflow.py end <desc>    - End session")
    return state

def cmd_save(description):
    """Save current progress"""
    state = get_state()
    if not state:
        print("❌ No active session. Run 'workflow.py start <task>' first.")
        return
    
    state["last_saved"] = datetime.now().isoformat()
    state["decisions"].append({
        "time": datetime.now().isoformat(),
        "action": "save",
        "description": description
    })
    save_state(state)
    
    # Update session temp
    if SESSION_FILE.exists():
        session = json.loads(SESSION_FILE.read_text())
        session["decisions"].append({
            "time": datetime.now().isoformat(),
            "description": description
        })
        SESSION_FILE.write_text(json.dumps(session, indent=2))
    
    print(f"✅ Progress saved: {description}")

def cmd_test():
    """Run tests for modified files"""
    state = get_state()
    if not state:
        print("❌ No active session.")
        return
    
    print("\n" + "="*50)
    print("  🧪 Running Tests")
    print("="*50 + "\n")
    
    # Check for test files
    test_results = []
    
    # Run stock_pro tests if modified
    stock_pro_dir = WORKSPACE / "30-scripts-tools" / "stock_pro"
    test_file = stock_pro_dir / "test_all.py"
    if test_file.exists():
        print("Running stock_pro tests...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE)
        )
        if result.returncode == 0:
            print("✅ stock_pro tests passed")
            test_results.append(("stock_pro", "passed"))
        else:
            print("❌ stock_pro tests failed")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            test_results.append(("stock_pro", "failed"))
    
    state["tests_run"] += 1
    state["last_test"] = datetime.now().isoformat()
    save_state(state)
    
    print(f"\n✅ Tests completed: {len(test_results)} test suites")
    return test_results

def cmd_end(description):
    """End session and compress"""
    state = get_state()
    if not state:
        print("❌ No active session.")
        return
    
    print(f"\n{'='*50}")
    print(f"  📋 Ending Session: {state['session_id']}")
    print(f"{'='*50}\n")
    
    # Calculate duration
    started = datetime.fromisoformat(state["started_at"])
    duration = datetime.now() - started
    
    print(f"Task: {state['task']}")
    print(f"Duration: {duration}")
    print(f"Decisions: {len(state['decisions'])}")
    print(f"Tests run: {state['tests_run']}")
    
    # Save to daily memory
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"
    
    summary = f"""
## Session: {state['task']}
**Time:** {state['started_at']} - {datetime.now().isoformat()}
**Duration:** {duration}
**Status:** Completed

### Decisions
"""
    for d in state["decisions"]:
        summary += f"- {d.get('description', d.get('action', 'unknown'))}\n"
    
    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
        memory_file.write_text(content + "\n" + summary, encoding='utf-8')
    else:
        memory_file.write_text(summary, encoding='utf-8')
    
    print(f"\n✅ Session saved to {memory_file}")
    
    # Cleanup
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
    
    print("✅ Session ended and cleaned up")

def cmd_status():
    """Show current session status"""
    state = get_state()
    if not state:
        print("\n❌ No active session")
        print("Run 'workflow.py start <task>' to begin.\n")
        return
    
    started = datetime.fromisoformat(state["started_at"])
    duration = datetime.now() - started
    
    print(f"\n{'='*50}")
    print(f"  📊 Session Status")
    print(f"{'='*50}")
    print(f"Session ID: {state['session_id']}")
    print(f"Task: {state['task']}")
    print(f"Status: {state['status']}")
    print(f"Duration: {duration}")
    print(f"Decisions: {len(state['decisions'])}")
    print(f"Tests run: {state['tests_run']}")
    print(f"{'='*50}\n")

def cmd_help():
    """Show help"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  UNIFIED WORKFLOW - 统一工作流                 ║
╠══════════════════════════════════════════════════════════════╣
║  用法: py workflow.py <command> [args]                        ║
║                                                              ║
║  Commands:                                                   ║
║    start <task>     开始新任务                                ║
║    save <desc>      保存进度                                  ║
║    test             运行测试                                  ║
║    end <desc>       结束会话                                  ║
║    status           查看状态                                  ║
║    help             显示帮助                                  ║
║                                                              ║
║  Example:                                                    ║
║    py workflow.py start "优化股票分析"                        ║
║    py workflow.py save "修复了缓存问题"                       ║
║    py workflow.py test                                       ║
║    py workflow.py end "v12.7优化完成"                         ║
╚══════════════════════════════════════════════════════════════╝
""")

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    commands = {
        "start": lambda: cmd_start(args[0] if args else "Untitled Task"),
        "save": lambda: cmd_save(args[0] if args else "Progress saved"),
        "test": cmd_test,
        "end": lambda: cmd_end(args[0] if args else "Session completed"),
        "status": cmd_status,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help,
    }
    
    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()