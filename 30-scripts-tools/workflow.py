#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
  UNIFIED WORKFLOW ENTRY - 统一工作流入口 v3.0
  用法: py workflow.py <command> [args]

  Commands:
    start <task>     - 开始新任务 (自动初始化会话)
    save <desc>      - 保存当前进度
    test             - 运行测试
    push             - Git 推送
    status           - 查看当前状态
    resume           - 恢复最近会话
    log              - 查看会话历史
    end <desc>       - 结束会话并压缩
    auto             - 开启自动保存 (每5分钟)
    help             - 显示帮助

  Features:
    - 自动检测当前项目
    - Git 集成
    - 自动发现测试
    - 统一状态存储
    - 自动保存
    - 会话历史
==============================================================================
"""
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

# 导入自我迭代模块
sys.path.insert(0, str(Path(__file__).parent))
try:
    from workflow_insights import track_command, track_session_duration, track_decision, save_decision, get_similar_decisions, generate_suggestions, cmd_report
    INSIGHTS_AVAILABLE = True
except ImportError:
    INSIGHTS_AVAILABLE = False

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
STATE_FILE = WORKSPACE / "execution-state.json"
HISTORY_FILE = WORKSPACE / "execution-history.json"
MEMORY_DIR = WORKSPACE / "10-MEMORY/00-CORE"
PROJECTS_DIR = WORKSPACE / "80-PROJECTS"
CONFIG_FILE = WORKSPACE / "30-scripts-tools" / "workflow_config.json"

# 项目检测规则
PROJECT_CONFIGS = {
    "NewsHub": ["news_hub.py", "config/sources.json"],
    "stock_pro": ["stock_pro.py", "config.json"],
}

# 默认配置
DEFAULT_CONFIG = {
    "auto_save_interval": 300,  # 5分钟
    "auto_push": False,
    "max_history": 20,
    "projects": PROJECT_CONFIGS
}


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置"""
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')


def get_state():
    """获取当前会话状态"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return None


def save_state(state):
    """保存会话状态"""
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')


def get_history():
    """获取会话历史"""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return []


def save_history(history):
    """保存会话历史"""
    config = load_config()
    # 只保留最近 N 条
    history = history[-config.get("max_history", 20):]
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding='utf-8')


def add_to_history(state, end_description=None):
    """添加历史记录"""
    history = get_history()
    entry = {
        "session_id": state.get("session_id"),
        "task": state.get("task"),
        "project": state.get("project"),
        "started_at": state.get("started_at"),
        "ended_at": datetime.now().isoformat(),
        "duration": str(datetime.now() - datetime.fromisoformat(state["started_at"])),
        "decisions_count": len(state.get("decisions", [])),
        "tests_run": state.get("tests_run", 0),
        "end_description": end_description,
        "status": "completed"
    }
    history.append(entry)
    save_history(history)


def detect_project():
    """自动检测当前项目"""
    for name, files in PROJECT_CONFIGS.items():
        project_dir = PROJECTS_DIR / name if name != "stock_pro" else WORKSPACE / "30-scripts-tools" / name
        if project_dir.exists():
            if all((project_dir / f).exists() for f in files):
                return name, project_dir

    if (WORKSPACE / ".git").exists():
        return "workspace", WORKSPACE

    return "unknown", WORKSPACE


def is_git_repo(directory):
    """检查目录是否是 Git 仓库"""
    return (directory / ".git").exists()


def get_git_changes(directory):
    """获取 Git 修改的文件列表"""
    if not is_git_repo(directory):
        return [], []

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return [], []

        modified = []
        untracked = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            status = line[:2]
            filepath = line[3:].strip()
            if status == "??":
                untracked.append(filepath)
            else:
                modified.append(filepath)
        return modified, untracked
    except:
        return [], []


def get_git_branch(directory):
    """获取当前分支"""
    if not is_git_repo(directory):
        return "N/A"

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A"
    except:
        return "N/A"


def get_unpushed_commits(directory):
    """获取未推送的提交数"""
    if not is_git_repo(directory):
        return 0

    try:
        result = subprocess.run(
            ["git", "log", "@{u}..HEAD", "--oneline"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=10
        )
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0


def discover_tests(project_dir):
    """自动发现测试"""
    tests = []
    pytest_dir = project_dir / "tests"
    if pytest_dir.exists():
        tests.append(("pytest", ["pytest", str(pytest_dir), "-v", "--tb=short"]))

    if project_dir.name == "NewsHub":
        tests.append(("newshub", ["pytest", str(project_dir / "tests"), "-v", "--tb=line"]))

    return tests


def run_tests(project_dir):
    """运行测试"""
    tests = discover_tests(project_dir)
    results = []

    for name, cmd in tests:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=120
            )
            passed = result.returncode == 0
            results.append((name, "passed" if passed else "failed", result.stdout[-300:] if result.stdout else ""))
        except Exception as e:
            results.append((name, "error", str(e)))

    return results


def git_push(directory):
    """Git 推送"""
    if not is_git_repo(directory):
        print("❌ 不是 Git 仓库")
        return False

    unpushed = get_unpushed_commits(directory)
    if unpushed == 0:
        print("✅ 没有待推送的提交")
        return True

    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(f"✅ 推送成功 ({unpushed} commits)")
            return True
        else:
            print(f"❌ 推送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 推送异常: {e}")
        return False


# ========== Auto Save ==========
_auto_save_thread = None
_auto_save_running = False


def _auto_save_worker():
    """自动保存工作线程"""
    global _auto_save_running
    config = load_config()
    interval = config.get("auto_save_interval", 300)

    while _auto_save_running:
        time.sleep(interval)
        if not _auto_save_running:
            break

        state = get_state()
        if state and state.get("status") == "active":
            project_dir = Path(state.get("project_dir", WORKSPACE))
            modified, untracked = get_git_changes(project_dir)

            state["last_saved"] = datetime.now().isoformat()
            state["files_modified"] = modified
            state["auto_saved"] = True
            save_state(state)

            print(f"\n  ⏰ Auto-saved at {datetime.now().strftime('%H:%M:%S')}")


def cmd_auto(action="start"):
    """自动保存控制"""
    global _auto_save_thread, _auto_save_running

    if action == "start":
        if _auto_save_running:
            print("✅ Auto-save already running")
            return

        config = load_config()
        interval = config.get("auto_save_interval", 300)
        _auto_save_running = True
        _auto_save_thread = threading.Thread(target=_auto_save_worker, daemon=True)
        _auto_save_thread.start()
        print(f"✅ Auto-save enabled (every {interval // 60} minutes)")

    elif action == "stop":
        _auto_save_running = False
        print("✅ Auto-save disabled")

    elif action == "status":
        if _auto_save_running:
            print("✅ Auto-save is running")
        else:
            print("❌ Auto-save is not running")


def cmd_start(task_name, project_name=None):
    """Start a new task session"""
    # 停止自动保存
    global _auto_save_running
    was_running = _auto_save_running
    if was_running:
        cmd_auto("stop")

    project_name = project_name or detect_project()[0]
    project_dir = PROJECTS_DIR / project_name if project_name not in ("workspace", "unknown") else WORKSPACE

    # 追踪
    if INSIGHTS_AVAILABLE:
        track_command("start", project_name)
        suggestions = generate_suggestions()
        if suggestions:
            print(f"\n💡 建议: {suggestions[0]['suggestion']}")

    print(f"\n{'=' *50}")
    print(f"  🚀 Starting: {task_name}")
    print(f"  📁 Project: {project_name}")
    print(f"{'=' *50}\n")

    branch = get_git_branch(project_dir)
    unpushed = get_unpushed_commits(project_dir)

    state = {
        "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "task": task_name,
        "project": project_name,
        "project_dir": str(project_dir),
        "branch": branch,
        "unpushed": unpushed,
        "started_at": datetime.now().isoformat(),
        "status": "active",
        "decisions": [],
        "files_modified": [],
        "tests_run": 0,
        "last_saved": datetime.now().isoformat(),
        "auto_saved": False
    }
    save_state(state)

    print(f"✅ Session: {state['session_id']}")
    print(f"   Branch: {branch}")
    if unpushed > 0:
        print(f"   ⚠️  {unpushed} commits 待推送")
    print(f"\nCommands:")
    print(f"  - save <desc>   保存进度")
    print(f"  - test          运行测试")
    print(f"  - push          Git推送")
    print(f"  - auto          开启自动保存")
    print(f"  - end <desc>    结束会话")

    # 恢复自动保存
    if was_running:
        cmd_auto("start")

    return state


def cmd_save(description):
    """Save current progress"""
    state = get_state()
    if not state:
        print("❌ No active session. Run 'workflow.py start <task>' first.")
        return

    project_dir = Path(state.get("project_dir", WORKSPACE))
    modified, untracked = get_git_changes(project_dir)

    state["last_saved"] = datetime.now().isoformat()
    state["files_modified"] = modified
    state["untracked"] = untracked
    state["decisions"].append({
        "time": datetime.now().isoformat(),
        "action": "save",
        "description": description
    })
    state["auto_saved"] = False
    save_state(state)

    # 追踪
    if INSIGHTS_AVAILABLE:
        track_command("save", state.get("project"))
        track_decision()
        save_decision(
            context=f"{state.get('task')} - {state.get('project')}",
            decision=description,
            result="saved"
        )

    print(f"✅ Saved: {description}")
    if modified:
        print(f"   Modified: {len(modified)} files")
    if untracked:
        print(f"   Untracked: {len(untracked)} files")


def cmd_test():
    """Run tests for current project"""
    state = get_state()
    if not state:
        print("❌ No active session.")
        return

    project_dir = Path(state.get("project_dir", WORKSPACE))
    project_name = state.get("project", "unknown")

    print(f"\n{'=' *50}")
    print(f"  🧪 Testing: {project_name}")
    print(f"{'=' *50}\n")

    results = run_tests(project_dir)

    for name, status, output in results:
        icon = "✅" if status == "passed" else "❌"
        print(f"{icon} {name}: {status}")
        if status != "passed":
            print(output)

    state["tests_run"] += 1
    state["last_test"] = datetime.now().isoformat()
    save_state(state)

    # 追踪
    if INSIGHTS_AVAILABLE:
        track_command("test", state.get("project"))
        track_test()

    return results


def cmd_push():
    """Git push"""
    state = get_state()
    if not state:
        print("❌ No active session.")
        return

    project_dir = Path(state.get("project_dir", WORKSPACE))
    git_push(project_dir)


def cmd_status():
    """Show current session status"""
    state = get_state()

    print(f"\n{'=' *50}")
    print(f"  📊 Session Status")
    print(f"{'=' *50}")

    if not state:
        print("❌ No active session\n")
        return

    started = datetime.fromisoformat(state["started_at"])
    duration = datetime.now() - started
    last_saved = state.get("last_saved")
    if last_saved:
        last_saved_dt = datetime.fromisoformat(last_saved)
        saved_ago = datetime.now() - last_saved_dt
        if saved_ago.seconds < 60:
            saved_ago_str = f"{saved_ago.seconds}s ago"
        elif saved_ago.seconds < 3600:
            saved_ago_str = f"{saved_ago.seconds // 60}m ago"
        else:
            saved_ago_str = f"{saved_ago.seconds // 3600}h ago"
    else:
        saved_ago_str = "never"

    project_dir = Path(state.get("project_dir", WORKSPACE))
    branch = get_git_branch(project_dir)
    unpushed = get_unpushed_commits(project_dir)

    print(f"Session ID: {state['session_id']}")
    print(f"Task: {state['task']}")
    print(f"Project: {state.get('project', 'N/A')}")
    print(f"Branch: {branch}")
    print(f"Status: {state['status']}")
    print(f"Duration: {duration}")
    print(f"Last saved: {saved_ago_str}")
    if state.get("auto_saved"):
        print(f"Auto-saved: YES")
    print(f"Decisions: {len(state['decisions'])}")
    print(f"Tests run: {state['tests_run']}")

    if unpushed > 0:
        print(f"\n⚠️  {unpushed} commits 待推送")
    else:
        print(f"\n✅ Git 已同步")

    modified, untracked = get_git_changes(project_dir)
    if modified:
        print(f"\nModified ({len(modified)}):")
        for f in modified[:5]:
            print(f"  - {f}")
        if len(modified) > 5:
            print(f"  ... and {len(modified) - 5} more")

    if _auto_save_running:
        print(f"\n⏰ Auto-save: ON")
    else:
        print(f"\n⏰ Auto-save: OFF")

    print(f"{'=' *50}\n")


def cmd_resume():
    """恢复最近的会话"""
    state = get_state()
    if not state:
        print("❌ No session to resume")
        return

    if state.get("status") != "active":
        state["status"] = "active"
        state["resumed_at"] = datetime.now().isoformat()
        save_state(state)
        print(f"✅ Resumed: {state['task']}")
    else:
        print(f"✅ Session already active: {state['task']}")


def cmd_log():
    """查看会话历史"""
    history = get_history()

    if not history:
        print("\n❌ No session history\n")
        return

    print(f"\n{'=' *50}")
    print(f"  📜 Session History ({len(history)} sessions)")
    print(f"{'=' *50}\n")

    for i, entry in enumerate(reversed(history[-10:]), 1):
        print(f"{i}. {entry.get('task', 'N/A')}")
        print(f"   Project: {entry.get('project', 'N/A')}")
        print(f"   Duration: {entry.get('duration', 'N/A')}")
        print(f"   Decisions: {entry.get('decisions_count', 0)}")
        print(f"   Tests: {entry.get('tests_run', 0)}")
        print(f"   Ended: {entry.get('end_description', 'N/A')}")
        print()


def cmd_end(description):
    """End session and compress"""
    global _auto_save_running
    state = get_state()
    if not state:
        print("❌ No active session.")
        return

    # 停止自动保存
    was_auto_save = _auto_save_running
    if was_auto_save:
        cmd_auto("stop")

    print(f"\n{'=' *50}")
    print(f"  📋 Ending Session: {state['session_id']}")
    print(f"{'=' *50}\n")

    duration = datetime.now() - datetime.fromisoformat(state["started_at"])
    duration_minutes = duration.seconds / 60

    print(f"Task: {state['task']}")
    print(f"Duration: {duration}")
    print(f"Decisions: {len(state['decisions'])}")
    print(f"Tests run: {state['tests_run']}")

    # 追踪
    if INSIGHTS_AVAILABLE:
        track_command("end", state.get("project"))
        track_session_duration(duration_minutes)

    # Auto push if unpushed commits
    project_dir = Path(state.get("project_dir", WORKSPACE))
    unpushed = get_unpushed_commits(project_dir)
    config = load_config()

    if unpushed > 0:
        print(f"\n⚠️  {unpushed} commits 待推送")
        if config.get("auto_push"):
            print("Auto-push enabled, pushing...")
            git_push(project_dir)
        else:
            response = input("推送? (y/n): ").strip().lower()
            if response == 'y':
                git_push(project_dir)

    # Save to daily memory
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"
    state["ended_at"] = datetime.now().isoformat()
    state["end_description"] = description

    summary = f"""
## Session: {state['task']}
**Project:** {state.get('project', 'N/A')}
**Time:** {state['started_at']} - {state['ended_at']}
**Duration:** {duration}
**Status:** {description}

### Decisions
"""
    for d in state["decisions"]:
        summary += f"- {d.get('description', d.get('action', 'unknown'))}\n"

    summary += f"\n### Tests Run: {state['tests_run']}\n"

    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
        memory_file.write_text(content + "\n" + summary, encoding='utf-8')
    else:
        memory_file.write_text(summary, encoding='utf-8')

    print(f"\n✅ Session saved to {memory_file}")

    # 添加到历史
    add_to_history(state, description)

    # Cleanup
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    print("✅ Session ended and cleaned up")


def cmd_help():
    """Show help"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  UNIFIED WORKFLOW v3.0                      ║
╠══════════════════════════════════════════════════════════════╣
║  用法: py workflow.py <command> [args]                      ║
║                                                              ║
║  Commands:                                                   ║
║    start <task>     开始新任务                                ║
║    save <desc>      保存进度                                  ║
║    test             运行测试 (自动发现)                        ║
║    push             Git 推送                                  ║
║    status           查看状态                                  ║
║    resume           恢复会话                                  ║
║    log              查看历史                                  ║
║    auto [start/stop] 自动保存控制                            ║
║    insights         自我分析报告                              ║
║    end <desc>       结束会话                                  ║
║    help             显示帮助                                  ║
║                                                              ║
║  Features:                                                   ║
║    - 自动检测项目 (NewsHub, stock_pro)                        ║
║    - Git 集成 (状态、推送)                                    ║
║    - 自动发现测试                                             ║
║    - 自动保存 (每5分钟)                                       ║
║    - 会话历史                                                 ║
║    - 自我迭代系统 (使用统计、决策库、智能建议)                  ║
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
        "push": cmd_push,
        "status": cmd_status,
        "resume": cmd_resume,
        "log": cmd_log,
        "auto": lambda: cmd_auto(args[0] if args else "start"),
        "end": lambda: cmd_end(args[0] if args else "Session completed"),
        "insights": cmd_report,
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
