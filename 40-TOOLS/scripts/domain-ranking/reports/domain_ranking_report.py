#!/usr/bin/env python3
"""
学科学术段位可视化报告生成器
生成 HTML 雷达图 + 晋升建议
"""
import json
from pathlib import Path
from datetime import datetime

def find_latest_collected_data(domain: str) -> Path:
    """查找最新的领域收集数据文件"""
    workspace = Path(__file__).parent.parent
    reports_dir = workspace / "21-reports"
    
    if not reports_dir.exists():
        return None
    
    pattern = f"{domain}-domain-data-*.json"
    files = list(reports_dir.glob(pattern))
    
    if not files:
        return None
    
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0]


def generate_html_report(domain: str, data_file: Path, output_path: Path):
    """生成 HTML 可视化报告"""
    
    with open(data_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    # 提取 11 维度数据
    dimensions = {
        '理论基础': data.get('theory', {}).get('xp', 0),
        '技术成熟度': data.get('technology', {}).get('xp', 0),
        '学术影响力': data.get('impact', {}).get('xp', 0),
        '应用广度': data.get('application', {}).get('xp', 0),
        '人才储备': data.get('talent', {}).get('xp', 0),
        '资金投入': data.get('funding', {}).get('xp', 0),
        '创新能力': data.get('innovation', {}).get('xp', 0),
        '国际合作': data.get('collaboration', {}).get('xp', 0),
        '教育普及': data.get('education', {}).get('xp', 0),
        '开源贡献': data.get('open_source', {}).get('xp', 0),
        '产业转化': data.get('industry', {}).get('xp', 0),
    }
    
    # 计算总分和段位
    weights = {
        '理论基础': 0.15, '技术成熟度': 0.15, '学术影响力': 0.12,
        '应用广度': 0.10, '人才储备': 0.08, '资金投入': 0.05,
        '创新能力': 0.10, '国际合作': 0.08, '教育普及': 0.08,
        '开源贡献': 0.07, '产业转化': 0.07
    }
    
    total_xp = sum(dimensions.values())
    weighted_score = sum(dimensions[dim] * weights[dim] for dim in dimensions)
    score = int(weighted_score / 100)  # 0-8000
    level = min(1000, max(1, score))
    
    # 段位
    ranks = [
        ("黑铁", 0, "#2C2C2C"), ("青铜", 1000, "#CD7F32"),
        ("白银", 2000, "#C0C0C0"), ("黄金", 3000, "#FFD700"),
        ("铂金", 4000, "#E5E4E2"), ("钻石", 5000, "#B9F2FF"),
        ("大师", 6000, "#9B59B6"), ("宗师", 7000, "#FFD700")
    ]
    
    current_rank = "黑铁"
    rank_color = "#2C2C2C"
    for name, threshold, color in reversed(ranks):
        if score >= threshold:
            current_rank = name
            rank_color = color
            break
    
    # 生成雷达图数据
    labels = list(dimensions.keys())
    values = list(dimensions.values())
    max_val = 10000
    
    # 颜色映射 (根据 XP 值)
    def get_color(value):
        if value < 500:
            return "#EF4444"  # 红 - 亟需改进
        elif value < 700:
            return "#F59E0B"  # 橙 - 需要提升
        elif value < 800:
            return "#10B981"  # 绿 - 稳步发展
        else:
            return "#3B82F6"  # 蓝 - 领域领先
    
    colors = [get_color(v) for v in values]
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{domain} 学科学术段位报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
        .header h1 {{ color: #333; font-size: 28px; margin-bottom: 10px; }}
        .header .meta {{ color: #666; font-size: 14px; }}
        .rank-badge {{ 
            display: inline-block;
            background: {rank_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 18px;
            margin-top: 10px;
        }}
        .main-grid {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
            margin-bottom: 20px;
        }}
        .panel {{ 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
        .panel-title {{ 
            font-size: 18px; 
            color: #333; 
            margin-bottom: 15px; 
            font-weight: 600;
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 10px; 
        }}
        .stat-card {{ 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
        }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
        .recommendations {{ margin-top: 20px; }}
        .rec-item {{ 
            padding: 12px; 
            margin-bottom: 8px; 
            border-radius: 6px; 
            border-left: 4px solid;
            font-size: 14px;
        }}
        .rec-critical {{ background: #FEE2E2; border-color: #EF4444; }}
        .rec-urgent {{ background: #FEF3C7; border-color: #F59E0B; }}
        .rec-focus {{ background: #D1FAE5; border-color: #10B981; }}
        .rec-ok {{ background: #DBEAFE; border-color: #3B82F6; }}
        .chart-container {{ position: relative; height: 400px; }}
        @media (max-width: 768px) {{
            .main-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 {domain} 学科学术段位报告</h1>
            <div class="meta">
                生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                数据源：{data_file.name}
            </div>
            <div class="rank-badge">
                {current_rank} {level}级 | 总分：{score}/8000 | 进度：{level/10:.1f}%
            </div>
        </div>
        
        <div class="main-grid">
            <div class="panel">
                <div class="panel-title">📊 11 维度能力雷达图</div>
                <div class="chart-container">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-title">📈 核心指标</div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{total_xp:,}</div>
                        <div class="stat-label">总 XP</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{score}</div>
                        <div class="stat-label">段位分数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{level}</div>
                        <div class="stat-label">当前等级</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{1000 - level}</div>
                        <div class="stat-label">距下段</div>
                    </div>
                </div>
                
                <div class="recommendations">
                    <div class="panel-title" style="margin-top: 20px;">🎯 晋升建议</div>
                    {generate_recommendations_html(dimensions)}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(labels, ensure_ascii=False)},
                datasets: [{{
                    label: '{domain}',
                    data: {values},
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    pointBackgroundColor: {json.dumps(colors)},
                    pointRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        min: 0,
                        max: {max_val},
                        ticks: {{ stepSize: 2000 }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': ' + context.parsed.r + ' XP';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def generate_recommendations_html(dimensions: dict) -> str:
    """生成建议 HTML"""
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1])
    
    html_parts = []
    for dim, xp in sorted_dims[:6]:  # 最弱的 6 个维度
        if xp < 500:
            css_class = "rec-critical"
            label = "🔴 CRITICAL"
        elif xp < 700:
            css_class = "rec-urgent"
            label = "🟡 URGENT"
        elif xp < 800:
            css_class = "rec-focus"
            label = "🟢 FOCUS"
        else:
            css_class = "rec-ok"
            label = "🔵 OK"
        
        html_parts.append(f'''
            <div class="rec-item {css_class}">
                <strong>{label}</strong> {dim}: {xp:.0f}/10000 XP
            </div>
        ''')
    
    return ''.join(html_parts)


if __name__ == "__main__":
    import sys
    
    # Windows UTF-8 兼容
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    domain = sys.argv[1] if len(sys.argv) > 1 else "LIG"
    data_file = find_latest_collected_data(domain)
    
    if not data_file:
        print(f"[ERROR] 未找到 {domain} 的收集数据")
        sys.exit(1)
    
    output_dir = Path(__file__).parent.parent / "21-reports"
    output_path = output_dir / f"{domain}-domain-ranking-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    
    generate_html_report(domain, data_file, output_path)
    print(f"[OK] 报告已生成：{output_path}")
