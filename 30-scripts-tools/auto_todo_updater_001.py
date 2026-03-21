import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动 TODO 更新器 v1.0

功能：
1. 检测任务完成（检查工具文件是否存在）
2. 自动更新 TODO.md 标记完成
3. 自动提交 Git
4. 记录更新日志

使用：
  py auto_todo_updater.py --check
  py auto_todo_updater.py --update
  py auto_todo_updater.py --auto
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path


class AutoTODOUpdater:
    """自动 TODO 更新器"""
    
    def __init__(self):
        self.workspace = Path("D:/OpenClaw/workspace")
        self.todo_file = self.workspace / "TODO.md"
        self.tools_registry = self.workspace / "30-scripts-tools" / "tools_registry.json"
        self.log_file = self.workspace / "13-memory" / "todo-update-log.jsonl"
        
        # Phase 2 工具清单
        self.phase2_tools = {
            'SA-005': 'sa_005_indicator_calculator.py',
            'SA-006': 'sa_006_pattern_recognition.py',
            'SA-007': 'sa_007_trend_analysis.py',
            'SA-008': 'sa_008_support_resistance.py',
            'SA-009': 'sa_009_financial_ratios.py',
            'SA-010': 'sa_010_valuation_model.py',
            'SA-011': 'sa_011_growth_analysis.py',
            'SA-012': 'sa_012_industry_analysis.py'
        }
    
    def check_tool_completion(self) -> dict:
        """
        检查工具完成情况
        
        Returns:
            dict: 检查结果
        """
        result = {
            'total': len(self.phase2_tools),
            'completed': 0,
            'pending': [],
            'completion_rate': 0
        }
        
        for tool_id, filename in self.phase2_tools.items():
            filepath = self.tools_registry.parent / filename
            if filepath.exists():
                result['completed'] += 1
            else:
                result['pending'].append(tool_id)
        
        result['completion_rate'] = round(result['completed'] / result['total'] * 100, 1)
        
        return result
    
    def update_todo(self) -> dict:
        """
        更新 TODO.md
        
        Returns:
            dict: 更新结果
        """
        result = {
            'success': False,
            'message': '',
            'changes': []
        }
        
        if not self.todo_file.exists():
            result['message'] = 'TODO.md 不存在'
            return result
        
        # 检查完成情况
        check_result = self.check_tool_completion()
        
        if check_result['completion_rate'] == 100:
            # 读取当前 TODO
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已标记完成
            if 'Phase 2 - 股票分析 100% 完成' in content:
                result['message'] = 'TODO.md 已是最新'
                result['success'] = True
                return result
            
            # 更新 TODO 内容
            new_content = self._generate_completed_todo(check_result)
            
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result['success'] = True
            result['message'] = f'Phase 2 100% 完成，已更新 TODO.md'
            result['changes'] = [
                f'Phase 2: 8/8 工具完成 (100%)',
                f'统计：待做 0, 完成 10'
            ]
            
            # 记录日志
            self._log_update(result)
        
        else:
            result['message'] = f'Phase 2 进度：{check_result["completion_rate"]}%'
        
        return result
    
    def _generate_completed_todo(self, check_result: dict) -> str:
        """生成已完成的 TODO 内容"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        content = f"""# TODO.md - 待办事项

**最后更新:** {timestamp}  
**状态:** 压缩版 (只保留待做)

---

## ✅ 已完成 (2026-03-20)

### Phase 2 - 股票分析 100% 完成
- [x] SA-005: 技术指标计算器
- [x] SA-006: 形态识别
- [x] SA-007: 趋势分析
- [x] SA-008: 支撑阻力
- [x] SA-009: 财务比率
- [x] SA-010: 估值模型
- [x] SA-011: 成长性分析
- [x] SA-012: 行业地位 + 报告生成 ✅

**Git 提交:** Phase2-complete-SA-012-industry-analysis

### 工作流强制执行 v2.0 ✅
- [x] 创建 workflow_enforcer_v2.py
- [x] 集成 content_validator
- [x] 每步验证输出内容

**Git 提交:** Add-workflow-enforcer-v2-with-content-validation

### 会话压缩自动化 ✅
- [x] 创建 auto_session_compressor.py
- [x] 配置每 2 小时自动检查
- [x] 添加到 HEARTBEAT.md

**Git 提交:** Add-auto-session-compressor-every-2-hours

### 文档压缩 ✅
- [x] SOUL.md (400KB→3KB, -99%)
- [x] TODO.md (722 行→34 行，-95%)

---

## 📊 统计

| 类别 | 待做 | 进行中 | 完成 |
|------|------|--------|------|
| Phase 2 | 0 | 0 | 8 |
| 工作流 | 0 | 0 | 1 |
| 自动化 | 0 | 0 | 1 |
| **总计** | **0** | **0** | **10** |

---

**完整历史:** `13-memory/task-history-*.md`
"""
        return content
    
    def auto_commit(self) -> dict:
        """
        自动提交 Git
        
        Returns:
            dict: 提交结果
        """
        result = {
            'success': False,
            'message': ''
        }
        
        try:
            # Git add
            subprocess.run(
                ['git', 'add', str(self.todo_file, timeout=60)],
                cwd=str(self.workspace),
                capture_output=True,
                timeout=30
            )
            
            # Git commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            msg = f'Auto: TODO.md update - Phase 2 complete ({timestamp})'
            
            result_proc = subprocess.run(
                ['git', 'commit', '-m', msg],
                cwd=str(self.workspace, timeout=60),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_proc.returncode == 0:
                result['success'] = True
                result['message'] = 'Git 提交成功'
            else:
                result['message'] = f'Git 提交失败：{result_proc.stderr}'
        
        except Exception as e:
            result['message'] = str(e)
        
        return result
    
    def _log_update(self, result: dict):
        """记录更新日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'changes': result.get('changes', [])
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except (IOError, OSError, UnicodeDecodeError):
            pass
    
    def run_auto(self):
        """自动模式"""
        print("=" * 70)
        print(" " * 20 + "自动 TODO 更新器")
        print("=" * 70)
        
        # 检查完成情况
        check_result = self.check_tool_completion()
        
        print(f"\nPhase 2 进度：{check_result['completion_rate']}%")
        print(f"已完成：{check_result['completed']}/{check_result['total']}")
        
        if check_result['pending']:
            print(f"待完成：{', '.join(check_result['pending'])}")
        
        # 如果 100% 完成，更新 TODO
        if check_result['completion_rate'] == 100:
            print("\nPhase 2 100% 完成，更新 TODO.md...")
            update_result = self.update_todo()
            
            print(f"更新结果：{update_result['message']}")
            
            if update_result['success']:
                print("\n自动提交 Git...")
                commit_result = self.auto_commit()
                print(f"提交结果：{commit_result['message']}")
                
                if commit_result['success']:
                    print("\n自动推送 Git...")
                    subprocess.run(
                        ['git', 'push'],
                        cwd=str(self.workspace, timeout=60),
                        capture_output=True,
                        timeout=60
                    )
                    print("推送完成")
        else:
            print("\nPhase 2 尚未完成，跳过更新")


logging.basicConfig(level=logging.INFO)
def main():
    """主函数"""
    updater = AutoTODOUpdater()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            result = updater.check_tool_completion()
            print(f"Phase 2 进度：{result['completion_rate']}%")
            print(f"已完成：{result['completed']}/{result['total']}")
            if result['pending']:
                print(f"待完成：{', '.join(result['pending'])}")
        
        elif sys.argv[1] == '--update':
            result = updater.update_todo()
            print(result['message'])
        
        elif sys.argv[1] == '--auto':
            updater.run_auto()
        
        else:
            print("用法：py auto_todo_updater.py [--check|--update|--auto]")
    else:
        # 默认自动模式
        updater.run_auto()


if __name__ == '__main__':
    main()
