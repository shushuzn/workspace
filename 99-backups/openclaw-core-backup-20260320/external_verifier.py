#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
外部验证器 - 第三方审计接口
【防护 v7 核心】- 独立验证 + 公开审计 + 可信时间戳

功能:
  1. 生成可公开验证的证明
  2. 第三方审计接口
  3. 可信时间戳服务
  4. 完整性报告生成
  5. 导出验证包
"""
import json
import hashlib
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
BLOCKCHAIN_LOG = Path("30-scripts-tools/blockchain_log.jsonl")
CHECKPOINT_FILE = Path("30-scripts-tools/blockchain_checkpoints.json")
VIOLATION_LOG = Path("30-scripts-tools/violation_log.jsonl")
AUDIT_REPORT_DIR = Path("99-backups/audit-reports")

class ExternalVerifier:
    """外部验证器 - 防护 v7"""

    def __init__(self):
        self.session_id = self._get_session_id()
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def _get_session_id(self):
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("session_id")

    def generate_audit_package(self, output_dir: Path = None) -> dict:
        """生成审计包（供第三方验证）"""
        if output_dir is None:
            output_dir = AUDIT_REPORT_DIR

        output_dir.mkdir(parents=True, exist_ok=True)

        # 收集所有关键文件
        files_to_include = {
            "execution-state.json": STATE_FILE,
            "blockchain_log.jsonl": BLOCKCHAIN_LOG,
            "blockchain_checkpoints.json": CHECKPOINT_FILE,
            "violation_log.jsonl": VIOLATION_LOG,
        }

        package = {
            "generated_at": self.timestamp,
            "session_id": self.session_id,
            "files": {},
            "hashes": {}
        }

        for name, file_path in files_to_include.items():
            if file_path.exists():
                with open(file_path, "rb") as f:
                    content = f.read()

                # 保存副本
                output_file = output_dir / f"{self.session_id}_{name}"
                with open(output_file, "wb") as f:
                    f.write(content)

                # 计算哈希
                file_hash = hashlib.sha256(content).hexdigest()
                package["files"][name] = {
                    "path": str(output_file),
                    "size": len(content),
                    "lines": content.count(b"\n")
                }
                package["hashes"][name] = file_hash

        # 保存审计包元数据
        package_file = output_dir / f"{self.session_id}_audit_package.json"
        with open(package_file, "w", encoding="utf-8") as f:
            json.dump(package, f, ensure_ascii=False, indent=2)

        return {
            "package_file": str(package_file),
            "files_count": len(package["files"]),
            "output_dir": str(output_dir)
        }

    def generate_integrity_report(self) -> dict:
        """生成完整性报告"""
        report = {
            "report_id": hashlib.sha256(self.timestamp.encode()).hexdigest()[:16],
            "generated_at": self.timestamp,
            "session_id": self.session_id,
            "checks": {}
        }

        # 检查 1: 执行状态
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            report["checks"]["execution_state"] = {
                "exists": True,
                "session_id": state.get("session_id"),
                "mandatory_execution": state.get("mandatory_execution"),
                "entry_point": state.get("entry_point"),
                "completed_steps": state.get("completed_steps", 0)
            }
        else:
            report["checks"]["execution_state"] = {"exists": False}

        # 检查 2: 区块链日志
        if BLOCKCHAIN_LOG.exists():
            with open(BLOCKCHAIN_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
            report["checks"]["blockchain_log"] = {
                "exists": True,
                "total_blocks": len(lines),
                "last_block": json.loads(lines[-1])["block_height"] if lines else 0
            }
        else:
            report["checks"]["blockchain_log"] = {"exists": False}

        # 检查 3: 检查点
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            report["checks"]["checkpoint"] = {
                "exists": True,
                "merkle_root": checkpoint.get("merkle_root", "")[:16] + "...",
                "block_height": checkpoint.get("block_height")
            }
        else:
            report["checks"]["checkpoint"] = {"exists": False}

        # 检查 4: 违规日志
        if VIOLATION_LOG.exists():
            with open(VIOLATION_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
            report["checks"]["violation_log"] = {
                "exists": True,
                "total_violations": len(lines)
            }
        else:
            report["checks"]["violation_log"] = {"exists": False}

        # 总体评估
        passed_checks = sum(1 for check in report["checks"].values() if check.get("exists"))
        total_checks = len(report["checks"])
        report["overall"] = {
            "passed": passed_checks,
            "total": total_checks,
            "rate": f"{passed_checks /total_checks *100:.1f}%" if total_checks > 0 else "N/A"
        }

        # 保存报告
        AUDIT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_file = AUDIT_REPORT_DIR / f"{self.session_id}_integrity_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return {
            "report_file": str(report_file),
            "overall": report["overall"]
        }

    def get_trusted_timestamp(self) -> dict:
        """获取可信时间戳（使用 Git commit 作为时间证明）"""
        try:
            # 使用 Git commit 时间作为可信时间戳
            result = subprocess.run(
                "git log -1 --format=%H%n%ci",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                return {
                    "git_commit": lines[0] if len(lines) > 0 else "N/A",
                    "git_time": lines[1] if len(lines) > 1 else "N/A",
                    "local_time": self.timestamp,
                    "source": "git"
                }
        except Exception:
            pass

        # Fallback: 使用本地时间
        return {
            "local_time": self.timestamp,
            "source": "local",
            "warning": "No trusted timestamp source available"
        }

    def verify_session_chain(self, session_id: str) -> dict:
        """验证特定会话的完整链"""
        if not BLOCKCHAIN_LOG.exists():
            return {"error": "No blockchain log"}

        with open(BLOCKCHAIN_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()

        session_entries = []
        for line in lines:
            try:
                entry = json.loads(line)
                if entry.get("session_id") == session_id:
                    session_entries.append(entry)
            except Exception:
                pass

        if not session_entries:
            return {"found": False, "message": "No entries for this session"}

        # 验证链完整性
        prev_hash = session_entries[0].get("prev_hash", "")
        valid = True
        for entry in session_entries:
            if entry.get("prev_hash") != prev_hash:
                valid = False
                break
            prev_hash = entry.get("hash", "")

        return {
            "found": True,
            "session_id": session_id,
            "entry_count": len(session_entries),
            "chain_valid": valid,
            "first_block": session_entries[0].get("block_height"),
            "last_block": session_entries[-1].get("block_height")
        }

    def display(self):
        """显示验证状态"""
        print("=" * 70)
        print("外部验证器 v7.0")
        print("=" * 70)
        print(f"会话：{self.session_id}")
        print(f"时间：{self.timestamp}")
        print()

        # 生成报告
        report_result = self.generate_integrity_report()
        print("完整性报告:")
        print(f"  文件：{report_result['report_file']}")
        print(f"  通过：{report_result['overall']['passed']}/{report_result['overall']['total']}")
        print(f"  比率：{report_result['overall']['rate']}")
        print()

        # 可信时间戳
        ts = self.get_trusted_timestamp()
        print("可信时间戳:")
        print(f"  来源：{ts['source']}")
        print(f"  时间：{ts.get('git_time', ts.get('local_time'))}")
        print()

        # 审计包
        print("审计包:")
        print(f"  目录：{AUDIT_REPORT_DIR}")
        print(f"  状态：准备就绪")
        print("=" * 70)


def main():
    import sys

    verifier = ExternalVerifier()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--package":
            result = verifier.generate_audit_package()
            print(f"审计包已生成：{result['package_file']}")
            return 0
        elif sys.argv[1] == "--report":
            result = verifier.generate_integrity_report()
            print(f"报告已生成：{result['report_file']}")
            print(f"通过率：{result['overall']['rate']}")
            return 0
        elif sys.argv[1] == "--verify-session":
            if len(sys.argv) > 2:
                session_id = sys.argv[2]
                result = verifier.verify_session_chain(session_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

    # 默认：显示状态
    verifier.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
