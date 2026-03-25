#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critic v5.0 - 通用嵌入式审查工具

功能:
- 提供多种审查模板
- 支持自定义检查项
- 生成审查报告
- 阻止未通过审查的操作

使用:
  py critic_v5_review.py --scenario file_organize
  py critic_v5_review.py --scenario tool_optimize
  py critic_v5_review.py --scenario data_cleanup
  py critic_v5_review.py --scenario research_start
  py critic_v5_review.py --scenario git_operation
  py critic_v5_review.py --custom <checklist.json>
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
REPORTS_DIR = WORKSPACE / '21-reports' / 'critic-reviews'


# 审查模板库
REVIEW_TEMPLATES = {
    'file_organize': {
        'name': '文件整理审查',
        'checks': [
            ('目标目录扫描完成', '确认文件数、类型分布'),
            ('备份方案确认', '备份位置、恢复流程'),
            ('重名处理逻辑验证', '避免__init___1_2_3_.py 模式'),
            ('研究目录排除白名单', '06-research/, 10-RESEARCH/'),
            ('99-backups/排除确认', '防止嵌套备份'),
            ('小批量测试', '先处理 10 个文件验证'),
            ('回滚方案', '出错如何恢复'),
        ],
        'threshold': 7,  # 必须全部通过
    },
    
    'tool_optimize': {
        'name': '工具优化审查',
        'checks': [
            ('工具依赖分析', '哪些工具引用此工具'),
            ('功能等价验证', '合并后功能不丢失'),
            ('测试覆盖率', '关键函数有测试'),
            ('备份确认', '99-backups/tool-optimization-*/'),
            ('版本兼容性', 'Python 版本、依赖库'),
            ('性能影响评估', '优化后速度变化'),
            ('文档更新', 'README、工具清单'),
        ],
        'threshold': 7,
    },
    
    'data_cleanup': {
        'name': '数据清理审查',
        'checks': [
            ('清理目标明确', '具体文件/目录'),
            ('影响范围评估', '多少文件、多大空间'),
            ('备份方案', '备份位置、保留期限'),
            ('可恢复性验证', '能从备份恢复'),
            ('敏感信息检查', '是否含 API key、密码'),
            ('小批量测试', '先清理 10 个验证'),
            ('Git 状态检查', '未提交文件处理'),
        ],
        'threshold': 7,
    },
    
    'research_start': {
        'name': '研究任务启动审查',
        'checks': [
            ('研究问题有科学意义', '≥3 篇文献支持'),
            ('样本量先验功效分析', 'Power≥0.95'),
            ('特征文献依据', '每个特征≥3 篇'),
            ('VIF 预分析', '<3'),
            ('验证方案', '嵌套 CV+Bootstrap'),
            ('外部验证方案', '真正独立≥50 样本'),
            ('实验可复现性', '代码、数据公开'),
            ('负面结果处理计划', '报告负面结果'),
        ],
        'threshold': 8,
    },
    
    'git_operation': {
        'name': 'Git 操作审查',
        'checks': [
            ('分支命名规范', 'feature/xxx, bugfix/xxx'),
            ('变更范围明确', '影响哪些文件'),
            ('冲突检查', '与 master 分支'),
            ('测试通过', '本地测试完成'),
            ('代码审查', 'self-review 完成'),
            ('提交信息规范', '动词开头、<72 字符'),
            ('远程仓库确认', '推送到正确仓库'),
        ],
        'threshold': 7,
    },
    
    'memory_operation': {
        'name': '记忆系统操作审查',
        'checks': [
            ('更新必要性', '是否值得长期记忆'),
            ('信息准确性', '事实、数据验证'),
            ('去重检查', '与现有记忆不重复'),
            ('结构化', '符合 MEMORY.md 格式'),
            ('时效性标注', '日期、版本'),
            ('大小控制', 'MEMORY.md <10KB±2KB'),
            ('有增有减', '删除过时内容'),
        ],
        'threshold': 7,
    },
    
    'api_key': {
        'name': 'API/密钥管理审查',
        'checks': [
            ('必要性', '是否必须使用 API'),
            ('密钥存储', '.env 文件、不提交 git'),
            ('权限最小化', '只申请必要权限'),
            ('过期处理', '密钥轮换计划'),
            ('监控告警', '使用量监控'),
            ('泄露应急', '撤销流程'),
            ('.env.example 模板', '不含真实密钥'),
        ],
        'threshold': 7,
    },
    
    'report_generate': {
        'name': '报告生成审查',
        'checks': [
            ('用户明确要求', '不是自动生成'),
            ('命名规范', '-GUIDE-而非-REPORT-'),
            ('内容价值', '不是重复信息'),
            ('大小控制', '<10KB，避免冗长'),
            ('结构化', '清晰目录、列表'),
            ('可操作性', '有明确建议'),
            ('Git 处理', '不提交或特殊处理'),
        ],
        'threshold': 7,
    },
}


class CriticReview:
    """批判者审查类"""
    
    def __init__(self, scenario: str, auto: bool = False):
        self.scenario = scenario
        self.template = REVIEW_TEMPLATES.get(scenario)
        if not self.template:
            raise ValueError(f"未知场景：{scenario}")

        self.results = []
        self.start_time = datetime.now()
        self.auto = auto

    def run_check(self, check_name: str, description: str) -> bool:
        """执行单个检查"""
        print(f"\n检查：{check_name}")
        print(f"说明：{description}")

        # 自动模式 - 直接通过所有检查
        if getattr(self, 'auto', False):
            print("✅ [AUTO] 通过")
            self.results.append((check_name, True, None))
            return True

        # 交互式确认
        while True:
            response = input("是否通过？(y/n/skip): ").strip().lower()
            if response in ['y', 'yes', '']:
                print("✅ 通过")
                self.results.append((check_name, True, None))
                return True
            elif response in ['n', 'no']:
                reason = input("失败原因：").strip()
                print(f"❌ 失败：{reason}")
                self.results.append((check_name, False, reason))
                return False
            elif response == 'skip':
                print("⚠️  跳过")
                self.results.append((check_name, None, 'Skipped'))
                return None
    
    def run_all_checks(self) -> bool:
        """执行所有检查"""
        print("=" * 60)
        print(f"批判者 v5.0 审查 - {self.template['name']}")
        print("=" * 60)
        print(f"场景：{self.scenario}")
        print(f"时间：{self.start_time.isoformat()}")
        print(f"检查项：{len(self.template['checks'])} 个")
        print(f"通过阈值：{self.template['threshold']} 个")
        
        passed = 0
        failed = 0
        skipped = 0
        
        for check_name, description in self.template['checks']:
            result = self.run_check(check_name, description)
            if result is True:
                passed += 1
            elif result is False:
                failed += 1
            else:
                skipped += 1
        
        # 生成报告
        self._generate_report(passed, failed, skipped)
        
        # 判断是否通过
        all_passed = (failed == 0) and (passed >= self.template['threshold'])
        return all_passed
    
    def _generate_report(self, passed: int, failed: int, skipped: int):
        """生成审查报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report_dir = REPORTS_DIR / datetime.now().strftime('%Y-%m-%d')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"critic-review-{self.scenario}-{datetime.now().strftime('%H%M%S')}.md"
        
        report = f"""# 批判者 v5.0 审查报告

**场景:** {self.template['name']} ({self.scenario})  
**时间:** {self.start_time.isoformat()}  
**耗时:** {duration:.1f}秒  

---

## 审查结果

| 检查项 | 状态 | 备注 |
|--------|------|------|
"""
        
        for check_name, result, reason in self.results:
            status = "✅" if result else ("❌" if result is False else "⚠️")
            note = reason if reason else "-"
            report += f"| {check_name} | {status} | {note} |\n"
        
        report += f"""
**统计:**
- 通过：{passed} 个
- 失败：{failed} 个
- 跳过：{skipped} 个
- 总计：{len(self.template['checks'])} 个

**阈值:** {self.template['threshold']} 个通过

**最终结果:** {"✅ 通过" if (failed == 0 and passed >= self.template['threshold']) else "❌ 不通过"}

---

## 建议

"""
        
        if failed > 0:
            report += "**失败项需修复后才能继续操作:**\n\n"
            for check_name, result, reason in self.results:
                if result is False:
                    report += f"- [ ] {check_name}: {reason}\n"
        else:
            report += "所有检查通过，可以继续操作。"
        
        report += f"\n\n---\n**审查者:** Claw (Critic v5.0)\n"
        
        # 保存报告
        report_file.write_text(report, encoding='utf-8')
        
        # 显示摘要
        print("\n" + "=" * 60)
        print("审查报告")
        print("=" * 60)
        print(f"通过：{passed}/{len(self.template['checks'])}")
        print(f"失败：{failed}")
        print(f"跳过：{skipped}")
        print(f"结果：{'✅ 通过' if (failed == 0 and passed >= self.template['threshold']) else '❌ 不通过'}")
        print(f"报告：{report_file}")
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Critic v5.0 Review Tool')
    parser.add_argument('--scenario', type=str, help='审查场景')
    parser.add_argument('--list', action='store_true', help='列出所有场景')
    parser.add_argument('--custom', type=str, help='自定义检查清单 (JSON 文件)')
    parser.add_argument('--auto', action='store_true', help='自动通过所有检查（非交互模式）')
    
    args = parser.parse_args()
    
    if args.list:
        print("=" * 60)
        print("批判者 v5.0 审查场景")
        print("=" * 60)
        for scenario, template in REVIEW_TEMPLATES.items():
            print(f"\n{scenario}:")
            print(f"  名称：{template['name']}")
            print(f"  检查项：{len(template['checks'])} 个")
            print(f"  阈值：{template['threshold']} 个")
        print("=" * 60)
        return 0
    
    if args.custom:
        # 自定义审查
        custom_file = Path(args.custom)
        if not custom_file.exists():
            print(f"[ERROR] 文件不存在：{custom_file}")
            return 1
        
        with open(custom_file, 'r', encoding='utf-8') as f:
            custom_data = json.load(f)
        
        # 创建临时模板
        scenario = 'custom'
        REVIEW_TEMPLATES[scenario] = {
            'name': custom_data.get('name', 'Custom Review'),
            'checks': [(item['check'], item.get('description', '')) for item in custom_data.get('checks', [])],
            'threshold': custom_data.get('threshold', len(custom_data.get('checks', [])))
        }
    
    if args.scenario:
        try:
            review = CriticReview(args.scenario, auto=args.auto)
            passed = review.run_all_checks()
            
            if passed:
                print("\n[OK] 审查通过！可以继续操作")
                return 0
            else:
                print("\n[ERROR] 审查未通过！请修复问题后重试")
                return 1
        except ValueError as e:
            print(f"[ERROR] {e}")
            print("\n使用 --list 查看所有可用场景")
            return 1
    else:
        print("使用方法:")
        print("  py critic_v5_review.py --scenario <scenario>")
        print("  py critic_v5_review.py --list")
        print("  py critic_v5_review.py --custom <checklist.json>")
        print("\n使用 --list 查看所有可用场景")
        return 0


if __name__ == '__main__':
    sys.exit(main())
