"""
Agentic BPM - AI-Driven Business Process Management
"""

__version__ = "0.1.0"
__author__ = "OpenClaw"

from .orchestrator import AgenticOrchestrator, Task, Workflow

__all__ = ["AgenticOrchestrator", "Task", "Workflow", "load_template", "list_templates"]