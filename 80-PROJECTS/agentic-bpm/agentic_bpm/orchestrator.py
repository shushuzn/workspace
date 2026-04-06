"""
Agentic BPM Orchestrator - 核心编排引擎
AI Agent 驱动的任务自动编排
"""

import json
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    priority: int = 5  # 1-10
    depends_on: List[str] = field(default_factory=list)
    result: Any = None
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""


@dataclass
class Workflow:
    """工作流定义"""
    id: str
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: str = "ready"  # ready, running, completed, failed
    current_task: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class AgenticOrchestrator:
    """
    Agentic BPM 核心编排器
    
    功能：
    1. AI 自动决策下一步做什么
    2. 任务依赖管理
    3. 工作流状态跟踪
    4. 与现有 workflow 系统集成
    """

    # 任务状态转移规则
    TRANSITIONS = {
        "pending": ["in_progress"],
        "in_progress": ["completed", "failed"],
        "completed": [],
        "failed": ["pending"]  # 可重试
    }

    def __init__(self, workflow_dir: str = ".agentic-bpm"):
        self.workflow_dir = Path(workflow_dir)
        self.workflow_dir.mkdir(exist_ok=True, parents=True)

        self.current_workflow: Optional[Workflow] = None
        self.task_history: List[Dict] = []

    # ============== 工作流管理 ==============

    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """创建新工作流"""
        import uuid
        wf = Workflow(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description
        )
        self.current_workflow = wf
        return wf

    def add_task(self, task: Task) -> str:
        """添加任务到当前工作流"""
        if not self.current_workflow:
            raise ValueError("No active workflow. Create one first.")

        self.current_workflow.tasks.append(task)
        return task.id

    def save_workflow(self):
        """保存工作流到文件"""
        if not self.current_workflow:
            return

        wf = self.current_workflow
        data = {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "status": wf.status,
            "current_task": wf.current_task,
            "created_at": wf.created_at,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "status": t.status,
                    "priority": t.priority,
                    "depends_on": t.depends_on,
                    "result": str(t.result) if t.result else None,
                    "error": t.error,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at
                }
                for t in wf.tasks
            ]
        }

        file_path = self.workflow_dir / f"{wf.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(file_path)

    def load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """加载工作流"""
        file_path = self.workflow_dir / f"{workflow_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        wf = Workflow(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            status=data["status"],
            current_task=data.get("current_task", ""),
            created_at=data["created_at"]
        )

        for t in data.get("tasks", []):
            task = Task(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                status=t["status"],
                priority=t.get("priority", 5),
                depends_on=t.get("depends_on", []),
                result=t.get("result"),
                error=t.get("error", ""),
                created_at=t["created_at"],
                completed_at=t.get("completed_at", "")
            )
            wf.tasks.append(task)

        self.current_workflow = wf
        return wf

    # ============== AI 决策 ==============

    def decide_next_task(self) -> Optional[Task]:
        """
        AI 决策：决定下一步做什么
        
        决策逻辑：
        1. 找出所有 pending 任务
        2. 检查依赖是否满足
        3. 按优先级排序
        4. 返回最高优先级的可执行任务
        """
        if not self.current_workflow:
            return None

        # 获取所有可执行的任务
        executable = []

        for task in self.current_workflow.tasks:
            if task.status != "pending":
                continue

            # 检查依赖
            deps = self._check_dependencies(task)
            if not deps:
                executable.append(task)

        if not executable:
            return None

        # 按优先级排序（高优先级在前）
        executable.sort(key=lambda t: -t.priority)

        return executable[0]

    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        if not task.depends_on:
            return True

        for dep_id in task.depends_on:
            dep_task = self._find_task(dep_id)
            if not dep_task or dep_task.status != "completed":
                return False

        return True

    # ============== 模板管理 ==============

    def load_template(self, template_name: str) -> Optional[Workflow]:
        """从模板加载工作流"""
        template_dir = Path(__file__).parent.parent / "templates"
        template_path = template_dir / f"{template_name}_workflow.json"

        if not template_path.exists():
            # 尝试直接名称
            template_path = template_dir / f"{template_name}.json"
            if not template_path.exists():
                return None

        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        wf = Workflow(
            id=data["id"] if "id" in data else str(uuid.uuid4())[:8],
            name=data["name"],
            description=data.get("description", "")
        )

        for t in data.get("tasks", []):
            task = Task(
                id=t["id"],
                name=t["name"],
                description=t.get("description", ""),
                priority=t.get("priority", 5),
                depends_on=t.get("depends_on", [])
            )
            wf.tasks.append(task)

        self.current_workflow = wf
        return wf

    def list_templates(self) -> list:
        """列出可用模板"""
        template_dir = Path(__file__).parent.parent / "templates"
        if not template_dir.exists():
            return []
        return [f.stem.replace("_workflow", "") for f in template_dir.glob("*_workflow.json")]

    def _find_task(self, task_id: str) -> Optional[Task]:
        """查找任务"""
        if not self.current_workflow:
            return None

        for task in self.current_workflow.tasks:
            if task.id == task_id:
                return task
        return None

    # ============== 执行控制 ==============

    def execute_next(self) -> Dict[str, Any]:
        """
        执行下一个任务
        
        Returns:
            执行结果字典
        """
        # AI 决策
        next_task = self.decide_next_task()

        if not next_task:
            # 没有可执行的任务
            if self.current_workflow:
                self.current_workflow.status = "completed"
            return {
                "status": "completed",
                "message": "No more tasks to execute"
            }

        # 更新状态
        next_task.status = "in_progress"
        self.current_workflow.current_task = next_task.id
        self.current_workflow.status = "running"

        # 记录历史
        self.task_history.append({
            "task_id": next_task.id,
            "task_name": next_task.name,
            "started_at": datetime.now().isoformat()
        })

        return {
            "status": "executing",
            "task_id": next_task.id,
            "task_name": next_task.name,
            "message": f"Ready to execute: {next_task.name}"
        }

    def complete_task(self, task_id: str, result: Any = None, error: str = ""):
        """完成任务"""
        task = self._find_task(task_id)
        if not task:
            return

        task.status = "completed" if not error else "failed"
        task.result = result
        task.error = error
        task.completed_at = datetime.now().isoformat()

        # 更新历史
        for h in self.task_history:
            if h["task_id"] == task_id and "completed_at" not in h:
                h["completed_at"] = datetime.now().isoformat()
                h["result"] = str(result) if result else None
                h["error"] = error
                break

        # 保存状态
        self.save_workflow()

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        if not self.current_workflow:
            return {"status": "no_workflow"}

        wf = self.current_workflow

        # 统计
        stats = {
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }

        for task in wf.tasks:
            stats[task.status] = stats.get(task.status, 0) + 1

        return {
            "workflow_id": wf.id,
            "workflow_name": wf.name,
            "status": wf.status,
            "current_task": wf.current_task,
            "stats": stats,
            "progress": stats["completed"] / len(wf.tasks) * 100 if wf.tasks else 0
        }

    # ============== 与现有系统集成 ==============

    def integrate_with_workflow_enforcer(self):
        """与 workflow_enforcer 集成"""
        try:
            sys.path.insert(0, '30-scripts-tools')
            from workflow_enforcer import WorkflowEnforcer
            from workflow_menu import WorkflowMenu

            # 同步状态
            menu = WorkflowMenu()
            state = menu.load_state()

            if state:
                # 从 workflow_enforcer 获取当前步骤
                current_step = state.get('current_step', 0)
                total_steps = state.get('total_steps', 17)

                # 自动创建对应任务
                self.create_workflow(
                    name=f"Workflow Step {current_step}",
                    description=f"Executing workflow step {current_step}/{total_steps}"
                )

            return True
        except Exception as e:
            print(f"Integration warning: {e}")
            return False


# 快速使用
if __name__ == "__main__":
    orchestrator = AgenticOrchestrator()

    # 创建工作流
    wf = orchestrator.create_workflow(
        name="Test Workflow",
        description="Test agentic BPM"
    )

    # 添加任务
    orchestrator.add_task(Task(
        id="t1",
        name="Step 1",
        description="First step",
        priority=10
    ))

    orchestrator.add_task(Task(
        id="t2",
        name="Step 2",
        description="Second step",
        priority=5,
        depends_on=["t1"]
    ))

    # 执行
    result = orchestrator.execute_next()
    print(f"Executing: {result}")

    # 完成
    orchestrator.complete_task("t1", result="Success")

    # 状态
    status = orchestrator.get_status()
    print(f"Status: {status}")