# 工作流优化方案 - 完整详情

**版本:** v1.0.0  
**日期:** 2026-03-19  
**状态:** Phase 1 实施中

---

## 📋 目录

1. [方案 A: 自动步骤追踪](#方案-a-自动步骤追踪)
2. [方案 B: 交互式菜单](#方案-b-交互式菜单)
3. [方案 C: 工具层强制检查](#方案-c-工具层强制检查)
4. [方案 D: 智能步骤跳过](#方案-d-智能步骤跳过)
5. [方案 E: 进度可视化](#方案-e-进度可视化)

---

## 方案 A: 自动步骤追踪

### 问题详述

**当前流程:**
```
用户：执行工具 X
AI:  [执行工具...]
AI:  ✅ 工具执行完成

[用户需要手动]
→ py workflow_enforcer.py --complete-step N
```

**问题:**
1. 用户容易忘记手动确认
2. 增加 50% 操作步骤
3. 打断工作流连续性
4. 容易出错（输错步骤号）

### 技术方案

#### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   Tool Executor                          │
│  (tool_executor.py)                                      │
├─────────────────────────────────────────────────────────┤
│  1. 接收工具调用请求                                      │
│  2. 验证当前工作流步骤                                    │
│  3. 执行工具                                              │
│  4. 捕获执行结果                                          │
│  5. 自动调用 WorkflowEnforcer.complete_step()            │
│  6. 返回结果给用户                                        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                Workflow Enforcer                         │
│  (workflow_enforcer.py)                                  │
├─────────────────────────────────────────────────────────┤
│  - 检查工作流状态                                         │
│  - 验证步骤顺序                                           │
│  - 更新 checkpoint.json                                   │
│  - 记录执行日志                                           │
└─────────────────────────────────────────────────────────┘
```

#### 代码实现

**文件:** `30-scripts-tools/tool_executor.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Executor with Auto-Step Completion
工具执行器 - 带自动步骤追踪
"""

import json
import subprocess
import sys
import io
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

# 修复 Windows 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class WorkflowViolationError(Exception):
    """工作流违规异常"""
    pass

class ToolExecutor:
    def __init__(self, flow_id="20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.checkpoint_file = FLOW_ARCHIVE / flow_id / "checkpoint.json"
        self.current_step = self._load_current_step()
    
    def _load_current_step(self):
        """加载当前步骤"""
        if not self.checkpoint_file.exists():
            return 1
        
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        completed = state.get('completed_steps', [])
        return len(completed) + 1
    
    def _load_workflow_config(self):
        """加载工作流配置"""
        workflow_file = FLOW_ARCHIVE / self.flow_id / "workflow.json"
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_step_tool_mapping(self):
        """获取步骤 - 工具映射"""
        workflow = self._load_workflow_config()
        mapping = {}
        
        for step in workflow.get('steps', []):
            step_id = step['step_id']
            tool_id = step.get('tool_id')
            if tool_id:
                mapping[tool_id] = step_id
        
        return mapping
    
    def execute_tool(self, tool_id, auto_complete=True):
        """
        执行工具并自动完成步骤
        
        Args:
            tool_id: 工具 ID
            auto_complete: 是否自动完成步骤 (默认 True)
        
        Returns:
            dict: 执行结果
        """
        # 1. 验证工作流状态
        if not self._verify_workflow_active():
            raise WorkflowViolationError(
                "工作流未启动！请先执行：py workflow_enforcer.py --start"
            )
        
        # 2. 检查工具 - 步骤映射
        tool_mapping = self._get_step_tool_mapping()
        expected_step = tool_mapping.get(tool_id)
        
        if expected_step and expected_step != self.current_step:
            print(f"[WARN] 工具 {tool_id} 通常在步骤 {expected_step} 执行")
            print(f"       当前步骤：{self.current_step}")
        
        # 3. 执行工具
        print(f"\n[Tool Executor] 执行工具：{tool_id}")
        print(f"     当前步骤：{self.current_step}")
        print(f"     自动完成：{auto_complete}")
        
        result = self._run_tool_command(tool_id)
        
        # 4. 自动完成步骤
        if auto_complete and result['success']:
            self._complete_current_step(tool_id, result)
        
        return result
    
    def _verify_workflow_active(self):
        """验证工作流是否激活"""
        if not self.checkpoint_file.exists():
            return False
        
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return state.get('status') in ['in_progress', 'started']
    
    def _run_tool_command(self, tool_id):
        """执行工具命令"""
        registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
        
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        tool_config = registry.get('tools', {}).get(tool_id)
        
        if not tool_config:
            return {
                'success': False,
                'error': f"工具未找到：{tool_id}",
                'execution_time_ms': 0
            }
        
        command = tool_config.get('command')
        if not command:
            return {
                'success': False,
                'error': f"工具无命令配置：{tool_id}",
                'execution_time_ms': 0
            }
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=tool_config.get('timeout_seconds', 60)
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time_ms': execution_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"工具执行超时 (>{tool_config.get('timeout_seconds', 60)}s)",
                'execution_time_ms': tool_config.get('timeout_seconds', 60) * 1000
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time_ms': 0
            }
    
    def _complete_current_step(self, tool_id, result):
        """自动完成当前步骤"""
        enforcer_script = WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"
        
        command = [
            sys.executable,
            str(enforcer_script),
            "--complete-step",
            str(self.current_step)
        ]
        
        subprocess.run(command, capture_output=True)
        
        self._log_execution(tool_id, result)
        
        self.current_step += 1
        
        print(f"\n[OK] 步骤 {self.current_step - 1} 自动完成")
        print(f"     工具：{tool_id}")
        print(f"     结果：{'成功' if result['success'] else '失败'}")
        print(f"     下一步：{self.current_step}")
    
    def _log_execution(self, tool_id, result):
        """记录执行日志"""
        log_file = FLOW_ARCHIVE / self.flow_id / "execution-log.json"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
        else:
            log = {
                'workflow_id': self.flow_id,
                'executions': []
            }
        
        log['executions'].append({
            'step': self.current_step,
            'tool_id': tool_id,
            'timestamp': datetime.now().isoformat(),
            'success': result['success'],
            'execution_time_ms': result.get('execution_time_ms', 0)
        })
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='工具执行器 (带自动步骤追踪)')
    parser.add_argument('tool_id', help='工具 ID')
    parser.add_argument('--flow-id', default='20260318-universal-workflow-001',
                       help='工作流 ID')
    parser.add_argument('--no-auto-complete', action='store_true',
                       help='禁用自动完成步骤')
    
    args = parser.parse_args()
    
    executor = ToolExecutor(flow_id=args.flow_id)
    
    try:
        result = executor.execute_tool(
            args.tool_id,
            auto_complete=not args.no_auto_complete
        )
        
        if result['success']:
            print(f"\n[OK] 工具执行成功")
            sys.exit(0)
        else:
            print(f"\n[ERROR] 工具执行失败：{result.get('error', '未知错误')}")
            sys.exit(1)
            
    except WorkflowViolationError as e:
        print(f"\n[BLOCKER] {e}")
        sys.exit(1)
```

### 使用方式

```bash
# 方式 1: 直接调用工具（自动完成步骤）
py 30-scripts-tools\tool_executor.py fast-load

# 方式 2: 禁用自动完成
py 30-scripts-tools\tool_executor.py fast-load --no-auto-complete

# 方式 3: 指定工作流
py 30-scripts-tools\tool_executor.py fast-load --flow-id 20260318-universal-workflow-001
```

### 验收标准

- [ ] 工具执行成功后自动调用 `--complete-step`
- [ ] 工具执行失败时不标记步骤完成
- [ ] 工作流未激活时报错阻断
- [ ] 执行日志正确记录
- [ ] 支持 `--no-auto-complete` 开关
- [ ] 与现有 workflow_enforcer.py 兼容

### 实施时间

**预计:** 3.5 小时

---

## 方案 B: 交互式菜单

### 问题详述

**当前命令行体验:**
```bash
py workflow_enforcer.py --start
py workflow_enforcer.py --check-step 3
py workflow_enforcer.py --complete-step 3
py workflow_enforcer.py --validate
```

**问题:** 参数多，记忆负担重，无实时反馈

### 界面设计

```
============================================================
工作流执行器 - 20260318-universal-workflow-001 (v1.1.0)
============================================================

进度：[████████░░░░] 8/12 步骤完成 (67%)
状态：进行中
违规：0 次

------------------------------------------------------------
当前步骤：9. 批判者最终审查 [阻塞]
------------------------------------------------------------

可用操作:
  1. 执行当前步骤
  2. 查看步骤详情
  3. 查看工作流完整状态
  4. 查看执行历史
  5. 跳过当前步骤 (需要确认)
  6. 暂停工作流
  7. 退出（保持工作流状态）

选择操作 [1-7]: _
```

### 代码实现

**文件:** `30-scripts-tools/workflow_interactive.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive Menu for Workflow Execution
交互式菜单 - 降低工作流使用门槛
"""

import json
import subprocess
import sys
import os
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

class WorkflowInteractive:
    def __init__(self, flow_id="20260318-universal-workflow-001"):
        self.flow_id = flow_id
        self.checkpoint_file = FLOW_ARCHIVE / flow_id / "checkpoint.json"
        self.workflow_file = FLOW_ARCHIVE / flow_id / "workflow.json"
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_state(self):
        if not self.checkpoint_file.exists():
            return None
        with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_workflow(self):
        if not self.workflow_file.exists():
            return None
        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def show_header(self, state, workflow):
        print("=" * 60)
        print(f"工作流执行器 - {workflow.get('name', 'Unknown')} (v{workflow.get('version', '?')})")
        print("=" * 60)
        
        if state:
            total = state.get('total_steps', 0)
            completed = len(state.get('completed_steps', []))
            progress = int(completed / total * 10) if total > 0 else 0
            progress_bar = "█" * progress + "░" * (10 - progress)
            percentage = int(completed / total * 100) if total > 0 else 0
            
            print(f"\n进度：[{progress_bar}] {completed}/{total} 步骤完成 ({percentage}%)")
            print(f"状态：{state.get('status', 'unknown')}")
            print(f"违规：{len(state.get('violations', []))} 次")
    
    def show_current_step(self, state, workflow):
        if not state or not workflow:
            return
        
        completed = state.get('completed_steps', [])
        current_step_num = len(completed) + 1
        
        steps = workflow.get('steps', [])
        if current_step_num > len(steps):
            print("\n[OK] 所有步骤已完成!")
            return
        
        current_step = steps[current_step_num - 1]
        step_name = current_step.get('name', 'Unknown')
        blocking = current_step.get('blocking', False)
        blocking_tag = "[阻塞]" if blocking else "[非阻塞]"
        
        print(f"\n{'=' * 60}")
        print(f"当前步骤：{current_step_num}. {step_name} {blocking_tag}")
        print(f"{'=' * 60}")
        print(f"\n描述：{current_step.get('description', 'N/A')}")
        print(f"工具：{current_step.get('tool_id', 'N/A')}")
    
    def show_menu(self):
        print("\n可用操作:")
        print("  1. 执行当前步骤")
        print("  2. 查看步骤详情")
        print("  3. 查看工作流完整状态")
        print("  4. 查看执行历史")
        print("  5. 跳过当前步骤 (需要确认)")
        print("  6. 暂停工作流")
        print("  7. 退出（保持工作流状态）")
        print("  8. 刷新状态")
        print("  9. 帮助")
    
    def execute_current_step(self, state, workflow):
        if not state or not workflow:
            print("[ERROR] 工作流未启动")
            return
        
        completed = state.get('completed_steps', [])
        current_step_num = len(completed) + 1
        
        steps = workflow.get('steps', [])
        if current_step_num > len(steps):
            print("[OK] 所有步骤已完成!")
            return
        
        current_step = steps[current_step_num - 1]
        tool_id = current_step.get('tool_id')
        
        if not tool_id:
            print(f"[INFO] 步骤 {current_step_num} 无关联工具")
            return
        
        registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        tool_config = registry.get('tools', {}).get(tool_id)
        if not tool_config:
            print(f"[ERROR] 工具未找到：{tool_id}")
            return
        
        command = tool_config.get('command')
        print(f"\n[执行] {command}")
        print("-" * 60)
        
        result = subprocess.run(command, shell=True, encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            print("\n[OK] 工具执行成功，自动完成步骤...")
            subprocess.run([
                sys.executable,
                str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
                "--complete-step",
                str(current_step_num)
            ])
        else:
            print("\n[ERROR] 工具执行失败")
    
    def show_step_details(self, state, workflow):
        if not workflow:
            return
        
        steps = workflow.get('steps', [])
        print("\n步骤详情:")
        print("-" * 60)
        
        for i, step in enumerate(steps, 1):
            status = "[✓]" if i in state.get('completed_steps', []) else "[ ]"
            blocking = "[阻塞]" if step.get('blocking', False) else "[非阻塞]"
            print(f"{status} {i}. {step.get('name')} {blocking}")
    
    def show_full_status(self, state):
        if not state:
            print("[INFO] 工作流未启动")
            return
        
        print("\n完整状态:")
        print("-" * 60)
        for key, value in state.items():
            if isinstance(value, list):
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")
    
    def show_history(self):
        log_file = FLOW_ARCHIVE / self.flow_id / "execution-log.json"
        
        if not log_file.exists():
            print("[INFO] 无执行历史")
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            log = json.load(f)
        
        print("\n执行历史:")
        print("-" * 60)
        
        executions = log.get('executions', [])
        for exec_item in executions[-10:]:
            print(f"  步骤 {exec_item.get('step')}: {exec_item.get('tool_id')}")
            print(f"    时间：{exec_item.get('timestamp', 'N/A')}")
            print(f"    结果：{'✓' if exec_item.get('success') else '✗'}")
    
    def skip_step(self, state):
        confirm = input("\n确认跳过当前步骤？(y/N): ")
        if confirm.lower() != 'y':
            print("[取消] 跳过操作已取消")
            return
        
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--log-violation",
            "step_skip"
        ])
        
        print("[WARN] 步骤已跳过，违规已记录")
    
    def run(self):
        print("\n[启动] 加载工作流...")
        
        state = self.load_state()
        workflow = self.load_workflow()
        
        if not workflow:
            print("[ERROR] 工作流配置未找到!")
            return
        
        if not state:
            print("[INFO] 工作流未启动，是否现在启动？")
            confirm = input("启动工作流？(y/N): ")
            if confirm.lower() == 'y':
                subprocess.run([
                    sys.executable,
                    str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
                    "--start"
                ])
                state = self.load_state()
            else:
                return
        
        while True:
            self.clear_screen()
            self.show_header(state, workflow)
            self.show_current_step(state, workflow)
            self.show_menu()
            
            choice = input("\n选择操作 [1-9]: ").strip()
            
            if choice == '1':
                self.execute_current_step(state, workflow)
            elif choice == '2':
                self.show_step_details(state, workflow)
            elif choice == '3':
                self.show_full_status(state)
            elif choice == '4':
                self.show_history()
            elif choice == '5':
                self.skip_step(state)
            elif choice == '6':
                print("[暂停] 工作流已暂停")
                input("按 Enter 继续...")
            elif choice == '7':
                print("[退出] 保持工作流状态")
                break
            elif choice == '8':
                state = self.load_state()
                print("[刷新] 状态已更新")
                input("按 Enter 继续...")
            elif choice == '9':
                print("\n帮助:")
                print("  - 数字 1-9 选择对应操作")
                print("  - 步骤分阻塞/非阻塞两种")
                print("  - 阻塞步骤必须完成才能继续")
                input("\n按 Enter 继续...")
            
            state = self.load_state()


if __name__ == '__main__':
    ui = WorkflowInteractive()
    ui.run()
```

### 使用方式

```bash
# 启动交互式菜单
py 30-scripts-tools\workflow_interactive.py
```

### 验收标准

- [ ] 实时显示工作流进度
- [ ] 菜单选项完整（9 个操作）
- [ ] 执行步骤后自动刷新状态
- [ ] 支持退出后恢复状态

### 实施时间

**预计:** 5.5 小时

---

## 方案 C: 工具层强制检查

### 问题详述

**当前漏洞:**
```bash
# 用户可以直接调用工具，绕过工作流
py 30-scripts-tools\fast_load.py  # 无检查!
```

### 技术方案

修改 `tool_executor.py` 添加强制检查：

```python
def execute_tool(self, tool_id, auto_complete=True):
    # 1. 验证工作流状态
    if not self._verify_workflow_active():
        raise WorkflowViolationError(
            "工作流未启动！请先执行：py workflow_enforcer.py --start"
        )
    
    # 2. 检查工具 - 步骤映射
    tool_mapping = self._get_step_tool_mapping()
    expected_step = tool_mapping.get(tool_id)
    
    if expected_step and expected_step != self.current_step:
        raise WorkflowViolationError(
            f"工具 {tool_id} 不允许在步骤 {self.current_step} 执行\n"
            f"应该在步骤 {expected_step} 执行"
        )
    
    # 3. 执行工具...
```

### 验收标准

- [ ] 工作流未激活时阻断所有工具执行
- [ ] 工具 - 步骤映射正确验证
- [ ] 错误信息清晰指引修复

### 实施时间

**预计:** 4 小时

---

## 方案 D: 智能步骤跳过

### 问题详述

**当前:** 所有任务都执行 12 步，某些步骤不必要

### 技术方案

在 `workflow.json` 中添加条件：

```json
{
  "step_id": 5,
  "name": "子工作流调度",
  "condition": "task.requires_subworkflow",
  "skip_if": "task.type == 'simple_query'"
}
```

### 验收标准

- [ ] 简单任务自动跳过步骤 5
- [ ] 条件判断准确
- [ ] 跳过步骤记录日志

### 实施时间

**预计:** 8 小时

---

## 方案 E: 进度可视化

### 问题详述

**当前:** 无直观进度展示

### 技术方案

```bash
py workflow_enforcer.py --status

工作流：20260318-universal-workflow-001
状态：进行中 (8/12)

[✓] 1. 上下文加载验证
[✓] 2. Flow ID 绑定
[✓] 3. 任务解析
[✓] 4. 工具/工作流选择
[✓] 5. 子工作流调度
[✓] 6. 工具执行
[✓] 7. 执行日志记录
[✓] 8. 检查点保存
[●] 9. 批判者最终审查 ← 当前
[ ] 10. 质量门禁
[ ] 11. 会话压缩保存
[ ] 12. Git 提交推送

预计剩余时间：5 分钟
```

### 验收标准

- [ ] 图形化进度条
- [ ] 每步状态清晰
- [ ] 预计剩余时间

### 实施时间

**预计:** 2 小时

---

## 📊 实施路线图

### Phase 1 (本周)

| 任务 | 负责人 | 状态 | 截止日期 |
|------|--------|------|---------|
| 工具层强制检查 | Claw | ⏳ 待开始 | 2026-03-20 |
| 自动步骤追踪 | Claw | ⏳ 待开始 | 2026-03-21 |
| 交互式菜单 | Claw | ⏳ 待开始 | 2026-03-22 |

### Phase 2 (下周)

| 任务 | 状态 | 截止日期 |
|------|------|---------|
| 进度可视化 | ⏳ | 2026-03-25 |
| 文档更新 | ⏳ | 2026-03-26 |

### Phase 3 (本月)

| 任务 | 状态 | 截止日期 |
|------|------|---------|
| 智能步骤跳过 | ⏳ | 2026-03-30 |
| CI/CD 集成 | ⏳ | 2026-03-31 |

---

**文档版本:** v1.0.0  
**最后更新:** 2026-03-19  
**下次审查:** 2026-03-26
