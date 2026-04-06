"""History analysis engine for OpenViking sessions.

Scans historical sessions to extract topics, outcomes, and patterns,
then generates a capability-gap report for discovering new agent capabilities.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import urllib.parse
from collections import Counter
from typing import Optional

log = logging.getLogger("openviking-mcp.analyzer")

OV_BASE = os.environ.get("VIKING_BASE_URL", "http://127.0.0.1:1933")
OV_API_KEY = os.environ.get("VIKING_API_KEY", "")
OV_ACCOUNT = os.environ.get("VIKING_ACCOUNT", "default")
OV_USER = os.environ.get("VIKING_USER", "default")

# ─── Keywords for topic extraction ─────────────────────────────────────────────

TOPIC_KEYWORDS = {
    "代码/开发": ["code", "function", "class", "import", "module", "api", "bug", "fix", "refactor", "implement", "测试", "代码", "函数", "接口", "调试"],
    "文档/写作": ["readme", "docs", "document", "write", "markdown", "comment", "文档", "写作", "说明"],
    "数据分析": ["analysis", "data", "analytics", "metric", "chart", "visualize", "分析", "数据", "图表"],
    "研究/调研": ["research", "explore", "investigate", "survey", "study", "研究", "调研", "探索"],
    "项目管理": ["task", "project", "issue", "planning", "milestone", "任务", "项目", "计划"],
    "AI/ML": ["model", "training", "llm", "embedding", "prompt", "agent", "ai", "ml", "rl", "模型", "训练", "智能体"],
    "DevOps/运维": ["deploy", "ci", "cd", "pipeline", "docker", "kubernetes", "monitoring", "部署", "运维", "CI"],
    "浏览器/自动化": ["browser", "click", "navigate", "scrape", "crawl", "selenium", "浏览器", "自动化", "抓取"],
    "API/集成": ["mcp", "api", "rest", "graphql", "webhook", "integration", "集成", "接口"],
    "辩论/讨论": ["debate", "discuss", "argument", "opinion", "perspective", "辩论", "讨论", "观点"],
}

OUTCOME_KEYWORDS = {
    "success": ["shipped", "completed", "done", "success", "fixed", "implemented", "merged", "完成", "成功", "修复"],
    "failure": ["failed", "error", "broken", "crash", "block", "stuck", "失败", "错误", "阻塞"],
    "partial": ["partial", "incomplete", "timeout", "cancelled", "部分", "超时", "取消"],
}

# ─── Session Fetching ──────────────────────────────────────────────────────────

def _curl(method: str, path: str, data: dict = None) -> dict:
    url = f"{OV_BASE}{path}"
    cmd = ["curl", "-s", "--noproxy", "*", "-X", method, url,
           "-H", "Content-Type: application/json"]
    if OV_API_KEY:
        cmd.extend(["-H", f"X-API-Key: {OV_API_KEY}"])
    cmd.extend([
        "-H", f"X-OpenViking-Account: {OV_ACCOUNT}",
        "-H", f"X-OpenViking-User: {OV_USER}"
    ])
    if data:
        cmd.extend(["-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def _get_all_sessions() -> list[dict]:
    """Fetch all sessions for the current account."""
    try:
        result = _curl("GET", "/api/v1/sessions")
        return result.get("result", []) if isinstance(result, dict) else []
    except Exception:
        return []


def _get_session_messages(session_id: str) -> list[dict]:
    """Fetch messages for a session."""
    try:
        result = _curl("GET", f"/api/v1/sessions/{session_id}/messages")
        return result.get("result", []) if isinstance(result, dict) else []
    except Exception:
        return []


def _get_session_info(session_id: str) -> dict:
    """Fetch session info."""
    try:
        result = _curl("GET", f"/api/v1/sessions/{session_id}")
        return result.get("result", {}) if isinstance(result, dict) else {}
    except Exception:
        return {}


# ─── Topic Extraction ──────────────────────────────────────────────────────────

def extract_topics(messages: list[dict]) -> list[str]:
    """Extract topic tags from session messages."""
    all_text = " ".join(
        msg.get("content", "") for msg in messages
        if isinstance(msg.get("content"), str)
    ).lower()
    topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw.lower() in all_text for kw in keywords):
            topics.append(topic)
    return topics if topics else ["其他"]


def extract_outcome(messages: list[dict]) -> str:
    """Determine session outcome from message content."""
    all_text = " ".join(
        msg.get("content", "") for msg in messages
        if isinstance(msg.get("content"), str)
    ).lower()
    scores = {"success": 0, "failure": 0, "partial": 0}
    for outcome, keywords in OUTCOME_KEYWORDS.items():
        for kw in keywords:
            scores[outcome] += all_text.count(kw.lower())
    if scores["success"] > scores["failure"] and scores["success"] > scores["partial"]:
        return "success"
    if scores["failure"] > 0:
        return "failure"
    return "partial"


def extract_projects(messages: list[dict]) -> list[str]:
    """Extract project names from messages (look for paths)."""
    import re
    all_text = " ".join(
        msg.get("content", "") for msg in messages
        if isinstance(msg.get("content"), str)
    )
    # Match common project path patterns
    paths = re.findall(r'(?:80-PROJECTS|projects?|workspace)[\/\\][\w\-\.]+', all_text, re.IGNORECASE)
    # Deduplicate and clean
    seen = set()
    projects = []
    for p in paths:
        clean = re.sub(r'^.*?80-PROJECTS[\\\/]', '', p)
        clean = re.sub(r'[\\\/].*$', '', clean).strip()
        if clean and clean not in seen:
            seen.add(clean)
            projects.append(clean)
    return projects[:5]  # cap at 5


def extract_patterns(messages: list[dict]) -> list[str]:
    """Extract behavioral patterns from messages."""
    patterns = []
    all_text = " ".join(
        msg.get("content", "") for msg in messages
        if isinstance(msg.get("content"), str)
    )
    if "brainstorm" in all_text:
        patterns.append("头脑风暴")
    if "implement" in all_text or "执行" in all_text:
        patterns.append("执行驱动")
    if "review" in all_text or "检查" in all_text:
        patterns.append("审查驱动")
    if "test" in all_text or "测试" in all_text:
        patterns.append("测试优先")
    if "deploy" in all_text or "部署" in all_text:
        patterns.append("部署导向")
    return patterns


# ─── Capability Gap Detection ──────────────────────────────────────────────────

CAPABILITY_KEYWORDS = {
    "browser_automation": ["browser", "click", "navigate", "scrape", "selenium", "playwright", "浏览器", "抓取"],
    "code_analysis": ["semgrep", "ast", "tree-sitter", "lint", "code analysis", "代码分析"],
    "api_design": ["rest", "graphql", "endpoint", "api design", "接口设计"],
    "data_visualization": ["d3", "chart", "visualize", "plot", "可视化", "图表"],
    "trading_system": ["trading", "backtest", "market data", "signal", "交易", "回测"],
    "knowledge_graph": ["knowledge graph", "entity extraction", "context injection", "知识图谱"],
    "multi_agent": ["debate", "multi-agent", "roundtable", "coordination", "辩论", "多智能体"],
    "rl_training": ["reward", "policy", "grpo", "prm", "reinforcement", "强化学习"],
    "sentiment_analysis": ["sentiment", "emotion", "news analysis", "情绪", "情感分析"],
    "context_memory": ["session", "context", "memory", "recall", "会话", "记忆"],
}

NEVER_USED_KEYWORDS = {
    "browser_automation": ["openc", "opencli"],
    "code_analysis": ["semgrep", "tree-sitter", "code-agent"],
    "api_design": ["fastapi", "express", "rest"],
    "data_visualization": ["d3", "chart", "可视化"],
    "trading_system": ["alpha_vantage", "trading_engine"],
    "knowledge_graph": ["scrapeToGraph", "knowledge-bridge"],
    "multi_agent": ["multi-agent-hub", "debate"],
    "rl_training": ["rl-trading", "reward"],
    "sentiment_analysis": ["news", "sentiment"],
    "context_memory": ["openviking", "session"],
}


def detect_capability_gaps(topics_per_session: list[list[str]], patterns_per_session: list[list[str]]) -> dict:
    """Detect capability gaps — topics that were worked on but related capabilities not invoked."""
    # Topics worked on
    all_topics = [t for topics in topics_per_session for t in topics]
    topic_counts = Counter(all_topics)

    # Capabilities that were NOT mentioned across all sessions
    all_text_blob = " ".join(
        " ".join(patterns) for patterns in patterns_per_session
    ).lower()

    gaps = {}
    for cap, keywords in CAPABILITY_KEYWORDS.items():
        mentioned = any(kw.lower() in all_text_blob for kw in keywords)
        if not mentioned:
            gaps[cap] = {
                "evidence": f"Topic '{topic_counts.most_common(1)[0][0] if topic_counts else 'N/A'}' worked on but '{cap}' never invoked",
                "topic_frequency": dict(topic_counts.most_common(3)),
            }
    return gaps


# ─── Main Analysis ─────────────────────────────────────────────────────────────

def analyze_history(limit: int = 20) -> str:
    """Analyze historical sessions and generate capability gap report."""
    try:
        sessions = _get_all_sessions()
        if not sessions:
            return json.dumps({"success": False, "error": "No sessions found"}, ensure_ascii=False)

        # Take most recent N sessions
        sessions = sessions[:limit]

        results = []
        topics_counter = Counter()
        outcome_counter = Counter()
        projects_counter = Counter()
        patterns_counter = Counter()

        for sess in sessions:
            sid = sess.get("session_id", "")
            if not sid:
                continue
            messages = _get_session_messages(sid)
            if not messages:
                continue

            topics = extract_topics(messages)
            outcome = extract_outcome(messages)
            projects = extract_projects(messages)
            patterns = extract_patterns(messages)

            for t in topics:
                topics_counter[t] += 1
            outcome_counter[outcome] += 1
            for p in projects:
                projects_counter[p] += 1
            for pt in patterns:
                patterns_counter[pt] += 1

            results.append({
                "session_id": sid[:8] + "...",
                "topics": topics,
                "outcome": outcome,
                "projects": projects,
                "patterns": patterns,
                "message_count": len(messages),
            })

        # Capability gap detection
        topics_per_session = [r["topics"] for r in results]
        patterns_per_session = [r["patterns"] for r in results]
        gaps = detect_capability_gaps(topics_per_session, patterns_per_session)

        # Build markdown report
        md_lines = [
            "# OpenViking Capability Gap Report",
            "",
            f"**Sessions analyzed:** {len(results)}",
            f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Topic Distribution",
            "",
        ]
        for topic, count in topics_counter.most_common():
            pct = count / len(results) * 100
            md_lines.append(f"- **{topic}**: {count} sessions ({pct:.0f}%)")

        md_lines.extend(["", "## Outcome Distribution", ""])
        for outcome, count in outcome_counter.most_common():
            pct = count / len(results) * 100
            md_lines.append(f"- **{outcome}**: {count} ({pct:.0f}%)")

        if projects_counter:
            md_lines.extend(["", "## Projects Worked On", ""])
            for proj, count in projects_counter.most_common(10):
                md_lines.append(f"- `{proj}`: {count} sessions")

        if patterns_counter:
            md_lines.extend(["", "## Behavioral Patterns", ""])
            for pat, count in patterns_counter.most_common():
                pct = count / len(results) * 100
                md_lines.append(f"- **{pat}**: {count} ({pct:.0f}%)")

        if gaps:
            md_lines.extend(["", "## Capability Gaps (Opportunities)", ""])
            md_lines.append("*These capabilities were not invoked in analyzed sessions but may be relevant based on topics:*")
            md_lines.append("")
            for cap, info in gaps.items():
                md_lines.append(f"### {cap.replace('_', ' ').title()}")
                md_lines.append(f"- **Evidence:** {info['evidence']}")
                md_lines.append(f"- **Related topics:** {', '.join(info['topic_frequency'].keys())}")
                md_lines.append("")
        else:
            md_lines.extend(["", "## Capability Gaps", "", "No obvious gaps detected — all major capabilities have been exercised."])

        md_lines.extend(["", "## Recent Sessions", ""])
        md_lines.append("| Session | Topics | Outcome | Projects | Patterns |")
        md_lines.append("|---------|--------|---------|---------|---------|")
        for r in results[:10]:
            topics_str = ", ".join(r["topics"])
            projects_str = ", ".join(r["projects"]) or "-"
            patterns_str = ", ".join(r["patterns"]) or "-"
            md_lines.append(f"| `{r['session_id']}` | {topics_str} | {r['outcome']} | {projects_str} | {patterns_str} |")

        report = "\n".join(md_lines)
        return json.dumps({
            "success": True,
            "sessions_analyzed": len(results),
            "topic_distribution": dict(topics_counter.most_common()),
            "outcome_distribution": dict(outcome_counter),
            "projects": dict(projects_counter.most_common(10)),
            "patterns": dict(patterns_counter.most_common()),
            "capability_gaps": list(gaps.keys()),
            "report": report,
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        log.exception("analyze_history failed")
        return json.dumps({"success": False, "error": str(e)})


# Alias for MCP tool naming
session_analyze = analyze_history
