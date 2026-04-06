"""
bpmn_parser.py — Parse .bpmn files and export task-orchestrator JSON.

Usage:
  python -m agentic_bpm.bpmn_parser workflow.bpmn
  python -m agentic_bpm.bpmn_parser workflow.bpmn --output tasks.json
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


BPMN_NS = {None: "http://www.omg.org/spec/BPMN/20100524/MODEL"}

def parse_bpmn(bpmn_path: str) -> dict:
    """Parse a BPMN XML file and return task-orchestrator JSON."""
    tree = ET.parse(bpmn_path)
    root = tree.getroot()

    ns = BPMN_NS

    # Find all tasks
    tasks = []
    edges = []
    task_id_map = {}

    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if tag == "task":
            tid = elem.get("id")
            name = elem.get("name", tid)
            task_id_map[tid] = name
            tasks.append({
                "id": tid,
                "name": name,
                "type": "task",
                "status": "pending",
            })

        elif tag == "startEvent":
            tid = elem.get("id")
            name = elem.get("name", "Start")
            tasks.append({
                "id": tid,
                "name": name,
                "type": "start",
                "status": "ready",
            })

        elif tag == "endEvent":
            tid = elem.get("id")
            name = elem.get("name", "End")
            tasks.append({
                "id": tid,
                "name": name,
                "type": "end",
                "status": "pending",
            })

        elif tag == "exclusiveGateway":
            tid = elem.get("id")
            name = elem.get("name", "Gateway")
            task_id_map[tid] = name
            tasks.append({
                "id": tid,
                "name": name,
                "type": "gateway",
                "gatewayType": "exclusive",
                "status": "pending",
            })

        elif tag == "inclusiveGateway":
            tid = elem.get("id")
            name = elem.get("name", "Inclusive Gateway")
            task_id_map[tid] = name
            tasks.append({
                "id": tid,
                "name": name,
                "type": "gateway",
                "gatewayType": "inclusive",
                "status": "pending",
            })

        elif tag == "parallelGateway":
            tid = elem.get("id")
            name = elem.get("name", "Parallel Gateway")
            task_id_map[tid] = name
            tasks.append({
                "id": tid,
                "name": name,
                "type": "gateway",
                "gatewayType": "parallel",
                "status": "pending",
            })

        elif tag == "sequenceFlow":
            src = elem.get("sourceRef")
            tgt = elem.get("targetRef")
            if src and tgt:
                edges.append({"from": src, "to": tgt})

    result = {
        "tasks": tasks,
        "edges": edges,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Parse .bpmn file to task-orchestrator JSON")
    parser.add_argument("bpmn_file", help="Path to .bpmn file")
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    if not Path(args.bpmn_file).exists():
        print(f"❌ File not found: {args.bpmn_file}", file=sys.stderr)
        sys.exit(1)

    result = parse_bpmn(args.bpmn_file)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ Exported {len(result['tasks'])} tasks, {len(result['edges'])} edges → {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
