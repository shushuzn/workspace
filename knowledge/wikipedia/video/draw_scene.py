"""
从视频脚本提取 [画面：] 场景描述，生成对应配图
依赖: pip install matplotlib pillow numpy
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import argparse
import re
from pathlib import Path

plt.style.use('default')
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

COLORS = {
    'bg': '#ffffff', 'blue': '#1e40af', 'pink': '#9d174d',
    'green': '#166534', 'yellow': '#92400e', 'red': '#991b1b',
    'orange': '#9a3412', 'text': '#111827', 'muted': '#374151', 'grid': '#d1d5db',
}

def new_fig(figsize=(12, 8)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.axis('off')
    return fig, ax

def parse_script_header(script_path):
    """从脚本提取标题和简介"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 标题：从 # 视频文案：xxx 取 xxx
    title = None
    m = re.search(r'#\s*视频文案[：:]\s*(.+)', content)
    if m:
        title = m.group(1).strip()

    # 简介：开场 [画面：xxx] 之后、第一个 --- 之前的纯文本（取前80字）
    summary = None
    m = re.search(r'##\s*开场[（(][^）)]*[/）)].*?\n+(.+?)(?=---|\Z)', content, re.DOTALL)
    if m:
        # 去掉 [画面：xxx] 标注行，取剩余文本
        lines = m.group(1).split('\n')
        text_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('[画面：')]
        summary = ''.join(text_lines)[:120].strip()

    return title, summary

def draw_cover(out_path, title):
    """封面图：仅大标题，居中铺满画布"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    # 主标题居中
    if len(title) > 20:
        ax.text(6, 4, title, ha='center', va='center', fontsize=24,
                fontweight='bold', color=COLORS['text'], linespacing=1.6)
    else:
        ax.text(6, 4, title, ha='center', va='center', fontsize=30,
                fontweight='bold', color=COLORS['text'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

# ─── 配图绘制函数 ─────────────────────────────────────────

def draw_braid_group(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.text(5, 6.5, '辫群 B₃ 的编织方式', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(5, 6.1, '非阿贝尔结构：σ₁σ₂ ≠ σ₂σ₁', ha='center', fontsize=10, color=COLORS['muted'])
    top_plate = FancyBboxPatch((1, 5.2), 8, 0.15, boxstyle="round,pad=0.02", facecolor='#e5e7eb', edgecolor='#6b7280')
    ax.add_patch(top_plate)
    for i, (x, color) in enumerate(zip([2.5, 5, 7.5], ['#1e40af', '#9d174d', '#166534'])):
        circle = plt.Circle((x, 5.5), 0.18, facecolor=color)
        ax.add_patch(circle)
        ax.text(x, 5.8, f'#{i+1}', ha='center', fontsize=9, color='#374151', fontweight='bold')
    t = np.linspace(0, 1, 300)
    bx1 = 2.5 + 1.5 * np.sin(np.pi * t); by1 = 5.3 - 4.1 * t
    ax.plot(bx1, by1, color='#1e40af', linewidth=4, zorder=3)
    bx2 = 5 - 1.5 * np.sin(np.pi * t); by2 = 5.3 - 4.1 * t
    ax.plot(bx2, by2, color='#9d174d', linewidth=4, zorder=3)
    bx3 = np.full_like(t, 7.5); by3 = 5.3 - 4.1 * t
    ax.plot(bx3, by3, color='#166534', linewidth=4, zorder=3)
    bottom_plate = FancyBboxPatch((1, 1.0), 8, 0.15, boxstyle="round,pad=0.02", facecolor='#e5e7eb', edgecolor='#6b7280')
    ax.add_patch(bottom_plate)
    for i, (x, color) in enumerate(zip([2.5, 5, 7.5], ['#1e40af', '#9d174d', '#166534'])):
        circle = plt.Circle((x, 1.3), 0.18, facecolor=color)
        ax.add_patch(circle)
    sigma_style = dict(boxstyle='round,pad=0.3', facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2)
    ax.text(3.5, 3.6, 'σ₁', fontsize=16, fontweight='bold', color='#1e40af', ha='center', bbox=sigma_style)
    ax.text(6.0, 2.8, 'σ₂', fontsize=16, fontweight='bold', color='#9d174d', ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fce7f3', edgecolor='#9d174d', linewidth=2))
    rule_box = FancyBboxPatch((0.5, 0.1), 9, 0.7, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#9ca3af', linewidth=1.5)
    ax.add_patch(rule_box)
    ax.text(5, 0.45, '规则一：局部性（隔着≥1根可换位）  |  规则二：Yang-Baxter方程 σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁', ha='center', fontsize=10, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_iam_model(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'IAM 云身份与访问管理模型', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.25, '身份 · 权限 · 资源', ha='center', fontsize=10, color=COLORS['muted'])
    boxes = [
        (0.5, 1.2, 3.3, 4.5, '#dbeafe', '#1e40af', '身份 Identity', ['你是谁？', '', 'User (root/普通)', 'Group (运维/审计...)', 'Role (临时权限)']),
        (4.35, 1.2, 3.3, 4.5, '#fce7f3', '#9d174d', '权限 Permission', ['你能做什么？', '', 'Policy 文档定义', 'Allow / Deny', '对哪个资源+操作']),
        (8.2, 1.2, 3.3, 4.5, '#dcfce7', '#166534', '资源 Resource', ['哪些需要保护？', '', 'S3 存储桶', 'EC2 服务器', 'Lambda 函数'])
    ]
    for (x, y, w, h, fc, ec, title, lines) in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', fontsize=13, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 1.0 - i*0.65, line, ha='center', fontsize=11, color=COLORS['text'])
    for x in [3.8, 7.65]:
        ax.annotate('', xy=(x+0.05, 3.5), xytext=(x-0.35, 3.5), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    principle_box = FancyBboxPatch((0.5, 0.1), 11, 0.8, boxstyle="round,pad=0.1", facecolor='#1a2e3d', edgecolor='#60a5fa', linewidth=1.5)
    ax.add_patch(principle_box)
    ax.text(6, 0.5, '核心原则：默认禁止，只显式授予  |  没有明确授权 = 禁止访问', ha='center', fontsize=11, fontweight='bold', color='#60a5fa')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_attack_path(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'IAM 特权升级攻击路径', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '4步从普通用户到管理员', ha='center', fontsize=10, color=COLORS['muted'])
    steps = [
        (0.3, 3.8, 2.4, 2.0, '#991b1b', '① 初始入口', ['弱密码/钓鱼/漏洞', '拿到普通用户账号', '']),
        (3.2, 3.8, 2.4, 2.0, '#9a3412', '② 枚举权限', ['list-attached-', 'user-policies', '探测可用权限']),
        (6.1, 3.8, 2.4, 2.0, '#92400e', '③ 权限组合', ['PassRole+RunInstances', 'CreateAccessKey', 'AttachUserPolicy']),
        (9.0, 3.8, 2.6, 2.0, '#166534', '④ 持久化', ['创建后门账户', '修改IAM策略', '完全控制云账号']),
    ]
    for (x, y, w, h, color, title, lines) in steps:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor=color, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=color)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.8 - i*0.5, line, ha='center', fontsize=9, color=COLORS['text'])
    for i in range(3):
        x = steps[i][0] + steps[i][2]
        ax.annotate('', xy=(steps[i+1][0], 4.8), xytext=(x+0.05, 4.8), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    danger_box = FancyBboxPatch((0.3, 0.9), 11.4, 1.0, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor='#991b1b', linewidth=1.5)
    ax.add_patch(danger_box)
    ax.text(6, 1.65, '最危险的三个权限组合', ha='center', fontsize=11, fontweight='bold', color='#991b1b')
    ax.text(1.8, 1.2, 'PassRole+RunInstances', ha='center', fontsize=9, color='#991b1b')
    ax.text(5.5, 1.2, 'CreateAccessKey', ha='center', fontsize=9, color='#991b1b')
    ax.text(9.2, 1.2, 'AttachUserPolicy', ha='center', fontsize=9, color='#991b1b')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_le_flow(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数计算流程', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, 'IAM权限图 → 辫群 → Burau表示 → 特征值 → LE', ha='center', fontsize=10, color=COLORS['muted'])
    boxes = [
        (0.2, 2.8, 2.2, 2.5, '#dbeafe', '#1e40af', 'IAM权限图', ['节点: 用户/角色', '边: 权限关系', '边权重: 危险程度']),
        (3.0, 2.8, 2.2, 2.5, '#fce7f3', '#9d174d', '辫群元素', ['权限链→σᵢ序列', 'σ₁·σ₂⁻¹·σ₃', '非阿贝尔结构']),
        (5.8, 2.8, 2.4, 2.5, '#dcfce7', '#166534', 'Burau表示', ['→ n×n矩阵', '编码缠绕程度', 't变量记录交叉']),
        (8.7, 2.8, 2.2, 2.5, '#fef3c7', '#92400e', '特征值', ['求矩阵特征值', '取最大模', 'max |λᵢ|']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.85 - i*0.55, line, ha='center', fontsize=9, color=COLORS['text'])
    for i in range(3):
        x = boxes[i][0] + boxes[i][2]
        ax.annotate('', xy=(boxes[i+1][0], 4.05), xytext=(x+0.05, 4.05), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    le_box = FancyBboxPatch((8.7, 0.8), 2.2, 1.2, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor='#166534', linewidth=2.5)
    ax.add_patch(le_box)
    ax.text(9.8, 1.7, 'LE', ha='center', fontsize=20, fontweight='bold', color='#166534')
    ax.text(9.8, 1.2, '= max|λᵢ|', ha='center', fontsize=11, color='#374151')
    ax.annotate('', xy=(9.8, 1.95), xytext=(9.8, 2.75), arrowprops=dict(arrowstyle='->', color='#166534', lw=2))
    meaning_box = FancyBboxPatch((0.2, 0.3), 8.2, 1.5, boxstyle="round,pad=0.08", facecolor='#f3f4f6', edgecolor='#9ca3af', linewidth=1.5)
    ax.add_patch(meaning_box)
    ax.text(4.3, 1.55, 'LE 的物理含义', ha='center', fontsize=12, fontweight='bold', color='#111827')
    high_box = FancyBboxPatch((0.5, 0.4), 3.5, 1.0, boxstyle="round,pad=0.05", facecolor='#fef2f2', edgecolor='#991b1b', linewidth=1.5)
    ax.add_patch(high_box)
    ax.text(2.25, 1.1, 'LE高 → 聚焦型', ha='center', fontsize=11, color='#991b1b', fontweight='bold')
    ax.text(2.25, 0.65, '少数关键节点掌握大量权限', ha='center', fontsize=9, color='#374151')
    low_box = FancyBboxPatch((4.5, 0.4), 3.5, 1.0, boxstyle="round,pad=0.05", facecolor='#dcfce7', edgecolor='#166534', linewidth=1.5)
    ax.add_patch(low_box)
    ax.text(6.25, 1.1, 'LE低 → 分散型', ha='center', fontsize=11, color='#166534', fontweight='bold')
    ax.text(6.25, 0.65, '权限分散，无明显单点弱点', ha='center', fontsize=9, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_cross_domain(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '跨域泛化：零调参的特权升级检测', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '同构拓扑结构 -> 训练与部署无需适配', ha='center', fontsize=10, color=COLORS['muted'])
    solar_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2.5)
    ax.add_patch(solar_box)
    ax.text(2.55, 4.7, 'AWS Solar', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
    ax.text(2.55, 4.2, '训练数据集', ha='center', fontsize=10, color=COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(1.0, '#fef3c7', '#92400e'), (2.3, '#dbeafe', '#1e40af'), (3.6, '#fce7f3', '#9d174d')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'U{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    ax.annotate('', xy=(5.2, 3.75), xytext=(4.8, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(5.0, 4.1, '提取\n拓扑特征', ha='center', fontsize=9, color=COLORS['muted'])
    model_box = FancyBboxPatch((5.5, 2.8), 2.0, 1.8, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor='#166534', linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(6.5, 4.3, 'LE 模型', ha='center', fontsize=12, fontweight='bold', color='#166534')
    ax.text(6.5, 3.85, 'Burau-\nLyapunov\n指数', ha='center', fontsize=10, color='#166534')
    ax.annotate('', xy=(8.2, 3.75), xytext=(7.5, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(7.85, 4.1, '直接\n部署', ha='center', fontsize=9, color=COLORS['muted'])
    star_box = FancyBboxPatch((8.2, 2.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor='#92400e', linewidth=2.5)
    ax.add_patch(star_box)
    ax.text(9.95, 4.7, 'Stard Astro', ha='center', fontsize=13, fontweight='bold', color='#92400e')
    ax.text(9.95, 4.2, '完全不同域', ha='center', fontsize=10, color=COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(8.6, '#dcfce7', '#166534'), (9.6, '#fef3c7', '#92400e'), (10.6, '#dbeafe', '#1e40af')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'R{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    result_box = FancyBboxPatch((4.5, 0.5), 4.0, 1.5, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#6b7280', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(6.5, 1.75, '检测效果对比', ha='center', fontsize=12, fontweight='bold', color='#111827')
    ax.text(5.3, 1.2, '训练集(Solar): AUC 0.92', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(7.7, 1.2, '测试集(Stard): AUC 0.89', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(6.5, 0.7, '无需调参，结构同构 -> 泛化能力强', ha='center', fontsize=10, color=COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_cloud_graph(out_path):
    """场景1: 云平台 logo 变成一张密密麻麻的权限关系图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.5, '云平台 IAM 权限关系图', ha='center', fontsize=18, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.0, '用户、角色、服务账户之间的权限传递路径', ha='center', fontsize=11, color=COLORS['muted'])
    nodes = {
        'Root': (6, 5), 'Admin': (3, 4), 'Dev': (9, 4),
        'Svc1': (4, 2.5), 'Svc2': (8, 2.5), 'Bob': (2, 3), 'Alice': (10, 3),
    }
    edges = [
        ('Root', 'Admin'), ('Root', 'Dev'), ('Admin', 'Svc1'),
        ('Admin', 'Svc2'), ('Dev', 'Svc1'), ('Dev', 'Bob'),
        ('Svc1', 'Svc2'), ('Alice', 'Svc2'), ('Bob', 'Alice'),
    ]
    for (a, b) in edges:
        xa, ya = nodes[a]; xb, yb = nodes[b]
        ax.annotate('', xy=(xb, yb), xytext=(xa, ya),
                    arrowprops=dict(arrowstyle='->', color='#9ca3af', lw=1.5, alpha=0.7))
    for name, (x, y) in nodes.items():
        color = '#991b1b' if name == 'Root' else '#1e40af' if name in ('Admin', 'Dev') else '#166534'
        circle = plt.Circle((x, y), 0.35, facecolor=color, edgecolor='#374151', linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    ax.text(6, 0.8, '每条边 = 一条权限传递路径 = 黑客可能的提权链路', ha='center', fontsize=11, color=COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_three_methods(out_path):
    """场景2: 三种方法的逐一图示"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '特权升级检测的三条路', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    methods = [
        (0.5, 3.0, 3.5, 2.8, '#fee2e2', '#991b1b', '规则匹配', ['已知攻击签名', '特征码匹配', '局限：无法检测新招']),
        (4.3, 3.0, 3.5, 2.8, '#fef3c7', '#92400e', '行为异常', ['统计正常行为', '检测统计偏离', '局限：可被模仿潜伏']),
        (8.1, 3.0, 3.5, 2.8, '#e0e7ff', '#3730a3', '手工图分析', ['人工定义规则', '专家知识驱动', '局限：大规模看不过来']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in methods:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=13, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 1.0 - i*0.6, line, ha='center', fontsize=11, color=COLORS['text'])
    ax.text(6, 0.5, '共同问题：在这套系统上训练的检测方法，换到另一套云环境还能用吗？', ha='center', fontsize=11, color='#991b1b', fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_graph_to_braid(out_path):
    """场景3: IAM 权限图 → 编织动画"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '权限路径 = 一根辫子', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '交换相邻两个权限的位置 = 辫子的交叉动作 σᵢ', ha='center', fontsize=10, color=COLORS['muted'])
    # 左边：权限图
    graph_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.8, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2)
    ax.add_patch(graph_box)
    ax.text(2.55, 5.0, 'IAM 权限图', ha='center', fontsize=12, fontweight='bold', color='#1e40af')
    nodes = [('A', 1.5, 4.2), ('B', 2.8, 4.2), ('C', 4.1, 4.2)]
    for name, x, y in nodes:
        circle = plt.Circle((x, y), 0.25, facecolor='#1e40af', edgecolor='#1e40af')
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    coords = [(x, y) for _, x, y in nodes]
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', color='#1e40af', lw=2))
    ax.text(2.55, 2.85, '交换 A↔B 权限', ha='center', fontsize=10, color='#374151')
    ax.annotate('', xy=(6.3, 4.2), xytext=(5.5, 4.2), arrowprops=dict(arrowstyle='->', color='#374151', lw=3))
    ax.text(5.9, 4.6, '映射', ha='center', fontsize=10, color='#374151')
    # 右边：辫子
    braid_box = FancyBboxPatch((6.5, 2.5), 5.0, 2.8, boxstyle="round,pad=0.1", facecolor='#fce7f3', edgecolor='#9d174d', linewidth=2)
    ax.add_patch(braid_box)
    ax.text(9, 5.0, '辫群元素 σᵢ', ha='center', fontsize=12, fontweight='bold', color='#9d174d')
    t = np.linspace(0, 1, 200)
    colors = ['#1e40af', '#9d174d', '#166534']
    x_starts = [7.2, 9.0, 10.8]
    for i, (xs, c) in enumerate(zip(x_starts, colors)):
        if i == 0:
            bx = xs + 0.6 * np.sin(np.pi * t)
        elif i == 1:
            bx = xs - 0.6 * np.sin(np.pi * t)
        else:
            bx = np.full_like(t, xs)
        by = 5.0 - 2.2 * t
        ax.plot(bx, by, color=c, linewidth=3, zorder=3)
    sigma_box = FancyBboxPatch((8.3, 2.7), 1.5, 0.7, boxstyle='round,pad=0.2', facecolor='#fce7f3', edgecolor='#9d174d', linewidth=2)
    ax.add_patch(sigma_box)
    ax.text(9.05, 3.05, 'σ₁', ha='center', fontsize=14, fontweight='bold', color='#9d174d')
    ax.text(9.0, 2.65, '非阿贝尔：σ₁σ₂ ≠ σ₂σ₁', ha='center', fontsize=9, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_burau_pipeline(out_path):
    """场景4: 辫群 → Burau表示 → 矩阵 → 特征值 → 数值"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数计算', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    steps = [
        (0.2, 2.8, 2.2, 2.5, '#dbeafe', '#1e40af', '辫群元素', ['σ₁·σ₂⁻¹·σ₃', '权限链序列']),
        (3.0, 2.8, 2.2, 2.5, '#fce7f3', '#9d174d', 'Burau表示', ['→ n×n矩阵', 't变量记录缠绕']),
        (5.8, 2.8, 2.2, 2.5, '#dcfce7', '#166534', '求特征值', ['|λ₁|, |λ₂|...', '取最大模']),
        (8.6, 2.8, 2.6, 2.5, '#fef3c7', '#92400e', 'LE 指数', ['LE = max|λᵢ|', '量化危险程度']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in steps:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.9 - i*0.6, line, ha='center', fontsize=10, color=COLORS['text'])
    for i in range(3):
        xi = steps[i][0] + steps[i][2]
        ax.annotate('', xy=(steps[i+1][0], 4.05), xytext=(xi+0.05, 4.05), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    le_box = FancyBboxPatch((8.6, 0.8), 2.6, 1.2, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor='#166534', linewidth=2.5)
    ax.add_patch(le_box)
    ax.text(9.9, 1.7, 'LE', ha='center', fontsize=20, fontweight='bold', color='#166534')
    ax.text(9.9, 1.2, '= max|λᵢ|', ha='center', fontsize=11, color='#374151')
    ax.annotate('', xy=(9.9, 1.95), xytext=(9.9, 2.75), arrowprops=dict(arrowstyle='->', color='#166534', lw=2))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_abelian_proof(out_path):
    """场景5: 数学公式——不存在任何阿贝尔统计量能复制 LE 的区分能力"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.text(6, 7.4, '核心数学结论', ha='center', fontsize=18, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.9, '严格证明，非实验观察', ha='center', fontsize=11, color=COLORS['muted'])
    # 聚焦型示意
    ax.text(2.5, 6.2, '聚焦型（LE高）', ha='center', fontsize=12, fontweight='bold', color='#991b1b')
    for i, (x, c) in enumerate([(1.0, '#991b1b'), (2.0, '#d1d5db'), (3.0, '#d1d5db')]):
        circle = plt.Circle((x + 0.5, 5.4), 0.35, facecolor=c, edgecolor='#6b7280', linewidth=1)
        ax.add_patch(circle)
    ax.annotate('', xy=(2.0, 5.4), xytext=(1.5, 5.4), arrowprops=dict(arrowstyle='->', color='#991b1b', lw=2))
    ax.text(2.5, 4.7, '少数关键节点\n掌握大量权限', ha='center', fontsize=9, color='#374151')
    ax.text(2.5, 4.1, '均值=0.33  方差=0.11', ha='center', fontsize=9, color='#6b7280')
    # 分散型示意
    ax.text(9.5, 6.2, '分散型（LE低）', ha='center', fontsize=12, fontweight='bold', color='#166534')
    for i, (x, c) in enumerate([(8.0, '#d1d5db'), (9.0, '#d1d5db'), (10.0, '#d1d5db'), (8.5, '#d1d5db'), (9.5, '#d1d5db'), (10.5, '#d1d5db')]):
        circle = plt.Circle((x, 5.4), 0.25, facecolor=c, edgecolor='#6b7280', linewidth=1)
        ax.add_patch(circle)
    ax.text(9.5, 4.7, '权限分散各处\n无明显单点弱点', ha='center', fontsize=9, color='#374151')
    ax.text(9.5, 4.1, '均值=0.33  方差=0.09', ha='center', fontsize=9, color='#6b7280')
    # 核心结论
    conclusion_box = FancyBboxPatch((0.8, 0.8), 10.4, 2.2, boxstyle="round,pad=0.1", facecolor='#1a2e3d', edgecolor='#60a5fa', linewidth=2)
    ax.add_patch(conclusion_box)
    ax.text(6, 2.7, '不存在任何阿贝尔统计量', ha='center', fontsize=13, fontweight='bold', color='#60a5fa')
    ax.text(6, 2.15, '能复制 LE 对"聚焦型"和"分散型"的区分能力', ha='center', fontsize=11, color='#93c5fd')
    ax.text(6, 1.55, '均值、方差、熵的任意组合均无法替代', ha='center', fontsize=11, color='#93c5fd')
    ax.text(6, 1.0, 'LE 测量的是非阿贝尔结构，无法被交换顺序不变量刻画', ha='center', fontsize=10, color='#60a5fa')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_cross_domain_effect(out_path):
    """场景6: Solar训练 → 直接应用到Stard Astrophysics → 效果对比"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '跨域泛化效果', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '拓扑同构 -> 零调参跨域检测', ha='center', fontsize=10, color=COLORS['muted'])
    solar_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2.5)
    ax.add_patch(solar_box)
    ax.text(2.55, 4.7, 'AWS Solar', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
    ax.text(2.55, 4.2, '训练集', ha='center', fontsize=10, color=COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(1.0, '#fef3c7', '#92400e'), (2.3, '#dbeafe', '#1e40af'), (3.6, '#fce7f3', '#9d174d')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
    ax.annotate('', xy=(5.2, 3.75), xytext=(4.8, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(5.0, 4.1, '提取\n拓扑特征', ha='center', fontsize=9, color=COLORS['muted'])
    model_box = FancyBboxPatch((5.5, 2.8), 2.0, 1.8, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor='#166534', linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(6.5, 4.3, 'LE 模型', ha='center', fontsize=12, fontweight='bold', color='#166534')
    ax.annotate('', xy=(8.2, 3.75), xytext=(7.5, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(7.85, 4.1, '直接部署', ha='center', fontsize=9, color=COLORS['muted'])
    star_box = FancyBboxPatch((8.2, 2.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor='#92400e', linewidth=2.5)
    ax.add_patch(star_box)
    ax.text(9.95, 4.7, 'Stard Astro', ha='center', fontsize=13, fontweight='bold', color='#92400e')
    ax.text(9.95, 4.2, '测试集（完全不同域）', ha='center', fontsize=10, color=COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(8.6, '#dcfce7', '#166534'), (9.6, '#fef3c7', '#92400e'), (10.6, '#dbeafe', '#1e40af')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
    result_box = FancyBboxPatch((4.5, 0.5), 4.0, 1.5, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#6b7280', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(6.5, 1.75, '检测效果几乎不变', ha='center', fontsize=12, fontweight='bold', color='#166534')
    ax.text(5.3, 1.2, '训练 AUC: 0.92', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(7.7, 1.2, '测试 AUC: 0.89', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(6.5, 0.7, '不需要调参 / 重训练 / 适配', ha='center', fontsize=10, color=COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_attack_disperse(out_path):
    """场景7: LE升高 → 攻击者分散权限 → LE降低"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '攻防博弈：LE 被反向利用', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '攻击者知道 LE 计算方式后，可以刻意分散权限来隐藏攻击路径', ha='center', fontsize=10, color=COLORS['muted'])
    # 攻击前
    ax.text(2.0, 5.5, '攻击前：LE 高', ha='center', fontsize=12, fontweight='bold', color='#991b1b')
    for i, (x, c) in enumerate([(1.0, '#991b1b'), (2.0, '#d1d5db'), (3.0, '#d1d5db')]):
        circle = plt.Circle((x + 0.5, 4.7), 0.35, facecolor=c, edgecolor='#6b7280', linewidth=1)
        ax.add_patch(circle)
    ax.text(2.0, 4.0, '少数节点\n掌握大量权限', ha='center', fontsize=9, color='#374151')
    ax.text(2.0, 3.4, 'LE = 0.87', ha='center', fontsize=11, fontweight='bold', color='#991b1b')
    # 箭头
    ax.annotate('', xy=(5.8, 4.7), xytext=(4.5, 4.7), arrowprops=dict(arrowstyle='->', color='#374151', lw=2))
    ax.text(5.15, 5.0, '攻击者\n分散权限', ha='center', fontsize=9, color='#374151')
    # 攻击后
    ax.text(9.0, 5.5, '攻击后：LE 低', ha='center', fontsize=12, fontweight='bold', color='#166534')
    for i, (x, c) in enumerate([(7.5, '#d1d5db'), (8.5, '#d1d5db'), (9.5, '#d1d5db'), (10.5, '#d1d5db')]):
        circle = plt.Circle((x, 4.7), 0.3, facecolor=c, edgecolor='#6b7280', linewidth=1)
        ax.add_patch(circle)
    ax.text(9.0, 4.0, '权限分散各处\n攻击路径被隐藏', ha='center', fontsize=9, color='#374151')
    ax.text(9.0, 3.4, 'LE = 0.34', ha='center', fontsize=11, fontweight='bold', color='#166534')
    # 底部问题
    q_box = FancyBboxPatch((0.5, 0.8), 11, 1.2, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor='#92400e', linewidth=1.5)
    ax.add_patch(q_box)
    ax.text(6, 1.7, '新问题：给定安全级别约束，怎样分配权限才能让 LE 最小化？', ha='center', fontsize=12, fontweight='bold', color='#92400e')
    ax.text(6, 1.1, '这是下一个研究方向', ha='center', fontsize=10, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_le_formula(out_path):
    """场景8: LE指数的核心公式"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数', ha='center', fontsize=18, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.1, '通过辫群的 Burau 表示，量化 IAM 图的结构复杂度', ha='center', fontsize=11, color=COLORS['muted'])
    # 公式区
    formula_box = FancyBboxPatch((1.5, 3.5), 9.0, 2.0, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#6b7280', linewidth=2)
    ax.add_patch(formula_box)
    ax.text(6, 5.0, 'LE  =  max |λᵢ(B(σ))|', ha='center', fontsize=18, fontweight='bold', color='#1e40af')
    ax.text(6, 4.3, 'B(σ) = Burau 表示矩阵（编码辫子缠绕程度）', ha='center', fontsize=11, color='#374151')
    ax.text(6, 3.8, 'λᵢ  =  B(σ) 的第 i 个特征值', ha='center', fontsize=11, color='#374151')
    # 含义
    high_box = FancyBboxPatch((0.5, 1.2), 5.0, 1.5, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor='#991b1b', linewidth=1.5)
    ax.add_patch(high_box)
    ax.text(3.0, 2.35, 'LE 高 -> 聚焦型危险', ha='center', fontsize=12, fontweight='bold', color='#991b1b')
    ax.text(3.0, 1.75, '少数关键节点掌握大量权限', ha='center', fontsize=10, color='#374151')
    ax.text(3.0, 1.3, '攻击者集中打这几个点', ha='center', fontsize=10, color='#374151')
    low_box = FancyBboxPatch((6.5, 1.2), 5.0, 1.5, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor='#166534', linewidth=1.5)
    ax.add_patch(low_box)
    ax.text(9.0, 2.35, 'LE 低 -> 分散型', ha='center', fontsize=12, fontweight='bold', color='#166534')
    ax.text(9.0, 1.75, '权限分散，无明显单点弱点', ha='center', fontsize=10, color='#374151')
    ax.text(9.0, 1.3, '攻击路径难以发现', ha='center', fontsize=10, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

# ─── 主函数：从脚本提取场景并生成 ────────────────────────────

def parse_scenes(script_path):
    """从脚本提取所有 [画面：] 场景"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 匹配 [画面：xxx]
    scenes = re.findall(r'\[画面：([^\]]+)\]', content)
    return scenes

def scene_to_key(desc):
    """将场景描述转换为函数键"""
    desc = desc.strip()
    if '云平台' in desc or '权限关系图' in desc:
        return 'cloud_graph'
    if '三种方法' in desc or '逐一图示' in desc:
        return 'three_methods'
    if '编织' in desc or '权限图' in desc:
        return 'graph_to_braid'
    if 'Burau' in desc or '矩阵' in desc or '特征值' in desc:
        return 'burau_pipeline'
    if '阿贝尔' in desc or '不存在' in desc:
        return 'abelian_proof'
    if 'Solar' in desc or 'Stard' in desc or '跨域' in desc:
        return 'cross_domain_effect'
    if '分散' in desc or 'LE 升高' in desc:
        return 'attack_disperse'
    if '公式' in desc or '核心公式' in desc:
        return 'le_formula'
    if '跨域' in desc:
        return 'cross_domain'
    if '攻击路径' in desc:
        return 'attack_path'
    if 'LE' in desc or 'Lyapunov' in desc:
        return 'le_flow'
    return None

SCENE_DRAWERS = {
    'cloud_graph': draw_cloud_graph,
    'three_methods': draw_three_methods,
    'graph_to_braid': draw_graph_to_braid,
    'burau_pipeline': draw_burau_pipeline,
    'abelian_proof': draw_abelian_proof,
    'cross_domain_effect': draw_cross_domain_effect,
    'attack_disperse': draw_attack_disperse,
    'le_formula': draw_le_formula,
}

def check_scene_coverage(script_path):
    """检查脚本中所有 [画面：] 场景是否都有对应绘图函数。返回 (covered, missing)"""
    scenes = parse_scenes(script_path)
    missing = []
    for i, desc in enumerate(scenes, 1):
        key = scene_to_key(desc)
        if key is None or key not in SCENE_DRAWERS:
            missing.append((i, desc))
    return len(scenes), missing

def report_coverage(script_path, strict=False):
    """报告场景覆盖率，若有缺失输出 WARNING 并列出，返回是否有缺失"""
    total, missing = check_scene_coverage(script_path)
    if not missing:
        print(f"  [OK] 全部 {total} 个场景均有绘图函数覆盖")
        return False
    print(f"  [WARN] {len(missing)}/{total} 个场景缺失绘图函数:")
    for idx, desc in missing:
        print(f"    场景{idx}: {desc[:40]}")
    if strict:
        print("  [ERROR] --strict 模式：存在未覆盖场景，退出")
        exit(1)
    return True

def generate_scenes_for_script(script_path, output_prefix, article_name, strict=False):
    """为一个脚本生成封面图和所有场景配图"""
    output_dir = Path(script_path).parent

    # 生成封面图
    title, summary = parse_script_header(script_path)
    if title:
        cover_path = output_dir / f"{output_prefix}-cover.png"
        draw_cover(cover_path, title)
        print(f"  [OK] 封面: {cover_path.name}")
    else:
        cover_path = None
        print(f"  [WARN] 未提取到标题")

    scenes = parse_scenes(script_path)
    if not scenes:
        print(f"  [WARN] 未找到 [画面：] 场景: {script_path}")
        return []
    print(f"  找到 {len(scenes)} 个场景: {[s[:20] for s in scenes]}")
    output_paths = []
    for i, desc in enumerate(scenes, 1):
        key = scene_to_key(desc)
        func = SCENE_DRAWERS.get(key)
        if func is None:
            print(f"  [SKIP] 场景{i} 无对应绘图函数: {desc[:30]}")
            continue
        out_path = output_dir / f"{output_prefix}-scene-{i:02d}.png"
        func(out_path)
        if out_path.exists():
            print(f"  [OK] 场景{i}: {out_path.name}")
            output_paths.append(out_path)
        else:
            print(f"  [SKIP] 场景{i} 文件未生成: {desc[:30]}")
    return output_paths

if __name__ == '__main__':
    import os
    os.makedirs('video', exist_ok=True)

    parser = argparse.ArgumentParser(description="生成视频场景配图")
    parser.add_argument("script", nargs="?", help="视频脚本 .md 路径（不指定则处理所有）")
    parser.add_argument("--strict", action="store_true", help="有未覆盖场景时退出（返回码1）")
    parser.add_argument("--check-only", action="store_true", help="仅检查覆盖率，不生成图片")
    args = parser.parse_args()

    if args.script:
        script = Path(args.script)
        if args.check_only:
            report_coverage(script, strict=args.strict)
        else:
            article_name = script.stem
            nn = article_name.split('-')[0]
            if report_coverage(script, strict=args.strict):
                print("  [ABORT] 有缺失场景，停止生成。补充绘图函数后重试（或去掉 --strict）")
                exit(1)
            generate_scenes_for_script(script, nn, article_name)
    else:
        wiki_root = Path(__file__).parent.parent
        scripts = list(wiki_root.glob("articles/**/*.md"))
        scripts = [s for s in scripts if re.search(r'^\d{2}-', s.name)]
        for script in sorted(scripts):
            print(f"\n处理: {script.relative_to(wiki_root)}")
            nn = script.stem.split('-')[0]
            if args.check_only:
                report_coverage(script, strict=args.strict)
            else:
                if report_coverage(script, strict=args.strict):
                    print("  [ABORT] 有缺失场景，停止生成")
                    exit(1)
                generate_scenes_for_script(script, nn, script.stem)
