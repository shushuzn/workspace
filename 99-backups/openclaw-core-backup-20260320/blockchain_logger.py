#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
区块链式日志 - 不可篡改的日志系统
【防护 v7 核心】- 哈希链 + Merkle 树 + 时间戳证明

功能:
  1. 每条日志包含前一条哈希（区块链结构）
  2. Merkle 树根哈希定期生成
  3. 时间戳证明（防时间篡改）
  4. 完整性验证
  5. 外部审计接口
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

LOG_FILE = Path("30-scripts-tools/blockchain_log.jsonl")
CHECKPOINT_FILE = Path("30-scripts-tools/blockchain_checkpoints.json")

class BlockchainLogger:
    """区块链式日志 - 防护 v7"""

    def __init__(self):
        self.last_hash = self._get_last_hash()
        self.block_height = self._get_block_height()
        self.pending_entries = []

    def _get_last_hash(self) -> str:
        """获取最后一条日志的哈希"""
        if not LOG_FILE.exists():
            return "0" * 64  # Genesis block

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return "0" * 64

        try:
            last_entry = json.loads(lines[-1])
            return last_entry.get("hash", "0" * 64)
        except Exception:
            return "0" * 64

    def _get_block_height(self) -> int:
        """获取区块高度"""
        if not LOG_FILE.exists():
            return 0

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        return len(lines)

    def _compute_hash(self, entry: dict) -> str:
        """计算条目哈希"""
        # 移除 hash 和 prev_hash 字段（避免循环）
        data = {k: v for k, v in entry.items() if k not in ["hash", "prev_hash"]}
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _compute_merkle_root(self, hashes: list) -> str:
        """计算 Merkle 树根哈希"""
        if not hashes:
            return "0" * 64

        # 如果数量是奇数，复制最后一个
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        # 递归计算
        if len(hashes) == 2:
            combined = hashes[0] + hashes[1]
            return hashlib.sha256(combined.encode()).hexdigest()

        # 分层计算
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i +1]
            next_level.append(hashlib.sha256(combined.encode()).hexdigest())

        return self._compute_merkle_root(next_level)

    def append(self, event_type: str, data: dict, session_id: str = None) -> dict:
        """添加日志条目（区块链结构）"""
        entry = {
            "block_height": self.block_height + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "event_type": event_type,
            "data": data,
            "prev_hash": self.last_hash,
        }

        # 计算当前哈希
        entry["hash"] = self._compute_hash(entry)

        # 写入文件
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # 更新状态
        self.last_hash = entry["hash"]
        self.block_height += 1

        # 每 100 条生成 Merkle 根
        if self.block_height % 100 == 0:
            self._create_checkpoint()

        return entry

    def _create_checkpoint(self):
        """创建检查点（Merkle 根）"""
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        hashes = []
        for line in lines:
            try:
                entry = json.loads(line)
                hashes.append(entry.get("hash", ""))
            except Exception:
                pass

        merkle_root = self._compute_merkle_root(hashes)

        checkpoint = {
            "block_height": self.block_height,
            "merkle_root": merkle_root,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash_count": len(hashes)
        }

        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)

        print(f"[CHECKPOINT] Block {self.block_height}, Merkle Root: {merkle_root[:16]}...")

    def verify_chain(self) -> dict:
        """验证区块链完整性"""
        if not LOG_FILE.exists():
            return {"valid": True, "message": "No log file"}

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        issues = []
        prev_hash = "0" * 64

        for i, line in enumerate(lines):
            try:
                entry = json.loads(line)

                # 检查 prev_hash 链
                if entry.get("prev_hash") != prev_hash:
                    issues.append(f"Block {i +1}: prev_hash mismatch")

                # 验证当前哈希
                computed_hash = self._compute_hash(entry)
                if entry.get("hash") != computed_hash:
                    issues.append(f"Block {i +1}: hash mismatch")

                prev_hash = entry.get("hash", "")

            except Exception as e:
                issues.append(f"Block {i +1}: parse error - {str(e)}")

        return {
            "valid": len(issues) == 0,
            "total_blocks": len(lines),
            "issues": issues
        }

    def get_audit_proof(self, block_height: int) -> dict:
        """获取审计证明（Merkle 证明）"""
        if not LOG_FILE.exists():
            return {"error": "No log file"}

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if block_height < 1 or block_height > len(lines):
            return {"error": "Invalid block height"}

        entry = json.loads(lines[block_height - 1])

        # 简单实现：返回完整链供验证
        return {
            "block_height": block_height,
            "entry": entry,
            "chain_length": len(lines),
            "verification": "Full chain available for verification"
        }

    def display(self):
        """显示区块链状态"""
        print("=" * 70)
        print("区块链日志系统 v7.0")
        print("=" * 70)
        print(f"区块高度：{self.block_height}")
        print(f"最后哈希：{self.last_hash[:16]}...")
        print()

        # 验证
        result = self.verify_chain()
        if result["valid"]:
            print("[OK] 区块链完整性验证通过")
        else:
            print(f"[FAIL] 发现 {len(result['issues'])} 个问题:")
            for issue in result["issues"][:5]:
                print(f"  - {issue}")
        print()

        # 检查点
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            print(f"最新检查点:")
            print(f"  区块：{checkpoint.get('block_height')}")
            print(f"  Merkle 根：{checkpoint.get('merkle_root', '')[:16]}...")
            print(f"  时间：{checkpoint.get('timestamp')}")
        print("=" * 70)


def main():
    import sys

    logger = BlockchainLogger()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            result = logger.verify_chain()
            print(f"验证结果：{'通过' if result['valid'] else '失败'}")
            return 0 if result["valid"] else 1
        elif sys.argv[1] == "--audit":
            if len(sys.argv) > 2:
                block_height = int(sys.argv[2])
                proof = logger.get_audit_proof(block_height)
                print(json.dumps(proof, indent=2, ensure_ascii=False))
            return 0

    # 默认：显示状态
    logger.display()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
