"""
文件存储
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class FileStorage:
    """
    文件存储系统
    
    功能:
    - JSON 文件存储
    - 自动备份
    - 批量读写
    """

    def __init__(self, storage_dir: Path, backup: bool = True):
        self.storage_dir = storage_dir
        self.backup = backup
        self.backup_dir = storage_dir.parent / 'backup' if backup else None

        # 确保目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if self.backup and self.backup_dir:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def save(self, memory_id: str, data: Dict) -> Path:
        """保存记忆"""
        # 备份
        if self.backup:
            self._backup(memory_id)

        # 保存
        file_path = self.storage_dir / f"{memory_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path

    def load(self, memory_id: str) -> Optional[Dict]:
        """加载记忆"""
        file_path = self.storage_dir / f"{memory_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        file_path = self.storage_dir / f"{memory_id}.json"

        if file_path.exists():
            # 移动到归档
            archive_dir = self.storage_dir / 'archived'
            archive_dir.mkdir(exist_ok=True)

            file_path.rename(archive_dir / f"{memory_id}.json")
            return True

        return False

    def list_all(self) -> List[str]:
        """列出所有记忆 ID"""
        ids = []

        for file_path in self.storage_dir.glob("*.json"):
            ids.append(file_path.stem)

        return ids

    def count(self) -> int:
        """统计记忆数量"""
        return len(list(self.storage_dir.glob("*.json")))

    def _backup(self, memory_id: str):
        """备份"""
        if not self.backup or not self.backup_dir:
            return

        src = self.storage_dir / f"{memory_id}.json"
        if src.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dst = self.backup_dir / f"{memory_id}_{timestamp}.json"

            import shutil
            shutil.copy2(src, dst)

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            'count': self.count(),
            'storage_dir': str(self.storage_dir),
            'backup_enabled': self.backup,
        }

    def __repr__(self):
        return f"FileStorage(count={self.count()}, dir={self.storage_dir})"
