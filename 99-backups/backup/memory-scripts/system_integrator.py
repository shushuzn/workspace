#!/usr/bin/env python3
"""
系统整合分析器
扫描所有工具，识别重复功能，提出整合建议

Usage:
    python system_integrator.py --scan
    python system_integrator.py --analyze
    python system_integrator.py --recommend
    python system_integrator.py --merge [category]
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class SystemIntegrator:
    """系统整合分析器"""
    
    def __init__(self):
        self.tools_dir = Path("30-scripts-tools")
        self.data_dir = Path("data")
        self.categories = {
            'research': ['arxiv', 'paper', 'research', 'study'],
            'memory': ['memory', 'distill', 'compress', 'lesson'],
            'knowledge_graph': ['kg_', 'knowledge_graph', 'kg-'],
            'persona': ['persona', 'innovator', 'critic', 'planner', 'executor', 'learner', 'coordinator', 'meta_cognition'],
            'workflow': ['workflow', 'workflows'],
            'deployment': ['deploy', 'install'],
            'monitoring': ['monitor', 'health', 'dashboard', 'alert'],
            'git': ['git'],
            'notification': ['feishu', 'notify', 'notification'],
            'cache': ['cache'],
            'config': ['config'],
            'test': ['test'],
            'auto': ['auto_', 'auto-'],
            'optimizer': ['optimizer', 'optimize'],
            'report': ['report', 'brief', 'summary'],
            'tool': ['tool', 'cli'],
        }
    
    def scan_tools(self) -> List[Dict]:
        """扫描所有工具"""
        
        print("\n" + "="*80)
        print("🔍 扫描工具...")
        print("="*80)
        
        tools = []
        
        for py_file in self.tools_dir.glob("*.py"):
            if py_file.name.startswith('__'):
                continue
            
            # 读取文件内容
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析文件
            tool_info = {
                'name': py_file.name,
                'path': str(py_file),
                'size': py_file.stat().st_size,
                'lines': len(content.splitlines()),
                'categories': self.categorize_tool(py_file.name),
                'functions': self.extract_functions(content),
                'classes': self.extract_classes(content),
                'imports': self.extract_imports(content),
                'description': self.extract_description(content),
            }
            
            tools.append(tool_info)
        
        print(f"  扫描完成：{len(tools)} 个工具")
        return tools
    
    def categorize_tool(self, filename: str) -> List[str]:
        """分类工具"""
        
        categories = []
        filename_lower = filename.lower()
        
        for category, keywords in self.categories.items():
            if any(kw in filename_lower for kw in keywords):
                categories.append(category)
        
        return categories if categories else ['other']
    
    def extract_functions(self, content: str) -> List[str]:
        """提取函数名"""
        
        pattern = r'^def\s+(\w+)\s*\('
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches
    
    def extract_classes(self, content: str) -> List[str]:
        """提取类名"""
        
        pattern = r'^class\s+(\w+)'
        matches = re.findall(pattern, content, re.MULTILINE)
        return matches
    
    def extract_imports(self, content: str) -> List[str]:
        """提取导入"""
        
        imports = []
        
        # import xxx
        pattern1 = r'^import\s+(\w+)'
        imports.extend(re.findall(pattern1, content, re.MULTILINE))
        
        # from xxx import
        pattern2 = r'^from\s+(\w+)'
        imports.extend(re.findall(pattern2, content, re.MULTILINE))
        
        return list(set(imports))
    
    def extract_description(self, content: str) -> str:
        """提取文档字符串"""
        
        # 查找模块 docstring
        pattern = r'^"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            desc = match.group(1).strip()
            return desc.split('\n')[0][:100]  # 第一行，最多 100 字符
        
        return ""
    
    def analyze_duplicates(self, tools: List[Dict]) -> Dict:
        """分析重复功能"""
        
        print("\n" + "="*80)
        print("🔍 分析重复功能...")
        print("="*80)
        
        # 按功能分组
        by_function = defaultdict(list)
        
        for tool in tools:
            # 基于文件名和函数名推测功能
            keywords = tool['name'].replace('.py', '').lower().split('_')
            for keyword in keywords:
                if len(keyword) > 3:
                    by_function[keyword].append(tool)
        
        # 识别重复
        duplicates = {}
        for keyword, tool_list in by_function.items():
            if len(tool_list) > 1:
                duplicates[keyword] = tool_list
        
        print(f"  发现 {len(duplicates)} 组可能重复的功能")
        
        return duplicates
    
    def analyze_similar_names(self, tools: List[Dict]) -> List[Tuple]:
        """分析相似命名"""
        
        print("\n" + "="*80)
        print("🔍 分析相似命名...")
        print("="*80)
        
        similar = []
        names = [t['name'] for t in tools]
        
        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                # 简单相似度检查
                base1 = name1.replace('.py', '').replace('_', '').replace('-', '')
                base2 = name2.replace('.py', '').replace('_', '').replace('-', '')
                
                if base1 in base2 or base2 in base1:
                    similar.append((name1, name2))
        
        print(f"  发现 {len(similar)} 对相似命名")
        return similar
    
    def generate_recommendations(self, tools: List[Dict], duplicates: Dict) -> List[Dict]:
        """生成整合建议"""
        
        print("\n" + "="*80)
        print("💡 生成整合建议...")
        print("="*80)
        
        recommendations = []
        
        # 1. 识别高优先级整合机会
        for keyword, tool_list in duplicates.items():
            if len(tool_list) >= 3:
                rec = {
                    'priority': 'HIGH',
                    'type': 'MERGE',
                    'keyword': keyword,
                    'tools': [t['name'] for t in tool_list],
                    'reason': f'{len(tool_list)} 个工具包含 "{keyword}"',
                    'suggested_name': f'{keyword}_manager.py',
                    'estimated_savings': f'{len(tool_list) - 1} 文件',
                }
                recommendations.append(rec)
        
        # 2. 识别配置工具整合
        config_tools = [t for t in tools if 'config' in t['categories']]
        if len(config_tools) > 1:
            rec = {
                'priority': 'HIGH',
                'type': 'MERGE',
                'keyword': 'config',
                'tools': [t['name'] for t in config_tools],
                'reason': f'{len(config_tools)} 个配置工具',
                'suggested_name': 'config_manager_unified.py',
                'estimated_savings': f'{len(config_tools) - 1} 文件',
            }
            recommendations.append(rec)
        
        # 3. 识别部署工具整合
        deploy_tools = [t for t in tools if 'deploy' in t['categories']]
        if len(deploy_tools) > 1:
            rec = {
                'priority': 'MEDIUM',
                'type': 'MERGE',
                'keyword': 'deploy',
                'tools': [t['name'] for t in deploy_tools],
                'reason': f'{len(deploy_tools)} 个部署工具',
                'suggested_name': 'deployment_manager.py',
                'estimated_savings': f'{len(deploy_tools) - 1} 文件',
            }
            recommendations.append(rec)
        
        # 4. 识别监控工具整合
        monitor_tools = [t for t in tools if 'monitor' in t['categories'] or 'dashboard' in t['categories'] or 'health' in t['categories']]
        if len(monitor_tools) > 1:
            rec = {
                'priority': 'MEDIUM',
                'type': 'UNIFY',
                'keyword': 'monitoring',
                'tools': [t['name'] for t in monitor_tools],
                'reason': f'{len(monitor_tools)} 个监控相关工具',
                'suggested_name': 'unified_monitoring_system.py',
                'estimated_savings': f'{len(monitor_tools) - 1} 文件',
            }
            recommendations.append(rec)
        
        # 5. 识别 CLI 工具整合
        cli_tools = [t for t in tools if 'cli' in t['name'] or 'tools' in t['name']]
        if len(cli_tools) > 1:
            rec = {
                'priority': 'LOW',
                'type': 'UNIFY',
                'keyword': 'cli',
                'tools': [t['name'] for t in cli_tools],
                'reason': f'{len(cli_tools)} 个 CLI 工具',
                'suggested_name': 'unified_cli.py',
                'estimated_savings': f'{len(cli_tools) - 1} 文件',
            }
            recommendations.append(rec)
        
        print(f"  生成 {len(recommendations)} 条整合建议")
        
        return recommendations
    
    def print_summary(self, tools: List[Dict], recommendations: List[Dict]):
        """打印总结"""
        
        print("\n" + "="*80)
        print("📊 系统整合分析总结")
        print("="*80)
        
        # 工具统计
        total_size = sum(t['size'] for t in tools)
        total_lines = sum(t['lines'] for t in tools)
        
        print(f"\n  工具总数：{len(tools)}")
        print(f"  总代码量：{total_size / 1024:.1f} KB ({total_lines} 行)")
        print(f"  平均每工具：{total_size / len(tools):.1f} KB")
        
        # 按类别统计
        by_category = defaultdict(list)
        for tool in tools:
            for cat in tool['categories']:
                by_category[cat].append(tool)
        
        print(f"\n  按类别分布:")
        for cat, cat_tools in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"    {cat}: {len(cat_tools)} 工具")
        
        # 整合建议
        high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
        medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
        low_priority = [r for r in recommendations if r['priority'] == 'LOW']
        
        print(f"\n  整合建议:")
        print(f"    高优先级：{len(high_priority)} 项")
        print(f"    中优先级：{len(medium_priority)} 项")
        print(f"    低优先级：{len(low_priority)} 项")
        
        # 预估节省
        total_savings = 0
        for rec in recommendations:
            if 'estimated_savings' in rec:
                # 解析 "X 文件" 格式
                try:
                    savings = int(rec['estimated_savings'].split()[0])
                    total_savings += savings
                except:
                    pass
        
        print(f"\n  预估节省：{total_savings} 文件")
        
        print("\n" + "="*80)
    
    def save_report(self, tools: List[Dict], recommendations: List[Dict]):
        """保存报告"""
        
        self.data_dir.mkdir(exist_ok=True)
        
        report = {
            'timestamp': str(Path.cwd()),
            'total_tools': len(tools),
            'total_size_kb': sum(t['size'] for t in tools) / 1024,
            'total_lines': sum(t['lines'] for t in tools),
            'categories': {},
            'recommendations': recommendations,
        }
        
        # 按类别统计
        by_category = defaultdict(int)
        for tool in tools:
            for cat in tool['categories']:
                by_category[cat] += 1
        
        report['categories'] = dict(by_category)
        
        # 保存
        report_file = self.data_dir / 'system_integration_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n  报告保存到：{report_file}")
    
    def run(self):
        """运行完整分析"""
        
        # 扫描
        tools = self.scan_tools()
        
        # 分析重复
        duplicates = self.analyze_duplicates(tools)
        
        # 分析相似命名
        similar = self.analyze_similar_names(tools)
        
        # 生成建议
        recommendations = self.generate_recommendations(tools, duplicates)
        
        # 打印总结
        self.print_summary(tools, recommendations)
        
        # 保存报告
        self.save_report(tools, recommendations)
        
        # 显示 Top 建议
        self.show_top_recommendations(recommendations)
    
    def show_top_recommendations(self, recommendations: List[Dict]):
        """显示 Top 建议"""
        
        print("\n" + "="*80)
        print("🎯 Top 整合建议")
        print("="*80)
        
        # 按优先级排序
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_recs = sorted(recommendations, key=lambda x: priority_order.get(x['priority'], 3))
        
        for i, rec in enumerate(sorted_recs[:10], 1):
            print(f"\n  {i}. [{rec['priority']}] {rec['type']} - {rec['keyword']}")
            print(f"     工具：{', '.join(rec['tools'][:5])}{'...' if len(rec['tools']) > 5 else ''}")
            print(f"     建议：{rec['suggested_name']}")
            print(f"     理由：{rec['reason']}")
            print(f"     节省：{rec['estimated_savings']}")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='系统整合分析器')
    parser.add_argument('--scan', action='store_true', help='扫描工具')
    parser.add_argument('--analyze', action='store_true', help='完整分析')
    parser.add_argument('--recommend', action='store_true', help='生成建议')
    parser.add_argument('--merge', type=str, help='合并指定类别')
    
    args = parser.parse_args()
    
    integrator = SystemIntegrator()
    
    if args.analyze or args.recommend:
        integrator.run()
    elif args.scan:
        tools = integrator.scan_tools()
        print(f"\n扫描完成：{len(tools)} 个工具")
    elif args.merge:
        print(f"合并类别：{args.merge}")
        # TODO: 实现合并逻辑
    else:
        integrator.run()


if __name__ == "__main__":
    main()
