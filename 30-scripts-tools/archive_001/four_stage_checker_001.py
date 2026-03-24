#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FOUR-STAGE-CHECKER-001 四阶段流程检查器
检查代码是否遵循 ARCHITECT → CODE → ASK → DEBUG 流程
"""
import json, sys, re
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")
CHECK_LOG = Path("10-MEMORY/00-CORE/.four_stage_check_log.json")

REQUIRED_SECTIONS = {
    "ARCHITECT": [
        r"STAGE.*1.*ARCHITECT",
        r"Purpose",
        r"Data\s*Flow",
    ],
    "CODE": [
        r"STAGE.*2.*CODE",
        r"class\s+\w+",
        r"def\s+\w+\(",
    ],
    "ASK": [
        r"STAGE.*3.*ASK",
        r"py\s+\w+.*\.py",
    ],
    "DEBUG": [
        r"STAGE.*4.*DEBUG",
        r"Test",
        r"20\d{2}",
    ],
}

SECTION_WEIGHTS = {
    "ARCHITECT": 25,  # 架构设计 25%
    "CODE": 30,       # 代码实现 30%
    "ASK": 20,        # 询问确认 20%
    "DEBUG": 25,       # 调试测试 25%
}


class FourStageChecker:
    """检查代码是否遵循四阶段流程"""

    def __init__(self):
        self.log = self._load_log()

    def _load_log(self):
        if CHECK_LOG.exists():
            try:
                return json.loads(CHECK_LOG.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass
        return {"checks": [], "compliant": [], "non_compliant": []}

    def _save_log(self):
        CHECK_LOG.write_text(json.dumps(self.log, indent=2, ensure_ascii=False), encoding="utf-8")

    def check_file(self, file_path):
        """检查单个文件"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"file": str(file_path), "error": str(e), "score": 0, "stages": {}}

        results = {"file": str(file_path), "stages": {}, "score": 0, "missing": []}
        total_score = 0

        for stage, patterns in REQUIRED_SECTIONS.items():
            stage_score = 0
            matched = 0
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    matched += 1
            stage_score = (matched / len(patterns)) * SECTION_WEIGHTS[stage]
            results["stages"][stage] = {
                "matched": matched,
                "total": len(patterns),
                "score": stage_score
            }
            total_score += stage_score

            if matched < len(patterns):
                results["missing"].append(stage)

        results["score"] = total_score
        results["compliant"] = total_score >= 80

        return results

    def check_all(self):
        """检查所有工具"""
        print("\n[FOUR-STAGE-CHECKER-001] 四阶段流程检查")
        print("=" * 50)

        results = []
        compliant_count = 0

        for f in sorted(TOOLS_DIR.glob("*_001.py")):
            if f.name.startswith("__"):
                continue
            result = self.check_file(f)
            results.append(result)

            if result.get("compliant"):
                compliant_count += 1
                self.log["compliant"].append(f.name)
            else:
                self.log["non_compliant"].append(f.name)

        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Print summary
        total = len(results)
        print(f"\n[SUMMARY]")
        print(f"  Total tools: {total}")
        print(f"  Compliant: {compliant_count} ({compliant_count /total *100:.0f}%)")
        print(f"  Non-compliant: {total - compliant_count}")

        # Print top/bottom
        print(f"\n[TOP 5 - Best]")
        for r in results[:5]:
            score = r.get("score", 0)
            print(f"  {r['file']}: {score:.0f}%")

        print(f"\n[BOTTOM 5 - Need Work]")
        for r in results[-5:]:
            score = r.get("score", 0)
            missing = r.get("missing", [])
            print(f"  {r['file']}: {score:.0f}% (missing: {', '.join(missing)})")

        # Save log
        self.log["checks"].append({
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "compliant": compliant_count,
            "score": compliant_count / total * 100 if total else 0
        })
        self._save_log()

        return results

    def check_new_file(self, file_path):
        """检查新文件是否符合四阶段"""
        result = self.check_file(file_path)

        if result["score"] < 80:
            print(f"\n[WARNING] {file_path.name} not 4-stage compliant!")
            print(f"  Score: {result['score']:.0f}%")
            print(f"  Missing: {', '.join(result.get('missing', []))}")
            print(f"\n  Required sections:")
            for stage in ["ARCHITECT", "CODE", "ASK", "DEBUG"]:
                if stage in result.get("missing", []):
                    print(f"    - {stage}")
            return False

        print(f"\n[OK] {file_path.name} is 4-stage compliant ({result['score']:.0f}%)")
        return True


def main():
    checker = FourStageChecker()

    if "--check-all" in sys.argv:
        checker.check_all()

    elif "--check" in sys.argv and len(sys.argv) > 2:
        file_path = Path(sys.argv[2])
        if not file_path.exists():
            file_path = TOOLS_DIR / sys.argv[2]
        if file_path.exists():
            checker.check_new_file(file_path)
        else:
            print(f"[ERROR] File not found: {file_path}")

    elif "--template" in sys.argv:
        print("\n[FOUR-STAGE TEMPLATE]")
        print("=" * 50)
        template = FOUR_STAGE_TEMPLATE if 'FOUR_STAGE_TEMPLATE' in dir() else None
        print("""
┌─────────────────────────────────────────────────────────────┐
│  FOUR-STAGE CODING: ARCHITECT → CODE → ASK → DEBUG         │
├─────────────────────────────────────────────────────────────┤
│  STAGE 1: ARCHITECT - Purpose, Data Flow, Files, Edge Cases │
│  STAGE 2: CODE - Implementation with DEBUG comments         │
│  STAGE 3: ASK - Run verification, check output              │
# py four_stage_checker_001.py  # Run verification
│  STAGE 4: DEBUG - Test cases, edge cases, fixes            │
# Test: 2026
└─────────────────────────────────────────────────────────────┘
        """)

    else:
        print("\n[FOUR-STAGE-CHECKER-001]")
        print("  --check-all      Check all tools")
        print("  --check <file>   Check specific file")
        print("  --template       Show template")
        print("\n[Running check-all...]")
        checker.check_all()

if __name__ == "__main__":
    main()
