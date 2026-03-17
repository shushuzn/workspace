#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product Manager Agent v3.0 - Main Entry Point
产品管理 Agent - 独立运行

功能:
- 产品价值评估（核心）
- 整洁度维护（基础）
- 数据分析（支撑）
- 报告生成

Author: Claw 🐾
Version: 3.0
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class ProductManagerAgent:
    """Product Manager Agent - 独立运行"""
    
    def __init__(self, config_path: str = None):
        self.workspace = Path(__file__).parent.parent  # D:\OpenClaw\workspace
        self.agent_root = Path(__file__).parent  # agent-pm 文件夹
        self.config_path = config_path or self.agent_root / "config" / "config.json"
        self.config = self.load_config()
        self.state = self.load_state()
        
        print("=" * 60)
        print(f"[PM Agent v3.0] 产品管理 Agent")
        print("=" * 60)
        print(f"工作区：{self.workspace}")
        print(f"配置：{self.config_path}")
        print("=" * 60)
    
    def load_config(self) -> Dict:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_state(self) -> Dict:
        """加载状态"""
        state_file = self.agent_root / "data" / "pm-state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_run": None,
            "total_runs": 0,
            "reports_generated": 0
        }
    
    def save_state(self):
        """保存状态"""
        state_file = self.agent_root / "data" / "pm-state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def run_full_analysis(self):
        """运行完整分析"""
        print("\n🔍 开始完整分析...\n")
        
        # 1. 产品价值分析
        print("📊 [1/3] 产品价值分析...")
        product_report = self.analyze_product_value()
        
        # 2. 整洁度检查
        print("\n🧹 [2/3] 整洁度检查...")
        cleanliness_report = self.check_cleanliness()
        
        # 3. 生成综合报告
        print("\n📝 [3/3] 生成综合报告...")
        self.generate_combined_report(product_report, cleanliness_report)
        
        # 更新状态
        self.state["last_run"] = datetime.now().isoformat()
        self.state["total_runs"] += 1
        self.save_state()
        
        print("\n" + "=" * 60)
        print("✅ 分析完成！")
        print(f"报告位置：{self.agent_root / 'reports'}")
        print("=" * 60)
    
    def analyze_product_value(self) -> Dict:
        """产品价值分析"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "tools_analyzed": 0,
            "high_value": [],
            "medium_value": [],
            "low_value": [],
            "recommendations": []
        }
        
        # 扫描 Python 工具
        tools = list(self.workspace.glob("*.py"))
        tools.extend(self.workspace.glob("**/*.py"))
        tools = list(set(tools))  # 去重
        
        report["tools_analyzed"] = len(tools)
        
        # 简单分析（后续扩展）
        for tool in tools[:10]:  # 先分析前 10 个
            value_score = self.estimate_tool_value(tool)
            if value_score >= 0.7:
                report["high_value"].append(str(tool))
            elif value_score >= 0.4:
                report["medium_value"].append(str(tool))
            else:
                report["low_value"].append(str(tool))
        
        # 生成建议
        if len(report["low_value"]) > 5:
            report["recommendations"].append({
                "type": "REVIEW",
                "message": f"发现 {len(report['low_value'])} 个低价值工具，建议审查",
                "priority": "P1"
            })
        
        # 保存报告
        self.save_report("product-analysis", "product-analysis-" + datetime.now().strftime("%Y-%m-%d") + ".md", report)
        
        return report
    
    def estimate_tool_value(self, tool_path: Path) -> float:
        """估算工具价值（简化版）"""
        score = 0.5  # 基础分
        
        # 最近修改过 +0.2
        try:
            mtime = tool_path.stat().st_mtime
            days_old = (datetime.now().timestamp() - mtime) / 86400
            if days_old < 30:
                score += 0.2
        except:
            pass
        
        # 被其他文件导入 +0.2
        # (简化：检查文件名是否在其他文件中出现)
        
        # 文件大小适中 +0.1
        try:
            size = tool_path.stat().st_size
            if 1000 < size < 100000:  # 1KB-100KB
                score += 0.1
        except:
            pass
        
        return min(1.0, score)
    
    def check_cleanliness(self) -> Dict:
        """整洁度检查"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "scores": {
                "structure": 0,
                "naming": 0,
                "organization": 0,
                "hygiene": 0,
                "overall": 0
            },
            "issues": {
                "too_many_folders": False,
                "duplicate_folders": [],
                "mixed_naming": [],
                "scattered_files": []
            },
            "recommendations": []
        }
        
        # 统计文件夹
        folders = [d for d in self.workspace.iterdir() if d.is_dir()]
        folder_count = len(folders)
        
        report["scores"]["structure"] = max(0, 100 - (folder_count - 50) * 2) if folder_count > 50 else 100
        
        # 检查问题
        if folder_count > 50:
            report["issues"]["too_many_folders"] = True
            report["recommendations"].append({
                "type": "MERGE",
                "message": f"文件夹过多 ({folder_count}个)，建议合并重复文件夹",
                "priority": "P0"
            })
        
        # 检查重复文件夹（简单版）
        folder_names = [f.name for f in folders]
        for i, name1 in enumerate(folder_names):
            for name2 in folder_names[i+1:]:
                if name1.lower() == name2.lower() or name1 in name2 or name2 in name1:
                    report["issues"]["duplicate_folders"].append((name1, name2))
        
        # 计算总分
        report["scores"]["overall"] = report["scores"]["structure"]
        
        # 保存报告
        self.save_report("cleanliness-reports", "cleanliness-" + datetime.now().strftime("%Y-%m-%d") + ".md", report)
        
        return report
    
    def save_report(self, report_type: str, filename: str, data: Dict):
        """保存报告"""
        reports_dir = self.agent_root / "reports" / report_type
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / filename
        
        # 生成 Markdown 报告
        md_content = self.generate_markdown_report(data, report_type)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✓ 报告已保存：{report_path}")
        self.state["reports_generated"] += 1
    
    def generate_markdown_report(self, data: Dict, report_type: str) -> str:
        """生成 Markdown 报告"""
        if report_type == "product-analysis":
            return f"""# 产品价值分析报告

**生成时间:** {data['timestamp']}
**分析工具数:** {data['tools_analyzed']}

---

## 价值分类

### 高价值工具 ({len(data['high_value'])}个)
{chr(10).join('- ' + t for t in data['high_value'][:10])}

### 中价值工具 ({len(data['medium_value'])}个)
{chr(10).join('- ' + t for t in data['medium_value'][:10])}

### 低价值工具 ({len(data['low_value'])}个)
{chr(10).join('- ' + t for t in data['low_value'][:10])}

---

## 建议

{chr(10).join(f"- [{r['priority']}] {r['message']}" for r in data['recommendations'])}

---

**PM Agent v3.0** | 产品价值第一
"""
        
        elif report_type == "cleanliness-reports":
            return f"""# 整洁度检查报告

**生成时间:** {data['timestamp']}

---

## 评分

| 维度 | 得分 |
|------|------|
| 结构 | {data['scores']['structure']}/100 |
| 命名 | {data['scores']['naming']}/100 |
| 组织 | {data['scores']['organization']}/100 |
| 卫生 | {data['scores']['hygiene']}/100 |
| **总分** | **{data['scores']['overall']}/100** |

---

## 发现的问题

- 文件夹过多：{data['issues']['too_many_folders']}
- 重复文件夹：{len(data['issues']['duplicate_folders'])} 对

---

## 建议

{chr(10).join(f"- [{r['priority']}] {r['message']}" for r in data['recommendations'])}

---

**PM Agent v3.0** | 整洁度基础
"""
        
        return "# Report\n\nNo content."
    
    def generate_combined_report(self, product: Dict, cleanliness: Dict):
        """生成综合报告"""
        combined = {
            "timestamp": datetime.now().isoformat(),
            "product_analysis": product,
            "cleanliness_check": cleanliness
        }
        
        md_content = f"""# PM Agent 综合报告

**生成时间:** {combined['timestamp']}

---

## 📊 产品价值分析

- 分析工具数：{product['tools_analyzed']}
- 高价值：{len(product['high_value'])}
- 中价值：{len(product['medium_value'])}
- 低价值：{len(product['low_value'])}

---

## 🧹 整洁度检查

- 总分：{cleanliness['scores']['overall']}/100
- 文件夹过多：{cleanliness['issues']['too_many_folders']}
- 重复文件夹：{len(cleanliness['issues']['duplicate_folders'])} 对

---

## 🎯 优先行动

### P0 - 立即执行
1. 合并重复文件夹
2. 审查低价值工具

### P1 - 本周执行
1. 统一命名规范
2. 整理散落文件

---

**PM Agent v3.0** | 产品价值第一 | 整洁度基础
"""
        
        reports_dir = self.agent_root / "reports" / "roadmaps"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"combined-{datetime.now().strftime('%Y-%m-%d')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✓ 综合报告已保存：{report_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PM Agent v3.0 - 产品管理 Agent")
    parser.add_argument("--run", action="store_true", help="运行完整分析")
    parser.add_argument("--analyze-product", action="store_true", help="仅产品价值分析")
    parser.add_argument("--check-cleanliness", action="store_true", help="仅整洁度检查")
    parser.add_argument("--auto-clean", action="store_true", help="自动整理（需确认）")
    
    args = parser.parse_args()
    
    agent = ProductManagerAgent()
    
    if args.run:
        agent.run_full_analysis()
    elif args.analyze_product:
        agent.analyze_product_value()
    elif args.check_cleanliness:
        agent.check_cleanliness()
    elif args.auto_clean:
        print("⚠️  自动整理功能开发中...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
