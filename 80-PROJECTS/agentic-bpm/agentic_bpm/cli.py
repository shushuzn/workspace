"""
Agentic BPM CLI - Command Line Interface
"""
import click
import json
import sys
from pathlib import Path
from agentic_bpm import AgenticOrchestrator, Task, Workflow


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Agentic BPM - AI-Driven Business Process Management"""
    pass


@cli.command()
@click.argument("name")
@click.option("-d", "--description", default="", help="Workflow description")
def create(name, description):
    """Create a new workflow"""
    orch = AgenticOrchestrator()
    wf = orch.create_workflow(name, description)
    orch.save_workflow()
    click.echo(f"✅ Workflow created: {wf.id} ({name})")


@cli.command()
@click.argument("name")
@click.option("-d", "--description", default="", help="Task description")
@click.option("-p", "--priority", default=5, type=int, help="Priority 1-10")
@click.option("-D", "--depends-on", multiple=True, help="Task IDs this depends on")
def task(name, description, priority, depends_on):
    """Add a task to current workflow"""
    orch = AgenticOrchestrator()

    if not orch.current_workflow:
        # 尝试加载最新工作流
        wf_dir = orch.workflow_dir
        wf_files = list(wf_dir.glob("*.json"))
        if wf_files:
            wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            orch.load_workflow(wf_files[0].stem)

    if not orch.current_workflow:
        click.echo("❌ No active workflow. Create one first.", err=True)
        sys.exit(1)

    import uuid
    task_id = f"t{uuid.uuid4().hex[:4]}"

    task = Task(
        id=task_id,
        name=name,
        description=description,
        priority=priority,
        depends_on=list(depends_on)
    )

    orch.add_task(task)
    orch.save_workflow()

    click.echo(f"✅ Task added: {task_id} ({name})")


@cli.command()
def next():
    """Execute next task (AI decision)"""
    orch = AgenticOrchestrator()

    # 加载最新工作流
    wf_dir = orch.workflow_dir
    wf_files = list(wf_dir.glob("*.json"))
    if wf_files:
        wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        orch.load_workflow(wf_files[0].stem)

    if not orch.current_workflow:
        click.echo("❌ No workflow found.", err=True)
        sys.exit(1)

    result = orch.execute_next()

    click.echo(f"\n📋 {result.get('message', result['status'])}")
    click.echo(f"   Task: {result.get('task_name', 'N/A')}")

    # 显示状态
    status = orch.get_status()
    click.echo(f"\n📊 Progress: {status['progress']:.1f}%")
    click.echo(f"   Pending: {status['stats']['pending']}")
    click.echo(f"   Completed: {status['stats']['completed']}")


@cli.command()
@click.argument("task_id")
@click.option("-r", "--result", default="", help="Task result")
@click.option("-e", "--error", default="", help="Error message")
def complete(task_id, result, error):
    """Mark a task as completed"""
    orch = AgenticOrchestrator()

    # 加载最新工作流
    wf_dir = orch.workflow_dir
    wf_files = list(wf_dir.glob("*.json"))
    if wf_files:
        wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        orch.load_workflow(wf_files[0].stem)

    if not orch.current_workflow:
        click.echo("❌ No workflow found.", err=True)
        sys.exit(1)

    orch.complete_task(task_id, result=result, error=error)

    status = "✅" if not error else "❌"
    click.echo(f"{status} Task {task_id} completed")

    # 显示状态
    final_status = orch.get_status()
    click.echo(f"\n📊 Workflow Progress: {final_status['progress']:.1f}%")


@cli.command()
def status():
    """Show current workflow status"""
    orch = AgenticOrchestrator()

    # 加载最新工作流
    wf_dir = orch.workflow_dir
    wf_files = list(wf_dir.glob("*.json"))
    if wf_files:
        wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        orch.load_workflow(wf_files[0].stem)

    if not orch.current_workflow:
        click.echo("❌ No workflow found.")
        return

    status = orch.get_status()

    click.echo(f"\n{'=' *50}")
    click.echo(f"📋 Workflow: {status['workflow_name']}")
    click.echo(f"{'=' *50}")
    click.echo(f"Status: {status['status']}")
    click.echo(f"Progress: {status['progress']:.1f}%")
    click.echo(f"\n📊 Task Stats:")
    click.echo(f"  ⏳ Pending: {status['stats']['pending']}")
    click.echo(f"  🔄 In Progress: {status['stats']['in_progress']}")
    click.echo(f"  ✅ Completed: {status['stats']['completed']}")
    click.echo(f"  ❌ Failed: {status['stats']['failed']}")

    # 进度条
    if orch.current_workflow.tasks:
        total = len(orch.current_workflow.tasks)
        completed = status['stats']['completed']
        bar_len = 30
        filled = int(bar_len * completed / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        click.echo(f"\n[{bar}] {status['progress']:.1f}%")


@cli.command()
def list():
    """List all workflows"""
    orch = AgenticOrchestrator()
    wf_dir = orch.workflow_dir

    wf_files = list(wf_dir.glob("*.json"))
    wf_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    if not wf_files:
        click.echo("No workflows found.")
        return

    click.echo(f"\n📁 Total workflows: {len(wf_files)}")

    for f in wf_files[:10]:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)

        task_count = len(data.get('tasks', []))
        completed = sum(1 for t in data.get('tasks', []) if t['status'] == 'completed')
        progress = completed / task_count * 100 if task_count > 0 else 0

        click.echo(f"\n  📋 {data['name']} ({data['id']})")
        click.echo(f"     Status: {data['status']}")
        click.echo(f"     Progress: {completed}/{task_count} ({progress:.0f}%)")


@cli.group()
def template():
    """Template management"""
    pass


@template.command("list")
def template_list():
    """List available templates"""
    orch = AgenticOrchestrator()
    templates = orch.list_templates()

    if not templates:
        click.echo("No templates found.")
        return

    click.echo(f"\n📦 Available templates: {len(templates)}")
    for t in templates:
        click.echo(f"  • {t}")


@template.command("load")
@click.argument("template_name")
def template_load(template_name):
    """Load a workflow from template"""
    orch = AgenticOrchestrator()
    wf = orch.load_template(template_name)

    if not wf:
        click.echo(f"❌ Template not found: {template_name}", err=True)
        sys.exit(1)

    orch.save_workflow()
    click.echo(f"✅ Template loaded: {wf.name} ({wf.id})")
    click.echo(f"   Tasks: {len(wf.tasks)}")


@cli.command()
@click.argument("workflow_id")
def load(workflow_id):
    """Load a specific workflow"""
    orch = AgenticOrchestrator()
    wf = orch.load_workflow(workflow_id)

    if not wf:
        click.echo(f"❌ Workflow not found: {workflow_id}", err=True)
        sys.exit(1)

    click.echo(f"✅ Loaded workflow: {wf.name} ({wf.id})")

    # 显示任务
    if wf.tasks:
        click.echo(f"\n📋 Tasks ({len(wf.tasks)}):")
        for t in wf.tasks:
            icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "failed": "❌"}.get(t.status, "❓")
            deps = f" (depends: {', '.join(t.depends_on)})" if t.depends_on else ""
            click.echo(f"  {icon} {t.id}: {t.name}{deps}")


if __name__ == "__main__":
    cli()