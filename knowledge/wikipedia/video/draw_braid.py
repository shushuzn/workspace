"""
生成高质量科普配图
依赖: pip install matplotlib pillow numpy
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.style.use('default')
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
COLORS = {
    'bg': '#ffffff', 'blue': '#1e40af', 'pink': '#9d174d',
    'green': '#166534', 'yellow': '#92400e', 'red': '#991b1b',
    'orange': '#9a3412', 'text': '#111827', 'muted': '#374151', 'grid': '#d1d5db',
}

def new_fig(figsize=(10, 6)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.axis('off')
    return fig, ax

def draw_braid_group():
    fig, ax = new_fig((10, 7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.text(5, 6.5, '辫群 B₃ 的编织方式', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(5, 6.1, '非阿贝尔结构：σ₁σ₂ ≠ σ₂σ₁', ha='center', fontsize=10, color=COLORS['muted'])
    top_plate = FancyBboxPatch((1, 5.2), 8, 0.15, boxstyle="round,pad=0.02", facecolor='#e5e7eb', edgecolor='#6b7280')
    ax.add_patch(top_plate)
    for i, (x, color) in enumerate(zip([2.5, 5, 7.5], ['#1e40af', '#9d174d', '#166534'])):
        circle = plt.Circle((x, 5.5), 0.18, color=color, zorder=5)
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
        circle = plt.Circle((x, 1.3), 0.18, color=color, zorder=5)
        ax.add_patch(circle)
    sigma_style = dict(boxstyle='round,pad=0.3', facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2)
    ax.text(3.5, 3.6, 'σ₁', fontsize=16, fontweight='bold', color='#1e40af', ha='center', bbox=sigma_style)
    ax.text(6.0, 2.8, 'σ₂', fontsize=16, fontweight='bold', color='#9d174d', ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fce7f3', edgecolor='#9d174d', linewidth=2))
    rule_box = FancyBboxPatch((0.5, 0.1), 9, 0.7, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#9ca3af', linewidth=1.5)
    ax.add_patch(rule_box)
    ax.text(5, 0.45, '规则一：局部性（隔着≥1根可换位）  |  规则二：Yang-Baxter方程 σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁', ha='center', fontsize=10, color='#374151')
    plt.tight_layout()
    plt.savefig('video/fig-01-braid-group.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("Saved video/fig-01-braid-group.png")

def draw_iam_model():
    fig, ax = new_fig((12, 7))
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
    plt.savefig('video/fig-02-iam-model.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("Saved video/fig-02-iam-model.png")

def draw_attack_path():
    fig, ax = new_fig((12, 7))
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
    plt.savefig('video/fig-03-attack-path.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("Saved video/fig-03-attack-path.png")

def draw_le_flow():
    fig, ax = new_fig((12, 7))
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
    plt.savefig('video/fig-04-le-flow.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("Saved video/fig-04-le-flow.png")

def draw_cross_domain():
    """跨域泛化示意图：Solar训练 → 直接应用到Stard Astrophysics"""
    fig, ax = new_fig((12, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '跨域泛化：零调参的特权升级检测', ha='center', fontsize=16, fontweight='bold', color=COLORS['text'])
    ax.text(6, 6.2, '同构拓扑结构 → 训练与部署无需适配', ha='center', fontsize=10, color=COLORS['muted'])
    # 左边：Solar 亚马逊云
    solar_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor='#1e40af', linewidth=2.5)
    ax.add_patch(solar_box)
    ax.text(2.55, 4.7, 'AWS Solar', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
    ax.text(2.55, 4.2, '训练数据集', ha='center', fontsize=10, color=COLORS['muted'])
    # IAM图示（Solar侧）
    for i, (x, fc, ec) in enumerate([(1.0, '#fef3c7', '#92400e'), (2.3, '#dbeafe', '#1e40af'), (3.6, '#fce7f3', '#9d174d')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'U{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    ax.annotate('', xy=(5.2, 3.75), xytext=(4.8, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(5.0, 4.1, '提取\n拓扑特征', ha='center', fontsize=9, color=COLORS['muted'])
    # 中间：LE模型
    model_box = FancyBboxPatch((5.5, 2.8), 2.0, 1.8, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor='#166534', linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(6.5, 4.3, 'LE 模型', ha='center', fontsize=12, fontweight='bold', color='#166534')
    ax.text(6.5, 3.85, 'Burau-\nLyapunov\n指数', ha='center', fontsize=10, color='#166534')
    ax.annotate('', xy=(8.2, 3.75), xytext=(7.5, 3.75), arrowprops=dict(arrowstyle='->', color=COLORS['muted'], lw=2))
    ax.text(7.85, 4.1, '直接\n部署', ha='center', fontsize=9, color=COLORS['muted'])
    # 右边：Stard Astrophysics 私有云
    star_box = FancyBboxPatch((8.2, 2.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor='#92400e', linewidth=2.5)
    ax.add_patch(star_box)
    ax.text(9.95, 4.7, 'Stard Astro', ha='center', fontsize=13, fontweight='bold', color='#92400e')
    ax.text(9.95, 4.2, '完全不同域', ha='center', fontsize=10, color=COLORS['muted'])
    # IAM图示（Stard侧，不同拓扑但同构）
    for i, (x, fc, ec) in enumerate([(8.6, '#dcfce7', '#166534'), (9.6, '#fef3c7', '#92400e'), (10.6, '#dbeafe', '#1e40af')]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'R{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    # 效果对比
    result_box = FancyBboxPatch((4.5, 0.5), 4.0, 1.5, boxstyle="round,pad=0.1", facecolor='#f3f4f6', edgecolor='#6b7280', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(6.5, 1.75, '检测效果对比', ha='center', fontsize=12, fontweight='bold', color='#111827')
    ax.text(5.3, 1.2, '训练集(Solar): AUC 0.92', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(7.7, 1.2, '测试集(Stard): AUC 0.89', ha='center', fontsize=10, color='#166534', fontweight='bold')
    ax.text(6.5, 0.7, '无需调参，结构同构 -> 泛化能力强', ha='center', fontsize=10, color=COLORS['muted'])
    plt.tight_layout()
    plt.savefig('video/fig-05-cross-domain.png', dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print("Saved video/fig-05-cross-domain.png")

if __name__ == '__main__':
    import os
    os.makedirs('video', exist_ok=True)
    draw_braid_group()
    draw_iam_model()
    draw_attack_path()
    draw_le_flow()
    draw_cross_domain()
    print("All done!")
