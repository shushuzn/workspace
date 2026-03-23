#!/usr/bin/env python3
"""
头脑风暴生成器
扫描系统，识别创新机会，生成优先级评分

Usage:
    python brainstorm_generator.py --scan
    python brainstorm_generator.py --generate
    python brainstorm_generator.py --full
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class BrainstormGenerator:
    """头脑风暴生成器"""

    def __init__(self):
        self.workspace = Path(".")
        self.data_dir = Path("data")

    def scan_system(self) -> Dict:
        """扫描系统状态"""

        print("\n" + "="*80)
        print("🔍 扫描系统...")
        print("="*80)

        # 工具统计
        tools_dir = Path("30-scripts-tools")
        tools = list(tools_dir.glob("*.py"))

        # 文档统计
        docs = list(Path(".").glob("*.md"))

        # 数据文件
        data_files = list(self.data_dir.glob("*.json")) if self.data_dir.exists() else []

        # Git 历史
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                capture_output=True,
                text=True,
                timeout=10
            )
            git_history = result.stdout.strip().split('\n')
        except:
            git_history = []

        stats = {
            'tools': len(tools),
            'docs': len(docs),
            'data_files': len(data_files),
            'recent_commits': len(git_history),
            'git_history': git_history[:5],
        }

        print(f"  工具：{stats['tools']} 个")
        print(f"  文档：{stats['docs']} 个")
        print(f"  数据文件：{stats['data_files']} 个")
        print(f"  最近提交：{stats['recent_commits']} 次")

        return stats

    def identify_gaps(self, stats: Dict) -> List[Dict]:
        """识别差距和机会"""

        print("\n" + "="*80)
        print("💡 识别创新机会...")
        print("="*80)

        opportunities = []

        # 1. 工具整合机会
        if stats['tools'] > 100:
            opportunities.append({
                'id': f'BRAIN-{len(opportunities)+1:03d}',
                'category': 'INTEGRATION',
                'title': '大规模工具整合',
                'description': f'{stats["tools"]} 个工具过多，整合到 50 个以内',
                'impact': 85,
                'feasibility': 90,
                'effort': 'MEDIUM',
                'estimated_hours': 20,
                'priority_score': 88,
            })

        # 2. 文档完善机会
        if stats['docs'] < stats['tools'] / 2:
            opportunities.append({
                'id': f'BRAIN-{len(opportunities)+1:03d}',
                'category': 'DOCUMENTATION',
                'title': '文档完善计划',
                'description': '工具/文档比例失衡，每个工具需要对应文档',
                'impact': 70,
                'feasibility': 95,
                'effort': 'LOW',
                'estimated_hours': 10,
                'priority_score': 82,
            })

        # 3. 测试覆盖机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'TESTING',
            'title': '自动化测试增强',
            'description': '为核心工具添加集成测试和端到端测试',
            'impact': 80,
            'feasibility': 85,
            'effort': 'MEDIUM',
            'estimated_hours': 15,
            'priority_score': 83,
        })

        # 4. 性能优化机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'PERFORMANCE',
            'title': '系统性能优化',
            'description': '分析瓶颈，优化关键路径 (启动时间/内存使用/执行速度)',
            'impact': 75,
            'feasibility': 80,
            'effort': 'HIGH',
            'estimated_hours': 25,
            'priority_score': 78,
        })

        # 5. 用户体验机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'UX',
            'title': '统一 CLI 体验优化',
            'description': '改进 openclaw.py，添加交互式菜单/自动补全/智能提示',
            'impact': 85,
            'feasibility': 90,
            'effort': 'MEDIUM',
            'estimated_hours': 12,
            'priority_score': 87,
        })

        # 6. 自动化机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'AUTOMATION',
            'title': 'HEARTBEAT 任务扩展',
            'description': '增加更多自动任务 (自动备份/自动清理/自动报告)',
            'impact': 80,
            'feasibility': 95,
            'effort': 'LOW',
            'estimated_hours': 8,
            'priority_score': 85,
        })

        # 7. 可视化机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'VISUALIZATION',
            'title': '统一监控仪表板',
            'description': '整合所有仪表板到一个统一界面，实时显示所有系统状态',
            'impact': 90,
            'feasibility': 85,
            'effort': 'MEDIUM',
            'estimated_hours': 16,
            'priority_score': 88,
        })

        # 8. AI 增强机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'AI_ENHANCEMENT',
            'title': '本地 LLM 能力扩展',
            'description': '扩展 Ollama 集成，支持更多模型/更复杂任务',
            'impact': 85,
            'feasibility': 80,
            'effort': 'MEDIUM',
            'estimated_hours': 18,
            'priority_score': 83,
        })

        # 9. 知识管理机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'KNOWLEDGE',
            'title': '知识图谱自动构建 2.0',
            'description': '从代码/文档/对话中自动提取知识，实时更新图谱',
            'impact': 88,
            'feasibility': 75,
            'effort': 'HIGH',
            'estimated_hours': 30,
            'priority_score': 84,
        })

        # 10. 协作增强机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'COLLABORATION',
            'title': '7 人格自主协作 2.0',
            'description': '人格系统更智能的自主触发和协作机制',
            'impact': 92,
            'feasibility': 70,
            'effort': 'HIGH',
            'estimated_hours': 35,
            'priority_score': 85,
        })

        # 11. 部署优化机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'DEPLOYMENT',
            'title': '一键部署增强',
            'description': '支持多云部署 (AWS/Azure/GCP)，自动配置 HTTPS/域名',
            'impact': 78,
            'feasibility': 85,
            'effort': 'MEDIUM',
            'estimated_hours': 14,
            'priority_score': 82,
        })

        # 12. 安全增强机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'SECURITY',
            'title': '安全审计自动化',
            'description': '自动扫描秘密/漏洞/配置错误，定期安全报告',
            'impact': 95,
            'feasibility': 90,
            'effort': 'MEDIUM',
            'estimated_hours': 12,
            'priority_score': 92,
        })

        # 13. 数据同步机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'DATA',
            'title': '跨设备数据同步',
            'description': 'Obsidian/Notion/GitHub 多平台自动同步',
            'impact': 82,
            'feasibility': 80,
            'effort': 'MEDIUM',
            'estimated_hours': 20,
            'priority_score': 81,
        })

        # 14. 插件系统机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'EXTENSIBILITY',
            'title': '插件系统架构',
            'description': '支持第三方插件，扩展系统能力',
            'impact': 90,
            'feasibility': 65,
            'effort': 'HIGH',
            'estimated_hours': 40,
            'priority_score': 80,
        })

        # 15. 学习系统机会
        opportunities.append({
            'id': f'BRAIN-{len(opportunities)+1:03d}',
            'category': 'LEARNING',
            'title': '从历史执行学习',
            'description': '分析成功/失败模式，自动优化工作流和决策',
            'impact': 95,
            'feasibility': 60,
            'effort': 'HIGH',
            'estimated_hours': 50,
            'priority_score': 82,
        })

        print(f"  识别 {len(opportunities)} 个创新机会")

        return opportunities

    def calculate_priority(self, opp: Dict) -> int:
        """计算优先级评分"""

        # 简单加权平均
        impact = opp.get('impact', 0)
        feasibility = opp.get('feasibility', 0)
        effort_score = {'LOW': 100, 'MEDIUM': 70, 'HIGH': 40}.get(opp.get('effort', 'MEDIUM'), 70)

        # 权重：影响力 40% + 可行性 35% + 效率 25%
        score = int(impact * 0.4 + feasibility * 0.35 + effort_score * 0.25)

        return score

    def generate_report(self, opportunities: List[Dict]) -> str:
        """生成头脑风暴报告"""

        report = []
        report.append("# 🧠 头脑风暴报告")
        report.append("")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"**创新机会:** {len(opportunities)} 个")
        report.append("")

        # 按优先级排序
        sorted_opps = sorted(opportunities, key=lambda x: x['priority_score'], reverse=True)

        # Top 5
        report.append("## 🎯 Top 5 优先级")
        report.append("")
        for i, opp in enumerate(sorted_opps[:5], 1):
            report.append(f"### {i}. {opp['title']} ({opp['priority_score']}/100)")
            report.append(f"**类别:** {opp['category']}")
            report.append(f"**影响力:** {opp['impact']}/100")
            report.append(f"**可行性:** {opp['feasibility']}/100")
            report.append(f"**工作量:** {opp['effort']} ({opp['estimated_hours']}h)")
            report.append(f"**描述:** {opp['description']}")
            report.append("")

        # 按类别分组
        report.append("## 📊 按类别分布")
        report.append("")

        by_category = {}
        for opp in opportunities:
            cat = opp['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(opp)

        for cat, cat_opps in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            avg_score = sum(o['priority_score'] for o in cat_opps) / len(cat_opps)
            report.append(f"- **{cat}:** {len(cat_opps)} 机会 (平均 {avg_score:.0f}分)")

        report.append("")

        # 完整列表
        report.append("## 📋 完整机会列表")
        report.append("")
        report.append("| ID | 类别 | 标题 | 优先级 | 影响力 | 可行性 | 工作量 |")
        report.append("|-----|------|------|--------|--------|--------|--------|")

        for opp in sorted_opps:
            report.append(f"| {opp['id']} | {opp['category']} | {opp['title'][:20]}... | {opp['priority_score']} | {opp['impact']} | {opp['feasibility']} | {opp['effort']} |")

        report.append("")

        # 下一步建议
        report.append("## 🚀 下一步建议")
        report.append("")
        report.append("**立即执行 (本周):**")
        for opp in sorted_opps[:3]:
            report.append(f"- [ ] {opp['title']} ({opp['estimated_hours']}h)")

        report.append("")
        report.append("**短期计划 (本月):**")
        for opp in sorted_opps[3:8]:
            report.append(f"- [ ] {opp['title']} ({opp['estimated_hours']}h)")

        report.append("")
        report.append("**长期规划 (下季度):**")
        for opp in sorted_opps[8:]:
            if opp['effort'] == 'HIGH':
                report.append(f"- [ ] {opp['title']} ({opp['estimated_hours']}h)")

        return "\n".join(report)

    def run(self):
        """运行完整头脑风暴"""

        # 扫描
        stats = self.scan_system()

        # 识别机会
        opportunities = self.identify_gaps(stats)

        # 生成报告
        report = self.generate_report(opportunities)

        # 保存报告
        report_file = self.data_dir / "brainstorm_report.md"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n  报告保存到：{report_file}")

        # 打印摘要
        print("\n" + "="*80)
        print("🎯 Top 5 创新机会")
        print("="*80)

        sorted_opps = sorted(opportunities, key=lambda x: x['priority_score'], reverse=True)

        for i, opp in enumerate(sorted_opps[:5], 1):
            print(f"\n{i}. **{opp['title']}** ({opp['priority_score']}/100)")
            print(f"   类别：{opp['category']}")
            print(f"   描述：{opp['description']}")
            print(f"   工作量：{opp['estimated_hours']}小时")

        print("\n" + "="*80)

        return opportunities


def main():
    import argparse

    parser = argparse.ArgumentParser(description='头脑风暴生成器')
    parser.add_argument('--scan', action='store_true', help='扫描系统')
    parser.add_argument('--generate', action='store_true', help='生成报告')
    parser.add_argument('--full', action='store_true', help='完整流程')

    args = parser.parse_args()

    generator = BrainstormGenerator()

    if args.full or args.generate:
        generator.run()
    elif args.scan:
        generator.scan_system()
    else:
        generator.run()


if __name__ == "__main__":
    main()
