"""
Generate Workflow Templates

生成默认工作流模板
"""

import yaml
from pathlib import Path

templates_dir = Path("config/workflows")
templates_dir.mkdir(parents=True, exist_ok=True)

# 科技新闻调研模板
tech_research = {
    "id": "tech_research",
    "name": "科技新闻调研",
    "description": "针对科技新闻自动调研相关 GitHub 项目",
    "trigger": {
        "category": "tech",
        "min_importance": 0.7
    },
    "tasks": [
        {
            "name": "搜索 GitHub 项目",
            "description": "根据新闻关键词搜索相关 GitHub 项目",
            "action": "github_search",
            "priority": 10
        },
        {
            "name": "分析项目活跃度",
            "description": "分析项目的 stars、commit 频率、issue 活跃度",
            "action": "analyze_project",
            "priority": 8,
            "depends_on": [0]
        },
        {
            "name": "生成调研报告",
            "description": "生成包含项目对比和分析的调研报告",
            "action": "generate_report",
            "priority": 6,
            "depends_on": [1]
        }
    ]
}

# 市场监控模板
market_monitor = {
    "id": "market_monitor",
    "name": "市场监控",
    "description": "监控市场动态并更新仪表板",
    "trigger": {
        "category": ["finance", "market"],
        "min_importance": 0.6
    },
    "tasks": [
        {
            "name": "提取关键数据",
            "description": "从新闻中提取关键市场数据",
            "action": "extract_data",
            "priority": 10
        },
        {
            "name": "更新监控仪表板",
            "description": "更新市场监控仪表板数据",
            "action": "update_dashboard",
            "priority": 8,
            "depends_on": [0]
        },
        {
            "name": "检查异常波动",
            "description": "检查是否有异常波动并告警",
            "action": "check_anomaly",
            "priority": 7,
            "depends_on": [1]
        }
    ]
}

# 风险预警模板
risk_alert = {
    "id": "risk_alert",
    "name": "风险预警",
    "description": "针对负面新闻生成风险预警",
    "trigger": {
        "sentiment": "negative",
        "min_importance": 0.8
    },
    "tasks": [
        {
            "name": "提取风险因素",
            "description": "从新闻中提取风险因素",
            "action": "extract_risks",
            "priority": 10
        },
        {
            "name": "评估影响范围",
            "description": "评估风险的影响范围和程度",
            "action": "assess_impact",
            "priority": 9,
            "depends_on": [0]
        },
        {
            "name": "生成应对建议",
            "description": "生成风险应对建议",
            "action": "generate_recommendations",
            "priority": 7,
            "depends_on": [1]
        },
        {
            "name": "高优先级推送",
            "description": "将预警信息高优先级推送给相关人员",
            "action": "urgent_push",
            "priority": 10,
            "depends_on": [2]
        }
    ]
}

# 竞品分析模板
competitor_analysis = {
    "id": "competitor_analysis",
    "name": "竞品分析",
    "description": "针对竞品新闻进行分析",
    "trigger": {
        "category": "company",
        "keywords": ["竞品", "竞争对手", "竞争"],
        "min_importance": 0.7
    },
    "tasks": [
        {
            "name": "识别竞品",
            "description": "从新闻中识别竞品信息",
            "action": "identify_competitor",
            "priority": 10
        },
        {
            "name": "收集竞品信息",
            "description": "收集竞品的最新动态和信息",
            "action": "gather_intel",
            "priority": 8,
            "depends_on": [0]
        },
        {
            "name": "对比分析",
            "description": "与我方产品进行对比分析",
            "action": "compare_analysis",
            "priority": 6,
            "depends_on": [1]
        }
    ]
}

# 保存模板
for template in [tech_research, market_monitor, risk_alert, competitor_analysis]:
    template_path = templates_dir / f"{template['id']}.yaml"
    with open(template_path, "w", encoding="utf-8") as f:
        yaml.dump(template, f, allow_unicode=True, default_flow_style=False)
    print(f"✅ Created: {template_path}")

print(f"\n🎉 Generated {4} workflow templates")
