"""
Agentic BPM REST API Server
Exposes BPM workflows and tasks via HTTP JSON API.
"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import uvicorn

from agentic_bpm import AgenticOrchestrator, Task, Workflow


app = FastAPI(title="Agentic BPM API", version="0.1.0")
_orch = AgenticOrchestrator()


# ─── Request/Response models ─────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    name: str
    description: str = ""


class CreateTaskRequest(BaseModel):
    name: str
    description: str = ""
    priority: int = 5
    depends_on: list[str] = []


class CompleteTaskRequest(BaseModel):
    result: str = ""
    error: str = ""


class LoadWorkflowRequest(BaseModel):
    workflow_id: str


# ─── Workflow endpoints ──────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "agentic-bpm-api"}


@app.get("/workflows")
def list_workflows():
    """List all workflows."""
    wf_dir = _orch.workflow_dir
    files = sorted(wf_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    result = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        task_count = len(data.get('tasks', []))
        completed = sum(1 for t in data.get('tasks', []) if t['status'] == 'completed')
        result.append({
            "id": data["id"],
            "name": data["name"],
            "description": data.get("description", ""),
            "status": data["status"],
            "progress": completed / task_count * 100 if task_count > 0 else 0,
            "task_count": task_count,
            "completed": completed,
            "created_at": data.get("created_at", ""),
        })
    return JSONResponse(result)


@app.post("/workflows")
def create_workflow(body: CreateWorkflowRequest):
    """Create a new workflow."""
    wf = _orch.create_workflow(body.name, body.description)
    _orch.save_workflow()
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "status": wf.status,
        "created_at": wf.created_at,
    }


@app.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    """Get workflow details."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "status": wf.status,
        "current_task": wf.current_task,
        "progress": _orch.get_status()["progress"],
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
                "completed_at": t.completed_at,
            }
            for t in wf.tasks
        ],
        "created_at": wf.created_at,
    }


# ─── Task endpoints ─────────────────────────────────────────────────

@app.post("/workflows/{workflow_id}/tasks")
def create_task(workflow_id: str, body: CreateTaskRequest):
    """Add a task to a workflow."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    if not _orch.current_workflow:
        _orch.current_workflow = wf

    import uuid
    task_id = f"t{uuid.uuid4().hex[:4]}"
    task = Task(
        id=task_id,
        name=body.name,
        description=body.description,
        priority=body.priority,
        depends_on=body.depends_on,
    )
    _orch.add_task(task)
    _orch.save_workflow()
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "depends_on": task.depends_on,
    }


@app.post("/workflows/{workflow_id}/tasks/{task_id}/complete")
def complete_task(workflow_id: str, task_id: str, body: CompleteTaskRequest):
    """Mark a task as completed."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    if not _orch.current_workflow:
        _orch.current_workflow = wf

    _orch.complete_task(task_id, result=body.result if body.result else None, error=body.error)
    return {"id": task_id, "status": "completed"}


@app.get("/workflows/{workflow_id}/tasks/{task_id}")
def get_task(workflow_id: str, task_id: str):
    """Get task details."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    task = _orch._find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "depends_on": task.depends_on,
        "result": str(task.result) if task.result else None,
        "error": task.error,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
    }


# ─── Execution endpoints ───────────────────────────────────────────

@app.post("/workflows/{workflow_id}/execute-next")
def execute_next(workflow_id: str):
    """Execute the next pending task (AI decision)."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    if not _orch.current_workflow:
        _orch.current_workflow = wf

    result = _orch.execute_next()
    return result


@app.get("/workflows/{workflow_id}/status")
def get_workflow_status(workflow_id: str):
    """Get workflow execution status."""
    wf = _orch.load_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    if not _orch.current_workflow:
        _orch.current_workflow = wf
    return _orch.get_status()


# ─── CLI server command ─────────────────────────────────────────────

def run_server(host: str = "127.0.0.1", port: int = 8765):
    """Run the REST API server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port=port)
