"""
SSE Event Streamer - Server-Sent Events for News Workflow Engine

Usage:
    python -m news_workflow.api.sse_server [--port 8080] [--config config/config.yaml]

Then visit http://localhost:8080/ in your browser.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from news_workflow.core.engine import NewsWorkflowEngine
import uvicorn

app = FastAPI(title="News Workflow Engine SSE")

# Global engine reference
_engine = None


# ── SSE Page ────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>News Workflow Engine — SSE Demo</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: ui-monospace, monospace; background: #0d1117; color: #e6edf3; padding: 16px; }
  h1 { font-size: 14px; color: #22d3ee; margin-bottom: 12px; }
  #status { font-size: 11px; color: #8b949e; margin-bottom: 12px; }
  #events { display: flex; flex-direction: column; gap: 4px; }
  .event { font-size: 11px; padding: 6px 8px; border-radius: 4px; background: #161b22; border-left: 3px solid #30363d; }
  .event.news { border-left-color: #58a6ff; }
  .event.workflow { border-left-color: #3fb950; }
  .event.task { border-left-color: #e3b341; }
  .event.alert { border-left-color: #f85149; }
  .event.system { border-left-color: #a78bfa; }
  .ts { color: #6e7681; margin-right: 8px; }
  .label { color: #8b949e; min-width: 90px; display: inline-block; }
  .msg { color: #e6edf3; }
</style>
</head>
<body>
<h1>News Workflow Engine — Live Events</h1>
<div id="status">Connecting...</div>
<div id="events"></div>
<script>
const events = document.getElementById('events');
const status = document.getElementById('status');
const ev = new EventSource('http://localhost:PORT/events');

ev.onopen = () => { status.textContent = 'Connected — streaming workflow events'; };
ev.onerror = () => { status.textContent = 'Disconnected — retrying...'; };

ev.addEventListener('news', e => {
  const d = JSON.parse(e.data);
  addEvent('news', 'NEWS', d.title || d.message || JSON.stringify(d).slice(0,80));
});

ev.addEventListener('workflow', e => {
  const d = JSON.parse(e.data);
  addEvent('workflow', 'WF', d.message || `workflow ${d.workflow_id} ${d.status}`);
});

ev.addEventListener('task', e => {
  const d = JSON.parse(e.data);
  addEvent('task', 'TASK', d.message || `task ${d.task_id} ${d.status}`);
});

ev.addEventListener('alert', e => {
  const d = JSON.parse(e.data);
  addEvent('alert', 'ALERT', d.message || JSON.stringify(d).slice(0,80));
});

ev.addEventListener('system', e => {
  const d = JSON.parse(e.data);
  addEvent('system', 'SYS', d.message || d.info || 'ping');
});

function addEvent(cls, label, msg) {
  const div = document.createElement('div');
  div.className = 'event ' + cls;
  const ts = new Date().toLocaleTimeString();
  div.innerHTML = '<span class="ts">' + ts + '</span><span class="label">' + label + '</span><span class="msg">' + esc(msg) + '</span>';
  events.appendChild(div);
  events.scrollTop = 1e9;
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
</script>
</body>
</html>"""

PORT = 8080


# ── SSE Stream ─────────────────────────────────────────────────────────────

@app.get("/")
async def get_page():
    return HTMLResponse(HTML.replace("PORT", str(PORT)))


@app.get("/events")
async def sse_events(request: Request):
    """Stream workflow events via SSE."""

    async def event_stream() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()

        # Register event callbacks on the engine
        def enqueue(event_type: str, data: dict):
            asyncio.create_task(queue.put((event_type, data)))

        if _engine is not None:
            # Wire up engine events
            _engine._sse_enqueue = enqueue

        # Send initial connection event
        yield "event: system\ndata: " + '{"info":"connected","time":"' + datetime.now().isoformat() + '"}\n\n'

        while True:
            if request.is_disconnected:
                break
            try:
                event_type, data = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: {event_type}\ndata: {data}\n\n"
            except asyncio.TimeoutError:
                # Keepalive
                yield "event: system\ndata: " + '{"info":"ping"}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Engine Wrapper with SSE Hooks ────────────────────────────────────────────

class SSENotifier:
    """Wraps NewsWorkflowEngine to emit SSE events."""

    def __init__(self, engine: NewsWorkflowEngine):
        self.engine = engine
        engine._sse_enqueue = lambda e, d: None  # no-op until connected

    async def emit(self, event_type: str, data: dict):
        if hasattr(self.engine, "_sse_enqueue"):
            self.engine._sse_enqueue(event_type, data)

    async def on_news(self, item: dict, analysis: dict):
        await self.emit("news", {
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "importance": analysis.get("importance", 0),
            "category": analysis.get("category", ""),
            "keywords": analysis.get("keywords", []),
        })

    async def on_workflow(self, workflow_id: int, status: str, analysis: dict):
        await self.emit("workflow", {
            "workflow_id": workflow_id,
            "status": status,
            "category": analysis.get("category", ""),
            "importance": analysis.get("importance", 0),
        })

    async def on_task(self, task_id: int, status: str, result: dict):
        await self.emit("task", {
            "task_id": task_id,
            "status": status,
            "success": result.get("success", False),
        })

    async def on_alert(self, workflow_id: int, analysis: dict):
        await self.emit("alert", {
            "workflow_id": workflow_id,
            "message": f"High importance workflow triggered: {analysis.get('category', 'unknown')}",
            "importance": analysis.get("importance", 0),
        })


def run_server(port: int, config_path: str):
    global _engine

    import asyncio
    from loguru import logger

    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")

    async def init_engine():
        engine = NewsWorkflowEngine(config_path)
        await engine.initialize()
        return engine

    # Start engine in background task
    _engine = asyncio.run(init_engine())
    sse = SSENotifier(_engine)

    # Monkey-patch process_news to emit events
    original_process = _engine.process_news

    async def process_news_with_sse(news_items):
        for item in news_items:
            analysis = await _engine.analyzer.analyze(item)
            threshold = _engine.config.get("analysis", {}).get("importance_threshold", 0.7)
            if analysis.get("importance", 0) >= threshold:
                news_id = await _engine._save_news(item, analysis)
                await sse.on_news(item, analysis)
                workflows = await _engine.workflow_manager.match_templates(analysis)
                for w_template in workflows:
                    wf_id = await _engine.workflow_manager.create_workflow(
                        template_id=w_template["id"],
                        news_id=news_id,
                        analysis=analysis,
                    )
                    if wf_id:
                        await sse.on_workflow(wf_id, "created", analysis)
                        imp_threshold = _engine.config.get("push", {}).get("importance_threshold", 0.8)
                        if analysis.get("importance", 0) >= imp_threshold:
                            await sse.on_alert(wf_id, analysis)
        return await original_process(news_items)

    _engine.process_news = process_news_with_sse

    logger.info(f"SSE server starting on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="News Workflow Engine SSE Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--config", default="config/config.yaml", help="Config file path")
    args = parser.parse_args()

    # Patch sys.argv so engine loads config correctly
    sys.argv = [__file__]
    run_server(args.port, args.config)


if __name__ == "__main__":
    main()
