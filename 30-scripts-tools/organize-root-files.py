#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""整理根目录散落文件 - 简化版"""

import os
import shutil
import sys
import io
from pathlib import Path

# 修复编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = r"D:\OpenClaw\workspace"

# 分类映射：文件名前缀/关键词 -> 目标目录
CATEGORIES = {
    # 研究报告类
    '10-RESEARCH/domain-research/领域研究/lig-conductivity-prediction-zenodo/docs': [
        'RESEARCH', 'ANALYSIS', 'INNOVATION', 'REPORT', 'SUMMARY',
        'BREAKTHROUGH', 'CAUSAL', 'EVALUATION', 'HEALTH',
        'PHASE', 'ITERATION', 'MISSION', 'BEYOND',
        'ARXIV', 'MEMORY', 'DASHBOARD', 'DEPLOYMENT', 'SECURITY',
        'OPTIMIZATION', 'INTEGRATION', 'GUIDE', 'PLAN', 'CHECKLIST',
        'AUDIT', 'VERIFICATION', 'PROGRESS', 'FINAL', 'COMPLETE',
        'STATUS', 'PROTECTION', 'INNOVATOR', 'PLANNER', 'CRITIC',
        'WORKFLOW', 'OBSIDIAN', 'CONTEXT', 'FEDERATED', 'ENERGY',
        'PRIVACY', 'SELF-ITERATION', 'NEW-SESSION', 'ERROR-PREVENTION',
        'IDENTITY', 'PROJECT-MAP', 'PROJECTS-INDEX', 'WORKSPACE-GUIDE',
        'WORKSPACE-INDEX', 'STOCK-ANALYZER', 'WEBSITE-ITERATION',
        'DYNAMIC-MEMORY', 'MEMORY-EVOLUTION', 'MEMORY-INTEGRATION',
        'MEMORY-OPTIMIZATION', 'MEMORY-DASHBOARD', 'PHASE1', 'PHASE2',
        'PHASE3', 'PHASE5', 'PHASE6', 'PHASE7', 'SESSION-COMPLETE',
        'SESSION-FINAL', 'SESSION-STATUS', 'SESSION-BREAKTHROUGH',
        'PERSONA-V4', 'DEFAULT-DASHBOARD', 'DEPLOY-GUIDE',
        'NATURAL-LANGUAGE', 'GIT-WORKFLOW', 'BIG-FILES',
        'SELF-CORRECTING', 'SELF-EVOLVING', 'SELF-HEALING',
        'MULTI-AGENT', 'MULTI-MODAL', 'ADAPTIVE', 'SMART',
        'PEER', 'SOCIAL', 'INSIDER', 'BRAIN', '00-', '100-'
    ],
    
    # 脚本工具
    '30-scripts-tools': [
        '.py', '.bat', '.sh', '.ps1',
        'activate', 'deploy', 'start', 'install',
        'cleanup', 'find', 'git-', 'test-', 'verify',
        'check', 'configure', 'reconfigure', 'update', 'upgrade',
        'load_test', 'final-verify', 'find-conflicts', 'remove-conflicts',
        'replace', 'send-notification', 'send-live', 'cron-notify',
        'openclaw', 'persona-system', 'memory-distiller', 'system_integrator',
        'vulnerability', 'security_scanner', 'autonomous', 'automated',
        'auto_', 'context_db', 'kg_rag', 'redis', 'federated',
        'energy', 'privacy', 'multi_', 'self_', 'smart',
        'peer', 'social', 'insider', 'brainstorm', 'arxiv_',
        'daily_report', 'dashboard-api', 'innovator-dashboard',
        'innovator-dashboard', 'research_dashboard', 'kg_', 'stock-',
        'login', 'index-with-theme', 'ssh-test', 'python_startup',
        'heartbeat_memory', 'memory_guided', 'memory_integration',
        'memory_kg', 'multi_agent', 'multi_modal', 'self_correcting',
        'self_evolving', 'self_healing', 'smart_rebalancer',
        'social_sentiment', 'insider_trading', 'peer_comparison',
        'persona-collaboration', 'energy_efficient', 'federated_learning',
        'federated_memory', 'privacy_preserving', 'adaptive_context'
    ],
    
    # arXiv 相关
    '40-arxiv': [
        'arxiv_'
    ],
    
    # 安全相关
    '04-plugins/security': [
        'security_', 'SECURITY-', 'vulnerability', 'auth-'
    ],
    
    # Obsidian
    '01-CONFIG/obsidian': [
        'OBSIDIAN-'
    ],
    
    # 测试
    '92-tests-测试': [
        'test-'
    ],
}

def get_category(filename):
    """判断文件分类"""
    filename_upper = filename.upper()
    
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.upper() in filename_upper:
                return category
    return None

def main():
    root = Path(WORKSPACE)
    
    files = [f for f in root.iterdir() if f.is_file()]
    
    stats = {'moved': 0, 'skipped': 0, 'errors': 0}
    
    print(f"扫描到 {len(files)} 个根目录文件\n")
    
    for file_path in files:
        filename = file_path.name
        
        # 跳过
        if filename.startswith('.') or filename in ['.gitignore', 'README.md', 'LICENSE', 'requirements.txt', 'AGENTS.md', 'SOUL.md', 'USER.md', 'TOOLS.md', 'TODO.md', 'HEARTBEAT.md', 'MEMORY.md']:
            print(f"  跳过：{filename}")
            stats['skipped'] += 1
            continue
        
        category = get_category(filename)
        
        if category:
            target_dir = root / category
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / filename
            
            # 重名处理
            counter = 1
            original_target = target_path
            while target_path.exists():
                target_path = target_dir / f"{original_target.stem}_{counter}{original_target.suffix}"
                counter += 1
            
            try:
                shutil.move(str(file_path), str(target_path))
                print(f"  OK: {filename} -> {category}/")
                stats['moved'] += 1
            except Exception as e:
                print(f"  FAIL: {filename} - {e}")
                stats['errors'] += 1
        else:
            print(f"  ?: {filename}")
            stats['skipped'] += 1
    
    print(f"\n完成！移动:{stats['moved']} 跳过:{stats['skipped']} 错误:{stats['errors']}")

if __name__ == '__main__':
    main()
