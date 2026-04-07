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
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from video.config import (
    T2I_MODEL, T2I_STEPS, T2I_GUIDANCE, T2I_SEED,
    TTS_ENGINE, KOKORO_VOICE_ZH, KOKORO_VOICE_EN,
    RATE, PITCH,
)

plt.style.use('default')
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
# 专业排版参数
matplotlib.rcParams['axes.spines.top'] = False
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['figure.edgecolor'] = 'none'

# 渐变色工厂
def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

def gradient_cmap(hex_start, hex_end, steps=50):
    """创建渐变 colormap"""
    import matplotlib.colors as mcolors
    c1, c2 = hex_to_rgb(hex_start), hex_to_rgb(hex_end)
    stops = np.linspace(0, 1, steps)
    colors = [(c1[0]+(c2[0]-c1[0])*s, c1[1]+(c2[1]-c1[1])*s, c1[2]+(c2[2]-c1[2])*s) for s in stops]
    return mcolors.LinearSegmentedColormap.from_list('grad', colors)

# ─── 专业视觉效果辅助 ───────────────────────────────────────────
from matplotlib.patches import Shadow

def shadow_box(ax, patch, offset=(3, -3), alpha=0.15, color='#000000'):
    """为 patch 添加阴影（复制 patch 并偏移淡化）"""
    shadow_patch = Shadow(patch, offset[0], offset[1], alpha=alpha, color=color)
    ax.add_patch(shadow_patch)
    return shadow_patch

def glow_circle(ax, cx, cy, radius, glow_color, n=3):
    """在圆周围添加辉光效果（多层半透明圆叠加）"""
    for i in range(n, 0, -1):
        r = radius * (1 + i * 0.4)
        alpha = 0.06 * (n - i + 1) / n
        glow = plt.Circle((cx, cy), r, facecolor=glow_color, alpha=alpha, zorder=0)
        ax.add_patch(glow)

def draw_title_bar(ax, text, y=7.2, fontsize=18, color='#1d4ed8', bold=True):
    """绘制带底部装饰线的标题"""
    ax.text(6, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold' if bold else 'normal', color=color, zorder=5)
    # 装饰线
    ax.axhline(y=y-0.25, xmin=0.3, xmax=0.7, color=color, linewidth=2, alpha=0.6, zorder=4)

def card(ax, x, y, w, h, facecolor, edgecolor, linewidth=2, label=None,
         shadow=True, shadow_offset=(2, -2), glow_color=None, glow_radius=None):
    """绘制带阴影的专业卡片框

    shadow: 是否添加阴影
    glow_color + glow_radius: 是否添加发光效果（用于高亮卡片）
    """
    # 先画阴影
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.1",
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=linewidth, zorder=3)
    if shadow:
        shadow_box(ax, box, offset=shadow_offset, alpha=0.12)
    ax.add_patch(box)
    # 发光效果
    if glow_color and glow_radius:
        glow_circle(ax, x + w/2, y + h/2, glow_radius, glow_color)
    # 标签
    if label:
        ax.text(x + w/2, y + h - 0.3, label,
                ha='center', fontsize=11, fontweight='bold', color=edgecolor, zorder=5)
    return box

def styled_arrow(ax, x0, y0, x1, y1, color='#64748b', lw=2.5, style='->',
                 label=None, label_offset=(0, 0.3)):
    """绘制带标签的箭头（美观样式）"""
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                 arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle='arc3,rad=0.0'),
                 zorder=4)
    if label:
        mx, my = (x0+x1)/2 + label_offset[0], (y0+y1)/2 + label_offset[1]
        ax.text(mx, my, label, ha='center', fontsize=9, color=color, alpha=0.8, zorder=5)

# ─── T2I 引擎（Stable Diffusion 2.1）─────────────────────────
_SD_PIPELINE = None

def _get_sd_pipeline():
    """单例 SD 2.1 DiffusersPipeline（FP16，RTX3060 可跑）"""
    global _SD_PIPELINE
    if _SD_PIPELINE is not None:
        return _SD_PIPELINE

    try:
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
        import torch
        import imageio_ffmpeg

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        print(f"  [SD] 加载模型到 {device} ({dtype})，首次需下载 ~2GB...")
        pipe = StableDiffusionPipeline.from_pretrained(
            T2I_MODEL,  # runwayml/stable-diffusion-v1-5 (open, no auth)
            torch_dtype=dtype,
            safety_checker=None,   # 去掉审查加速
        )
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to(device)

        # VRAM 优化：RTX3060 12G 可同时跑 batch
        if device == "cuda":
            pipe.enable_attention_slicing()   # 减少 VRAM 峰值
            try:
                pipe.enable_vae_slicing()      # 分片 VAE decode
            except Exception:
                pass

        _SD_PIPELINE = pipe
        print(f"  [SD] 模型加载完成")
        return pipe
    except ImportError as e:
        print(f"  [SD] 缺少依赖: {e}，将使用 matplotlib 渲染")
        return None
    except Exception as e:
        print(f"  [SD] 初始化失败: {e}，将使用 matplotlib 渲染")
        return None

# 专业配色方案（3xx-like 深色系）
COLORS = {
    # 主题：深邃学术蓝
    'bg': '#0f172a',       # 深蓝黑背景
    'bg_card': '#1e293b',   # 卡片背景
    'bg_light': '#334155',  # 浅色背景
    'primary': '#38bdf8',   # 主蓝（亮）
    'secondary': '#818cf8', # 紫
    'accent_red': '#f87171',  # 警示红
    'accent_green': '#4ade80', # 成功绿
    'accent_orange': '#fb923c', # 橙色
    'accent_yellow': '#fbbf24', # 黄色
    'text': '#f1f5f9',     # 主文本
    'text_muted': '#94a3b8', # 次要文本
    'border': '#475569',    # 边框
    'grid': '#1e293b',     # 网格
}

# 中文内容配色（浅色背景，保证可读性）
ZH_COLORS = {
    'bg': '#f8fafc', 'bg_card': '#f1f5f9', 'blue': '#1d4ed8',
    'green': '#15803d', 'red': '#dc2626', 'orange': '#c2410c',
    'yellow': '#b45309', 'text': '#1e293b', 'muted': '#64748b',
    'border': '#cbd5e1',
}

def new_fig(figsize=(12, 8), dark=True):
    """创建专业图表背景

    Args:
        dark: True=深色学术风(封面), False=浅色中文可读风(场景配图)
    """
    c = COLORS if dark else ZH_COLORS
    fig, ax = plt.subplots(figsize=figsize, facecolor=c['bg'])
    ax.set_facecolor(c['bg'])
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
    """封面图：深色学术风格，标题居中，专业科普感"""
    c = COLORS
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=c['bg'])
    ax.set_facecolor(c['bg'])
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    # 背景渐变（顶部深蓝→底部黑）
    import matplotlib.colors as mcolors
    grad_data = np.linspace(0, 1, 256).reshape(256, 1)
    cmap_grad = gradient_cmap('#0f3460', '#0f172a')
    ax.imshow(cmap_grad(grad_data), extent=[0, 12, 0, 8], aspect='auto', alpha=0.5, zorder=0)
    # 装饰光晕
    glow_circle(ax, 10.5, 7.0, 2.2, c['primary'], n=5)
    glow_circle(ax, 1.5, 1.0, 1.5, c['secondary'], n=3)
    # 底部装饰线
    ax.axhline(y=2.5, xmin=0.1, xmax=0.9, color=c['border'], linewidth=1.2, alpha=0.5)
    # 主标题
    if len(title) > 20:
        ax.text(6, 4.5, title, ha='center', va='center', fontsize=22,
                fontweight='bold', color=c['text'], linespacing=1.8, zorder=5)
    else:
        ax.text(6, 4.5, title, ha='center', va='center', fontsize=28,
                fontweight='bold', color=c['text'], linespacing=1.8, zorder=5)
    # 底部标注
    ax.text(6, 2.2, 'Wikipedia · 论文解读', ha='center', fontsize=11,
            color=c['text_muted'], alpha=0.7)
    plt.tight_layout(pad=0)
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=c['bg'])
    plt.close()

# ─── 配图绘制函数 ─────────────────────────────────────────

def draw_braid_group(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7)
    ax.text(5, 6.5, '辫群 B₃ 的编织方式', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(5, 6.1, '非阿贝尔结构：σ₁σ₂ ≠ σ₂σ₁', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    top_plate = FancyBboxPatch((1, 5.2), 8, 0.15, boxstyle="round,pad=0.02", facecolor='#f1f5f9', edgecolor='#64748b')
    ax.add_patch(top_plate)
    for i, (x, color) in enumerate(zip([2.5, 5, 7.5], [ZH_COLORS['blue'], ZH_COLORS['red'], ZH_COLORS['green']])):
        circle = plt.Circle((x, 5.5), 0.18, facecolor=color)
        ax.add_patch(circle)
        ax.text(x, 5.8, f'#{i+1}', ha='center', fontsize=9, color=ZH_COLORS['muted'], fontweight='bold')
    t = np.linspace(0, 1, 300)
    bx1 = 2.5 + 1.5 * np.sin(np.pi * t); by1 = 5.3 - 4.1 * t
    ax.plot(bx1, by1, color=ZH_COLORS['blue'], linewidth=4, zorder=3)
    bx2 = 5 - 1.5 * np.sin(np.pi * t); by2 = 5.3 - 4.1 * t
    ax.plot(bx2, by2, color=ZH_COLORS['red'], linewidth=4, zorder=3)
    bx3 = np.full_like(t, 7.5); by3 = 5.3 - 4.1 * t
    ax.plot(bx3, by3, color=ZH_COLORS['green'], linewidth=4, zorder=3)
    bottom_plate = FancyBboxPatch((1, 1.0), 8, 0.15, boxstyle="round,pad=0.02", facecolor='#f1f5f9', edgecolor='#64748b')
    ax.add_patch(bottom_plate)
    for i, (x, color) in enumerate(zip([2.5, 5, 7.5], [ZH_COLORS['blue'], ZH_COLORS['red'], ZH_COLORS['green']])):
        circle = plt.Circle((x, 1.3), 0.18, facecolor=color)
        ax.add_patch(circle)
    sigma_style = dict(boxstyle='round,pad=0.3', facecolor='#dbeafe', edgecolor=ZH_COLORS['blue'], linewidth=2)
    ax.text(3.5, 3.6, 'σ₁', fontsize=16, fontweight='bold', color=ZH_COLORS['blue'], ha='center', bbox=sigma_style)
    ax.text(6.0, 2.8, 'σ₂', fontsize=16, fontweight='bold', color=ZH_COLORS['red'], ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fce7f3', edgecolor=ZH_COLORS['red'], linewidth=2))
    rule_box = FancyBboxPatch((0.5, 0.1), 9, 0.7, boxstyle="round,pad=0.1", facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.5)
    ax.add_patch(rule_box)
    ax.text(5, 0.45, '规则一：局部性（隔着≥1根可换位）  |  规则二：Yang-Baxter方程 σᵢσᵢ₊₁σᵢ = σᵢ₊₁σᵢσᵢ₊₁', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_iam_model(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'IAM 云身份与访问管理模型', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.25, '身份 · 权限 · 资源', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    boxes = [
        (0.5, 1.2, 3.3, 4.5, '#dbeafe', ZH_COLORS['blue'], '身份 Identity', ['你是谁？', '', 'User (root/普通)', 'Group (运维/审计...)', 'Role (临时权限)']),
        (4.35, 1.2, 3.3, 4.5, '#fce7f3', ZH_COLORS['red'], '权限 Permission', ['你能做什么？', '', 'Policy 文档定义', 'Allow / Deny', '对哪个资源+操作']),
        (8.2, 1.2, 3.3, 4.5, '#dcfce7', ZH_COLORS['green'], '资源 Resource', ['哪些需要保护？', '', 'S3 存储桶', 'EC2 服务器', 'Lambda 函数'])
    ]
    for (x, y, w, h, fc, ec, title, lines) in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.35, title, ha='center', fontsize=13, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 1.0 - i*0.65, line, ha='center', fontsize=11, color=ZH_COLORS['text'])
    for x in [3.8, 7.65]:
        ax.annotate('', xy=(x+0.05, 3.5), xytext=(x-0.35, 3.5), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    principle_box = FancyBboxPatch((0.5, 0.1), 11, 0.8, boxstyle="round,pad=0.1", facecolor='#1e3a5f', edgecolor=ZH_COLORS['blue'], linewidth=1.5)
    ax.add_patch(principle_box)
    ax.text(6, 0.5, '核心原则：默认禁止，只显式授予  |  没有明确授权 = 禁止访问', ha='center', fontsize=11, fontweight='bold', color=ZH_COLORS['blue'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_attack_path(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'IAM 特权升级攻击路径', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, '4步从普通用户到管理员', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    steps = [
        (0.3, 3.8, 2.4, 2.0, ZH_COLORS['red'], '① 初始入口', ['弱密码/钓鱼/漏洞', '拿到普通用户账号', '']),
        (3.2, 3.8, 2.4, 2.0, ZH_COLORS['orange'], '② 枚举权限', ['list-attached-', 'user-policies', '探测可用权限']),
        (6.1, 3.8, 2.4, 2.0, ZH_COLORS['orange'], '③ 权限组合', ['PassRole+RunInstances', 'CreateAccessKey', 'AttachUserPolicy']),
        (9.0, 3.8, 2.6, 2.0, ZH_COLORS['green'], '④ 持久化', ['创建后门账户', '修改IAM策略', '完全控制云账号']),
    ]
    for (x, y, w, h, color, title, lines) in steps:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor=color, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=color)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.8 - i*0.5, line, ha='center', fontsize=9, color=ZH_COLORS['text'])
    for i in range(3):
        x = steps[i][0] + steps[i][2]
        ax.annotate('', xy=(steps[i+1][0], 4.8), xytext=(x+0.05, 4.8), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    danger_box = FancyBboxPatch((0.3, 0.9), 11.4, 1.0, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor=ZH_COLORS['red'], linewidth=1.5)
    ax.add_patch(danger_box)
    ax.text(6, 1.65, '最危险的三个权限组合', ha='center', fontsize=11, fontweight='bold', color=ZH_COLORS['red'])
    ax.text(1.8, 1.2, 'PassRole+RunInstances', ha='center', fontsize=9, color=ZH_COLORS['red'])
    ax.text(5.5, 1.2, 'CreateAccessKey', ha='center', fontsize=9, color=ZH_COLORS['red'])
    ax.text(9.2, 1.2, 'AttachUserPolicy', ha='center', fontsize=9, color=ZH_COLORS['red'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_le_flow(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数计算流程', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, 'IAM权限图 → 辫群 → Burau表示 → 特征值 → LE', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    boxes = [
        (0.2, 2.8, 2.2, 2.5, '#dbeafe', ZH_COLORS['blue'], 'IAM权限图', ['节点: 用户/角色', '边: 权限关系', '边权重: 危险程度']),
        (3.0, 2.8, 2.2, 2.5, '#fce7f3', ZH_COLORS['red'], '辫群元素', ['权限链→σᵢ序列', 'σ₁·σ₂⁻¹·σ₃', '非阿贝尔结构']),
        (5.8, 2.8, 2.4, 2.5, '#dcfce7', ZH_COLORS['green'], 'Burau表示', ['→ n×n矩阵', '编码缠绕程度', 't变量记录交叉']),
        (8.7, 2.8, 2.2, 2.5, '#fef3c7', ZH_COLORS['orange'], '特征值', ['求矩阵特征值', '取最大模', 'max |λᵢ|']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in boxes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.85 - i*0.55, line, ha='center', fontsize=9, color=ZH_COLORS['text'])
    for i in range(3):
        x = boxes[i][0] + boxes[i][2]
        ax.annotate('', xy=(boxes[i+1][0], 4.05), xytext=(x+0.05, 4.05), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    le_box = FancyBboxPatch((8.7, 0.8), 2.2, 1.2, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=2.5)
    ax.add_patch(le_box)
    ax.text(9.8, 1.7, 'LE', ha='center', fontsize=20, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(9.8, 1.2, '= max|λᵢ|', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    ax.annotate('', xy=(9.8, 1.95), xytext=(9.8, 2.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['green'], lw=2))
    meaning_box = FancyBboxPatch((0.2, 0.3), 8.2, 1.5, boxstyle="round,pad=0.08", facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.5)
    ax.add_patch(meaning_box)
    ax.text(4.3, 1.55, 'LE 的物理含义', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['text'])
    high_box = FancyBboxPatch((0.5, 0.4), 3.5, 1.0, boxstyle="round,pad=0.05", facecolor='#fef2f2', edgecolor=ZH_COLORS['red'], linewidth=1.5)
    ax.add_patch(high_box)
    ax.text(2.25, 1.1, 'LE高 → 聚焦型', ha='center', fontsize=11, color=ZH_COLORS['red'], fontweight='bold')
    ax.text(2.25, 0.65, '少数关键节点掌握大量权限', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    low_box = FancyBboxPatch((4.5, 0.4), 3.5, 1.0, boxstyle="round,pad=0.05", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=1.5)
    ax.add_patch(low_box)
    ax.text(6.25, 1.1, 'LE低 → 分散型', ha='center', fontsize=11, color=ZH_COLORS['green'], fontweight='bold')
    ax.text(6.25, 0.65, '权限分散，无明显单点弱点', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_cross_domain(out_path):
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '跨域泛化：零调参的特权升级检测', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, '同构拓扑结构 -> 训练与部署无需适配', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    solar_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor=ZH_COLORS['blue'], linewidth=2.5)
    ax.add_patch(solar_box)
    ax.text(2.55, 4.7, 'AWS Solar', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(2.55, 4.2, '训练数据集', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(1.0, '#fef3c7', ZH_COLORS['orange']), (2.3, '#dbeafe', ZH_COLORS['blue']), (3.6, '#fce7f3', ZH_COLORS['red'])]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'U{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    ax.annotate('', xy=(5.2, 3.75), xytext=(4.8, 3.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    ax.text(5.0, 4.1, '提取\n拓扑特征', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    model_box = FancyBboxPatch((5.5, 2.8), 2.0, 1.8, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(6.5, 4.3, 'LE 模型', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(6.5, 3.85, 'Burau-\nLyapunov\n指数', ha='center', fontsize=10, color=ZH_COLORS['green'])
    ax.annotate('', xy=(8.2, 3.75), xytext=(7.5, 3.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    ax.text(7.85, 4.1, '直接\n部署', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    star_box = FancyBboxPatch((8.2, 2.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor=ZH_COLORS['orange'], linewidth=2.5)
    ax.add_patch(star_box)
    ax.text(9.95, 4.7, 'Stard Astro', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['orange'])
    ax.text(9.95, 4.2, '完全不同域', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(8.6, '#dcfce7', ZH_COLORS['green']), (9.6, '#fef3c7', ZH_COLORS['orange']), (10.6, '#dbeafe', ZH_COLORS['blue'])]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.5, 3.2, f'R{i+1}', ha='center', va='center', fontsize=10, fontweight='bold', color=ec)
    result_box = FancyBboxPatch((4.5, 0.5), 4.0, 1.5, boxstyle="round,pad=0.1", facecolor='#f1f5f9', edgecolor='#64748b', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(6.5, 1.75, '检测效果对比', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(5.3, 1.2, '训练集(Solar): AUC 0.92', ha='center', fontsize=10, color=ZH_COLORS['green'], fontweight='bold')
    ax.text(7.7, 1.2, '测试集(Stard): AUC 0.89', ha='center', fontsize=10, color=ZH_COLORS['green'], fontweight='bold')
    ax.text(6.5, 0.7, '无需调参，结构同构 -> 泛化能力强', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_cloud_graph(out_path):
    """场景1: 云平台 logo 变成一张密密麻麻的权限关系图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.5, '云平台 IAM 权限关系图', ha='center', fontsize=18, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.0, '用户、角色、服务账户之间的权限传递路径', ha='center', fontsize=11, color=ZH_COLORS['muted'])
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
                    arrowprops=dict(arrowstyle='->', color='#94a3b8', lw=1.5, alpha=0.7))
    for name, (x, y) in nodes.items():
        color = ZH_COLORS['red'] if name == 'Root' else ZH_COLORS['blue'] if name in ('Admin', 'Dev') else ZH_COLORS['green']
        circle = plt.Circle((x, y), 0.35, facecolor=color, edgecolor=ZH_COLORS['muted'], linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    ax.text(6, 0.8, '每条边 = 一条权限传递路径 = 黑客可能的提权链路', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_three_methods(out_path):
    """场景2: 三种方法的逐一图示"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '特权升级检测的三条路', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    methods = [
        (0.5, 3.0, 3.5, 2.8, '#fee2e2', ZH_COLORS['red'], '规则匹配', ['已知攻击签名', '特征码匹配', '局限：无法检测新招']),
        (4.3, 3.0, 3.5, 2.8, '#fef3c7', ZH_COLORS['orange'], '行为异常', ['统计正常行为', '检测统计偏离', '局限：可被模仿潜伏']),
        (8.1, 3.0, 3.5, 2.8, '#e0e7ff', '#3730a3', '手工图分析', ['人工定义规则', '专家知识驱动', '局限：大规模看不过来']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in methods:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=13, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 1.0 - i*0.6, line, ha='center', fontsize=11, color=ZH_COLORS['text'])
    ax.text(6, 0.5, '共同问题：在这套系统上训练的检测方法，换到另一套云环境还能用吗？', ha='center', fontsize=11, color=ZH_COLORS['red'], fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_graph_to_braid(out_path):
    """场景3: IAM 权限图 → 编织动画"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '权限路径 = 一根辫子', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, '交换相邻两个权限的位置 = 辫子的交叉动作 σᵢ', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    # 左边：权限图
    graph_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.8, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor=ZH_COLORS['blue'], linewidth=2)
    ax.add_patch(graph_box)
    ax.text(2.55, 5.0, 'IAM 权限图', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['blue'])
    nodes = [('A', 1.5, 4.2), ('B', 2.8, 4.2), ('C', 4.1, 4.2)]
    for name, x, y in nodes:
        circle = plt.Circle((x, y), 0.25, facecolor=ZH_COLORS['blue'], edgecolor=ZH_COLORS['blue'])
        ax.add_patch(circle)
        ax.text(x, y, name, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    coords = [(x, y) for _, x, y in nodes]
    for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['blue'], lw=2))
    ax.text(2.55, 2.85, '交换 A↔B 权限', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    ax.annotate('', xy=(6.3, 4.2), xytext=(5.5, 4.2), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=3))
    ax.text(5.9, 4.6, '映射', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    # 右边：辫子
    braid_box = FancyBboxPatch((6.5, 2.5), 5.0, 2.8, boxstyle="round,pad=0.1", facecolor='#fce7f3', edgecolor=ZH_COLORS['red'], linewidth=2)
    ax.add_patch(braid_box)
    ax.text(9, 5.0, '辫群元素 σᵢ', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
    t = np.linspace(0, 1, 200)
    colors = [ZH_COLORS['blue'], ZH_COLORS['red'], ZH_COLORS['green']]
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
    sigma_box = FancyBboxPatch((8.3, 2.7), 1.5, 0.7, boxstyle='round,pad=0.2', facecolor='#fce7f3', edgecolor=ZH_COLORS['red'], linewidth=2)
    ax.add_patch(sigma_box)
    ax.text(9.05, 3.05, 'σ₁', ha='center', fontsize=14, fontweight='bold', color=ZH_COLORS['red'])
    ax.text(9.0, 2.65, '非阿贝尔：σ₁σ₂ ≠ σ₂σ₁', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_burau_pipeline(out_path):
    """场景4: 辫群 → Burau表示 → 矩阵 → 特征值 → 数值"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数计算', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    steps = [
        (0.2, 2.8, 2.2, 2.5, '#dbeafe', ZH_COLORS['blue'], '辫群元素', ['σ₁·σ₂⁻¹·σ₃', '权限链序列']),
        (3.0, 2.8, 2.2, 2.5, '#fce7f3', ZH_COLORS['red'], 'Burau表示', ['→ n×n矩阵', 't变量记录缠绕']),
        (5.8, 2.8, 2.2, 2.5, '#dcfce7', ZH_COLORS['green'], '求特征值', ['|λ₁|, |λ₂|...', '取最大模']),
        (8.6, 2.8, 2.6, 2.5, '#fef3c7', ZH_COLORS['orange'], 'LE 指数', ['LE = max|λᵢ|', '量化危险程度']),
    ]
    for (x, y, w, h, fc, ec, title, lines) in steps:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, title, ha='center', fontsize=11, fontweight='bold', color=ec)
        for i, line in enumerate(lines):
            ax.text(x + w/2, y + h - 0.9 - i*0.6, line, ha='center', fontsize=10, color=ZH_COLORS['text'])
    for i in range(3):
        xi = steps[i][0] + steps[i][2]
        ax.annotate('', xy=(steps[i+1][0], 4.05), xytext=(xi+0.05, 4.05), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    le_box = FancyBboxPatch((8.6, 0.8), 2.6, 1.2, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=2.5)
    ax.add_patch(le_box)
    ax.text(9.9, 1.7, 'LE', ha='center', fontsize=20, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(9.9, 1.2, '= max|λᵢ|', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    ax.annotate('', xy=(9.9, 1.95), xytext=(9.9, 2.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['green'], lw=2))
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_abelian_proof(out_path):
    """场景5: 数学公式——不存在任何阿贝尔统计量能复制 LE 的区分能力"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.text(6, 7.4, '核心数学结论', ha='center', fontsize=18, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.9, '严格证明，非实验观察', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    # 聚焦型示意
    ax.text(2.5, 6.2, '聚焦型（LE高）', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
    for i, (x, c) in enumerate([(1.0, ZH_COLORS['red']), (2.0, '#d1d5db'), (3.0, '#d1d5db')]):
        circle = plt.Circle((x + 0.5, 5.4), 0.35, facecolor=c, edgecolor='#64748b', linewidth=1)
        ax.add_patch(circle)
    ax.annotate('', xy=(2.0, 5.4), xytext=(1.5, 5.4), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['red'], lw=2))
    ax.text(2.5, 4.7, '少数关键节点\n掌握大量权限', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    ax.text(2.5, 4.1, '均值=0.33  方差=0.11', ha='center', fontsize=9, color='#64748b')
    # 分散型示意
    ax.text(9.5, 6.2, '分散型（LE低）', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    for i, (x, c) in enumerate([(8.0, '#d1d5db'), (9.0, '#d1d5db'), (10.0, '#d1d5db'), (8.5, '#d1d5db'), (9.5, '#d1d5db'), (10.5, '#d1d5db')]):
        circle = plt.Circle((x, 5.4), 0.25, facecolor=c, edgecolor='#64748b', linewidth=1)
        ax.add_patch(circle)
    ax.text(9.5, 4.7, '权限分散各处\n无明显单点弱点', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    ax.text(9.5, 4.1, '均值=0.33  方差=0.09', ha='center', fontsize=9, color='#64748b')
    # 核心结论
    conclusion_box = FancyBboxPatch((0.8, 0.8), 10.4, 2.2, boxstyle="round,pad=0.1", facecolor='#1e3a5f', edgecolor=ZH_COLORS['blue'], linewidth=2)
    ax.add_patch(conclusion_box)
    ax.text(6, 2.7, '不存在任何阿贝尔统计量', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(6, 2.15, '能复制 LE 对"聚焦型"和"分散型"的区分能力', ha='center', fontsize=11, color=ZH_COLORS['blue'])
    ax.text(6, 1.55, '均值、方差、熵的任意组合均无法替代', ha='center', fontsize=11, color=ZH_COLORS['blue'])
    ax.text(6, 1.0, 'LE 测量的是非阿贝尔结构，无法被交换顺序不变量刻画', ha='center', fontsize=10, color=ZH_COLORS['blue'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_cross_domain_effect(out_path):
    """场景6: Solar训练 → 直接应用到Stard Astrophysics → 效果对比"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '跨域泛化效果', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, '拓扑同构 -> 零调参跨域检测', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    solar_box = FancyBboxPatch((0.3, 2.5), 4.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor=ZH_COLORS['blue'], linewidth=2.5)
    ax.add_patch(solar_box)
    ax.text(2.55, 4.7, 'AWS Solar', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(2.55, 4.2, '训练集', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(1.0, '#fef3c7', ZH_COLORS['orange']), (2.3, '#dbeafe', ZH_COLORS['blue']), (3.6, '#fce7f3', ZH_COLORS['red'])]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
    ax.annotate('', xy=(5.2, 3.75), xytext=(4.8, 3.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    ax.text(5.0, 4.1, '提取\n拓扑特征', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    model_box = FancyBboxPatch((5.5, 2.8), 2.0, 1.8, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(6.5, 4.3, 'LE 模型', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    ax.annotate('', xy=(8.2, 3.75), xytext=(7.5, 3.75), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    ax.text(7.85, 4.1, '直接部署', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    star_box = FancyBboxPatch((8.2, 2.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor=ZH_COLORS['orange'], linewidth=2.5)
    ax.add_patch(star_box)
    ax.text(9.95, 4.7, 'Stard Astro', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['orange'])
    ax.text(9.95, 4.2, '测试集（完全不同域）', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    for i, (x, fc, ec) in enumerate([(8.6, '#dcfce7', ZH_COLORS['green']), (9.6, '#fef3c7', ZH_COLORS['orange']), (10.6, '#dbeafe', ZH_COLORS['blue'])]):
        circle = plt.Circle((x + 0.5, 3.2), 0.35, facecolor=fc, edgecolor=ec, linewidth=2)
        ax.add_patch(circle)
    result_box = FancyBboxPatch((4.5, 0.5), 4.0, 1.5, boxstyle="round,pad=0.1", facecolor='#f1f5f9', edgecolor='#64748b', linewidth=1.5)
    ax.add_patch(result_box)
    ax.text(6.5, 1.75, '检测效果几乎不变', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(5.3, 1.2, '训练 AUC: 0.92', ha='center', fontsize=10, color=ZH_COLORS['green'], fontweight='bold')
    ax.text(7.7, 1.2, '测试 AUC: 0.89', ha='center', fontsize=10, color=ZH_COLORS['green'], fontweight='bold')
    ax.text(6.5, 0.7, '不需要调参 / 重训练 / 适配', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_attack_disperse(out_path):
    """场景7: LE升高 → 攻击者分散权限 → LE降低"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, '攻防博弈：LE 被反向利用', ha='center', fontsize=16, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.2, '攻击者知道 LE 计算方式后，可以刻意分散权限来隐藏攻击路径', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    # 攻击前
    ax.text(2.0, 5.5, '攻击前：LE 高', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
    for i, (x, c) in enumerate([(1.0, ZH_COLORS['red']), (2.0, '#d1d5db'), (3.0, '#d1d5db')]):
        circle = plt.Circle((x + 0.5, 4.7), 0.35, facecolor=c, edgecolor='#64748b', linewidth=1)
        ax.add_patch(circle)
    ax.text(2.0, 4.0, '少数节点\n掌握大量权限', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    ax.text(2.0, 3.4, 'LE = 0.87', ha='center', fontsize=11, fontweight='bold', color=ZH_COLORS['red'])
    # 箭头
    ax.annotate('', xy=(5.8, 4.7), xytext=(4.5, 4.7), arrowprops=dict(arrowstyle='->', color=ZH_COLORS['muted'], lw=2))
    ax.text(5.15, 5.0, '攻击者\n分散权限', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    # 攻击后
    ax.text(9.0, 5.5, '攻击后：LE 低', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    for i, (x, c) in enumerate([(7.5, '#d1d5db'), (8.5, '#d1d5db'), (9.5, '#d1d5db'), (10.5, '#d1d5db')]):
        circle = plt.Circle((x, 4.7), 0.3, facecolor=c, edgecolor='#64748b', linewidth=1)
        ax.add_patch(circle)
    ax.text(9.0, 4.0, '权限分散各处\n攻击路径被隐藏', ha='center', fontsize=9, color=ZH_COLORS['muted'])
    ax.text(9.0, 3.4, 'LE = 0.34', ha='center', fontsize=11, fontweight='bold', color=ZH_COLORS['green'])
    # 底部问题
    q_box = FancyBboxPatch((0.5, 0.8), 11, 1.2, boxstyle="round,pad=0.1", facecolor='#fef3c7', edgecolor=ZH_COLORS['orange'], linewidth=1.5)
    ax.add_patch(q_box)
    ax.text(6, 1.7, '新问题：给定安全级别约束，怎样分配权限才能让 LE 最小化？', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['orange'])
    ax.text(6, 1.1, '这是下一个研究方向', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_le_formula(out_path):
    """场景8: LE指数的核心公式"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.text(6, 6.6, 'Burau-Lyapunov 指数', ha='center', fontsize=18, fontweight='bold', color=ZH_COLORS['text'])
    ax.text(6, 6.1, '通过辫群的 Burau 表示，量化 IAM 图的结构复杂度', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    # 公式区
    formula_box = FancyBboxPatch((1.5, 3.5), 9.0, 2.0, boxstyle="round,pad=0.1", facecolor='#f1f5f9', edgecolor='#64748b', linewidth=2)
    ax.add_patch(formula_box)
    ax.text(6, 5.0, 'LE  =  max |λᵢ(B(σ))|', ha='center', fontsize=18, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(6, 4.3, 'B(σ) = Burau 表示矩阵（编码辫子缠绕程度）', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    ax.text(6, 3.8, 'λᵢ  =  B(σ) 的第 i 个特征值', ha='center', fontsize=11, color=ZH_COLORS['muted'])
    # 含义
    high_box = FancyBboxPatch((0.5, 1.2), 5.0, 1.5, boxstyle="round,pad=0.08", facecolor='#fef2f2', edgecolor=ZH_COLORS['red'], linewidth=1.5)
    ax.add_patch(high_box)
    ax.text(3.0, 2.35, 'LE 高 -> 聚焦型危险', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
    ax.text(3.0, 1.75, '少数关键节点掌握大量权限', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    ax.text(3.0, 1.3, '攻击者集中打这几个点', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    low_box = FancyBboxPatch((6.5, 1.2), 5.0, 1.5, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=1.5)
    ax.add_patch(low_box)
    ax.text(9.0, 2.35, 'LE 低 -> 分散型', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(9.0, 1.75, '权限分散，无明显单点弱点', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    ax.text(9.0, 1.3, '攻击路径难以发现', ha='center', fontsize=10, color=ZH_COLORS['muted'])
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()


# ─── 2604.02427 论文配图 ─────────────────────────────────

def draw_valley_cover(out_path, title):
    """场景1: 封面图 - 谷极化探测"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    # 背景渐变效果（用矩形模拟）
    bg = FancyBboxPatch((0, 0), 12, 8, boxstyle="square", facecolor='#f8fafc', edgecolor='none')
    ax.add_patch(bg)
    # 标题
    ax.text(6, 5.5, title, ha='center', va='center', fontsize=22, fontweight='bold', color='#1e3a5f', wrap=True)
    # 副标题
    ax.text(6, 4.2, 'van der Waals 材料中的谷极化态探测', ha='center', fontsize=14, color='#64748b')
    ax.text(6, 3.5, '热电效应 · 电流整流 · 零磁场', ha='center', fontsize=12, color='#94a3b8', style='italic')
    # 装饰线
    ax.plot([1.5, 10.5], [2.8, 2.8], color='#93c5fd', linewidth=1.5)
    ax.text(6, 1.5, 'arXiv: 2604.02427 | Ising 超导体与谷极化', ha='center', fontsize=10, color='#94a3b8')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

def draw_vdw_heterojunction(out_path, desc):
    """场景2: 范德瓦尔斯异质结示意图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[02] ' + desc, fontsize=11, color='#374151')
    # Ising超导体层
    ising = FancyBboxPatch((1, 4), 4, 1.5, boxstyle="round,pad=0.1", facecolor=ZH_COLORS['blue'], edgecolor=ZH_COLORS['blue'], linewidth=2)
    ax.add_patch(ising)
    ax.text(3, 4.75, 'Ising 超导体', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(3, 4.25, '强自旋轨道耦合', ha='center', fontsize=10, color=ZH_COLORS['blue'])
    # 范德瓦尔斯界面
    ax.annotate('', xy=(5.2, 4.75), xytext=(5, 4.75), arrowprops=dict(arrowstyle='<->', color='#64748b', lw=2))
    ax.text(5.1, 5.1, 'vdW', ha='center', fontsize=9, color='#64748b')
    # TMDC层
    tmdc = FancyBboxPatch((6, 4), 4.5, 1.5, boxstyle="round,pad=0.1", facecolor='#bbf7d0', edgecolor=ZH_COLORS['green'], linewidth=2)
    ax.add_patch(tmdc)
    ax.text(8.25, 4.75, 'TMDC / 谷极化材料', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(8.25, 4.25, 'MoSe2 / WS2 / 少层', ha='center', fontsize=10, color=ZH_COLORS['green'])
    # 谷符号
    ax.text(2, 2.5, '↑ spin', ha='center', fontsize=12, color=ZH_COLORS['blue'])
    ax.text(8, 2.5, "K / K_prime 谷", ha='center', fontsize=12, color=ZH_COLORS['green'])
    ax.plot([3, 7.5], [2, 2], 'k--', alpha=0.3)
    ax.text(5.25, 1.8, '谷自由度 ↔ 自旋自由度  拓扑关联', ha='center', fontsize=11, color='#64748b', style='italic')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_ising_tmdc_junction(out_path, desc):
    """场景3: Ising超导体与TMDC异质结 - 能带示意"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[03] ' + desc, fontsize=11, color='#374151')
    # 左侧 Ising
    ising_e = FancyBboxPatch((0.5, 3.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor=ZH_COLORS['blue'], linewidth=2)
    ax.add_patch(ising_e)
    ax.text(2.25, 5.0, 'Ising 超导体', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['blue'])
    ax.text(2.25, 4.4, '伊辛配对', ha='center', fontsize=11, color=ZH_COLORS['blue'])
    ax.text(2.25, 3.8, '↑↑ ↓↓ 自旋极化', ha='center', fontsize=10, color=ZH_COLORS['blue'])
    # 中间能带
    ax.plot([4.2, 4.2], [2.5, 6.5], color='#94a3b8', linewidth=2, linestyle='--')
    ax.plot([4.7, 4.7], [2.5, 6.5], color='#94a3b8', linewidth=2, linestyle='--')
    ax.text(4.45, 6.8, '界面', ha='center', fontsize=10, color='#64748b')
    # Andreev反射箭头
    ax.annotate('', xy=(4.5, 5.0), xytext=(4.0, 5.3), arrowprops=dict(arrowstyle='->', color='#ef4444', lw=2))
    ax.text(4.0, 5.6, 'Andreev', ha='center', fontsize=8, color='#ef4444')
    # 右侧 TMDC
    tmdc_e = FancyBboxPatch((6.5, 3.5), 4, 2.5, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor=ZH_COLORS['green'], linewidth=2)
    ax.add_patch(tmdc_e)
    ax.text(8.5, 5.0, 'TMDC', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['green'])
    ax.text(8.5, 4.4, "谷 K 与 K_prime", ha='center', fontsize=11, color=ZH_COLORS['green'])
    ax.text(8.5, 3.8, '谷极化态', ha='center', fontsize=10, color='#4ade80')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_thermoelectric(out_path, desc):
    """场景4: 热电效应示意图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[04] ' + desc, fontsize=11, color='#374151')
    # 温度梯度符号
    ax.text(1, 5.8, 'T_high', ha='center', fontsize=14, color='#ef4444', fontweight='bold')
    ax.text(1, 2.2, 'T_low', ha='center', fontsize=14, color=ZH_COLORS['blue'], fontweight='bold')
    ax.annotate('', xy=(1, 3), xytext=(1, 5.5), arrowprops=dict(arrowstyle='<->', color='#ef4444', lw=2))
    # 材料区域
    mat = FancyBboxPatch((2.5, 2.5), 5, 4, boxstyle="round,pad=0.2", facecolor='#f1f5f9', edgecolor='#64748b', linewidth=2)
    ax.add_patch(mat)
    ax.text(5, 5.5, 'Ising/TMDC 异质结', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['muted'])
    # 热电电压表
    ax.text(5, 4.2, 'ΔT', ha='center', fontsize=12, color='#ef4444', fontweight='bold')
    ax.annotate('', xy=(5, 3.8), xytext=(5, 4.6), arrowprops=dict(arrowstyle='->', color='#ef4444', lw=1.5))
    ax.text(5, 3.5, 'V_thermo', ha='center', fontsize=11, color=ZH_COLORS['blue'], fontweight='bold')
    # 说明文字
    result = FancyBboxPatch((8, 3.5), 3.5, 2, boxstyle="round,pad=0.1", facecolor='#fef9c3', edgecolor='#eab308', linewidth=1.5)
    ax.add_patch(result)
    ax.text(9.75, 5.0, '热电系数', ha='center', fontsize=11, fontweight='bold', color='#854d0e')
    ax.text(9.75, 4.3, '∝ 谷极化强度', ha='center', fontsize=11, color='#a16207')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_iv_curve(out_path, desc):
    """场景5: 电流整流 I-V 曲线"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[05] ' + desc, fontsize=11, color='#374151')
    # I-V 曲线示意
    # 非对称整流曲线
    v = [i/10 for i in range(-50, 51)]
    i_vals = [0.3*v_i + 0.05*v_i**2 for v_i in v]  # 非线性非对称
    ax.plot([i*20+6 for i in v], [i*2+4 for i in i_vals], color=ZH_COLORS['blue'], linewidth=2.5)
    ax.axhline(y=4, color='#d1d5db', linewidth=1, linestyle='--')
    ax.axvline(x=6, color='#d1d5db', linewidth=1, linestyle='--')
    ax.text(6, 2.0, 'V', ha='center', fontsize=12, color='#64748b')
    ax.text(10.5, 4, 'I', ha='center', fontsize=12, color='#64748b', rotation=90)
    # 整流标注
    ax.annotate('整流不对称', xy=(9, 5.5), xytext=(8, 6.5), fontsize=11, color=ZH_COLORS['red'],
                arrowprops=dict(arrowstyle='->', color=ZH_COLORS['red']))
    # 公式
    formula = FancyBboxPatch((0.5, 1.2), 4.5, 1.8, boxstyle="round,pad=0.1", facecolor='#fef2f2', edgecolor=ZH_COLORS['red'], linewidth=1.5)
    ax.add_patch(formula)
    ax.text(2.75, 2.5, 'R = (V/I) 非对称', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
    ax.text(2.75, 1.8, '整流系数 ∝ 谷极化', ha='center', fontsize=11, color='#7f1d1d')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()

def draw_band_structure(out_path, desc):
    """场景6: 能带结构与谷极化示意"""
    _draw_band_structure(out_path, desc, progress=1.0)


def _draw_band_structure(out_path, desc, progress=1.0):
    """能带结构（支持进度动画，0.0→1.0）"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[06] ' + desc, fontsize=11, color='#374151')

    # 谷极化程度随 progress 变化（0→max_split）
    max_split = 2.0
    split_frac = progress  # 0=无分裂, 1=最大分裂

    # K 谷（始终完整）
    ax.plot([1, 5], [3, 5], color=ZH_COLORS['green'], linewidth=2.5)
    # K' 谷随 progress 从中间分裂
    mid_y = 3.0
    kp_top = mid_y + (5 - mid_y) * split_frac
    kp_bot = mid_y - (mid_y - 1) * split_frac
    ax.plot([1, 5], [mid_y, kp_top if progress < 0.5 else kp_top],
            color=ZH_COLORS['blue'], linewidth=2.5,
            alpha=max(0.3, progress))
    if progress > 0.3:
        ax.plot([1, 5], [mid_y, kp_bot],
                color=ZH_COLORS['blue'], linewidth=2.5, linestyle='--',
                alpha=max(0.3, min(1, (progress - 0.3) / 0.3)))

    ax.text(1, 2.4, "K'", ha='center', fontsize=11, color=ZH_COLORS['blue'], fontweight='bold')
    ax.text(1, 5.2, "K", ha='center', fontsize=11, color=ZH_COLORS['green'], fontweight='bold')

    # 分裂标注随 progress 出现
    if progress > 0.5:
        split_h = (kp_top - kp_bot) * (progress - 0.5) / 0.5
        ax.annotate('', xy=(3.5, mid_y + split_h / 2 + 0.1), xytext=(3.5, mid_y - split_h / 2 - 0.1),
                    arrowprops=dict(arrowstyle='<->', color='#94a3b8', lw=1.5))
        ax.text(3.8, 3.0, "谷极化", ha='left', fontsize=9, color='#64748b')

    ax.text(2.5, 6.5, '谷极化态', ha='center', fontsize=14, fontweight='bold', color='#16a34a')
    ax.text(2.5, 5.8, '↑ 自旋', ha='center', fontsize=11, color=ZH_COLORS['green'])

    box = FancyBboxPatch((6.5, 2), 5, 4, boxstyle="round,pad=0.15", facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
    ax.add_patch(box)
    ax.text(9, 5.3, '谷极化探测结果', ha='center', fontsize=13, fontweight='bold', color=ZH_COLORS['green'])
    lines = ['热电效应 → 电压信号', '电流整流 → I-V 非对称', '零磁场下可分辨', '无需光学测量']
    for j, line in enumerate(lines):
        ax.text(7, 4.5 - j*0.65, '✓ ' + line, ha='left', fontsize=10, color=ZH_COLORS['muted'])

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
    plt.close()


def draw_iv_curve(out_path, desc):
    """场景5: 电流整流 I-V 曲线"""
    _draw_iv_curve(out_path, desc, progress=1.0)


def _draw_iv_curve(out_path, desc, progress=1.0):
    """I-V 曲线（支持进度动画）"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[05] ' + desc, fontsize=11, color='#374151')

    v = [i/10 for i in range(-50, 51)]
    i_vals = [0.3*v_i + 0.05*v_i**2 for v_i in v]

    # 随 progress 逐渐绘制曲线
    n_pts = max(2, int(len(v) * progress))
    pts_x = [i*20+6 for i in v[:n_pts]]
    pts_y = [i*2+4 for i in i_vals[:n_pts]]
    ax.plot(pts_x, pts_y, color=ZH_COLORS['blue'], linewidth=2.5)

    ax.axhline(y=4, color='#d1d5db', linewidth=1, linestyle='--')
    ax.axvline(x=6, color='#d1d5db', linewidth=1, linestyle='--')
    ax.text(6, 2.0, 'V', ha='center', fontsize=12, color='#64748b')
    ax.text(10.5, 4, 'I', ha='center', fontsize=12, color='#64748b', rotation=90)

    if progress > 0.6:
        ax.annotate('整流不对称', xy=(9, 5.5), xytext=(8, 6.5), fontsize=11, color=ZH_COLORS['red'],
                    arrowprops=dict(arrowstyle='->', color=ZH_COLORS['red']))

    if progress > 0.8:
        formula = FancyBboxPatch((0.5, 1.2), 4.5, 1.8, boxstyle="round,pad=0.1", facecolor='#fef2f2', edgecolor=ZH_COLORS['red'], linewidth=1.5)
        ax.add_patch(formula)
        ax.text(2.75, 2.5, 'R = (V/I) 非对称', ha='center', fontsize=12, fontweight='bold', color=ZH_COLORS['red'])
        ax.text(2.75, 1.8, '整流系数 ∝ 谷极化', ha='center', fontsize=11, color='#7f1d1d')

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor=ZH_COLORS['bg'])
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
    if '封面' in desc or '谷极化探测' in desc:
        return 'valley_cover'
    if '范德瓦' in desc or '异质结' in desc or 'TMDC' in desc:
        return 'vdw_heterojunction'
    if 'Ising' in desc and 'TMDC' in desc:
        return 'ising_tmdc_junction'
    if '热电' in desc:
        return 'thermoelectric'
    if '整流' in desc or 'I-V' in desc or '电流' in desc:
        return 'iv_curve'
    if '能带' in desc or '谷' in desc:
        return 'band_structure'
    return None

# ─── matplotlib dispatch helpers ─────────────────────────────
def _mpl_dispatch(key, func, out_path, desc, title):
    """matplotlib 渲染分发（保留原参数路由逻辑）"""
    if key == 'valley_cover':
        func(out_path, title or '')
    elif key in ('vdw_heterojunction', 'ising_tmdc_junction',
                  'thermoelectric', 'iv_curve', 'band_structure'):
        func(out_path, desc)
    else:
        func(out_path)


def _mpl_fallback(key, func, out_path, desc, title):
    """T2I 失败后的 matplotlib 回退"""
    print(f"  [MPL] T2I 回退 → {key}")
    _mpl_dispatch(key, func, out_path, desc, title)


# ─── T2I 场景描述 → prompt 映射 ────────────────────────────
# 9 个艺术/概念类场景可走 Stable Diffusion
T2I_SCENES = {
    'valley_cover':         'Minimalist cover image, bold white typography on clean background, academic journal cover style, no people',
    'vdw_heterojunction':    'Scientific diagram of van der Waals heterostructure, two layered 2D materials sandwiched together, electron orbitals, glowing purple and blue layers, clean white background, technical illustration style',
    'ising_tmdc_junction':  'Phase transition diagram between two 2D semiconductor materials, Ising model spins flipping from ordered to disordered state, red and blue arrows, clean scientific illustration on white background',
    'thermoelectric':        'Thermoelectric effect diagram, temperature gradient with hot and cold sides, electrons flowing, Seebeck coefficient visualization, scientific diagram on white background',
    'cloud_graph':           'Abstract graph visualization of cloud IAM permissions, nodes connected by curved edges, color-coded by sensitivity level, minimal scientific illustration, white background',
    'three_methods':         'Three parallel scientific methods diagrams side by side, numbered 1 2 3, clean minimal style, white background, technical illustration',
    'graph_to_braid':        'Mathematical transformation diagram, a network graph morphing into braided strands, group theory visualization, clean academic illustration on white background',
    'cross_domain_effect':   'Security vulnerability spreading across domains, interconnected spheres labeled with IAM concepts, arrows showing privilege escalation paths, minimal scientific diagram on white',
    'attack_disperse':       'Attack vector dispersal pattern, branching diagram from a single entry point to multiple targets, cybersecurity concept, clean minimal style on white background',
}

# matplotlib 保留场景（数据/公式类，精确控制无法用 T2I 替代）
# 仅包含 SCENE_DRAWERS 中实际注册的场景（与 T2I_SCENES 互斥）
MPL_ONLY_SCENES = {
    'iv_curve', 'band_structure', 'burau_pipeline',
    'abelian_proof', 'le_formula',
}


def draw_with_t2i(out_path: Path, scene_key: str, desc: str = None) -> bool:
    """用 Stable Diffusion 生成图片，失败则返回 False"""
    pipe = _get_sd_pipeline()
    if pipe is None:
        return False

    prompt = T2I_SCENES.get(scene_key, desc or scene_key)
    negative_prompt = (
        "photorealistic, photograph, 3D render, blurry, low quality, "
        "text overlay, watermark, logo, signature, deformed, ugly, "
        "nsfw, nude, violent"
    )

    import torch
    seed = int(hash(scene_key) % (2**31))
    generator = torch.Generator(
        device="cuda" if torch.cuda.is_available() else "cpu"
    ).manual_seed(seed)

    try:
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=25,
            guidance_scale=7.5,
            generator=generator,
            height=512,
            width=768,   # 3:2 ≈ 12:8
        )
        img = result.images[0]
        img.save(str(out_path))
        return True
    except Exception as e:
        print(f"  [SD] 生成失败: {e}")
        return False


SCENE_DRAWERS = {
    # 2604.02427 论文场景
    'valley_cover': draw_valley_cover,
    'vdw_heterojunction': draw_vdw_heterojunction,
    'ising_tmdc_junction': draw_ising_tmdc_junction,
    'thermoelectric': draw_thermoelectric,
    'iv_curve': draw_iv_curve,
    'band_structure': draw_band_structure,
    # 2602.02366 论文场景
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

def generate_scenes_for_script(script_path, output_prefix, article_name, strict=False, use_t2i=True):
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
    # T2I 优先路由
    t2i_routed = 0
    mpl_used = 0
    t2i_fallback = 0

    for i, desc in enumerate(scenes, 1):
        key = scene_to_key(desc)
        func = SCENE_DRAWERS.get(key)
        if func is None:
            print(f"  [SKIP] 场景{i} 无对应绘图函数: {desc[:30]}")
            continue
        out_path = output_dir / f"{output_prefix}-scene-{i:02d}.png"

        # ── 路由策略 ──
        if use_t2i and key in T2I_SCENES:
            # 优先 T2I，失败则回退 matplotlib
            sd_ok = draw_with_t2i(out_path, key, desc)
            if sd_ok:
                t2i_routed += 1
                print(f"  [SD]  场景{i}: {out_path.name}")
            else:
                t2i_fallback += 1
                _mpl_fallback(key, func, out_path, desc, title)
                mpl_used += 1
        elif key in MPL_ONLY_SCENES:
            # 数据/公式类，强制 matplotlib
            _mpl_dispatch(key, func, out_path, desc, title)
            mpl_used += 1
        else:
            # 兜底：按旧逻辑
            _mpl_dispatch(key, func, out_path, desc, title)
            mpl_used += 1

        if out_path.exists():
            # 生成 companion .scene.json（供 make_video.py 动画帧生成使用）
            import json
            scene_json = output_dir / f"{output_prefix}-scene-{i:02d}.scene.json"
            scene_json.write_text(json.dumps({'desc': desc, 'key': key}, ensure_ascii=False), encoding='utf-8')
            output_paths.append(out_path)
        else:
            print(f"  [SKIP] 场景{i} 文件未生成: {desc[:30]}")

    # 统计报告
    if t2i_routed or t2i_fallback:
        print(f"  [路由] T2I {t2i_routed} | T2I回退→MPL {t2i_fallback} | MPL {mpl_used}")
    return output_paths

if __name__ == '__main__':
    import os
    os.makedirs('video', exist_ok=True)

    parser = argparse.ArgumentParser(description="生成视频场景配图（SD 2.1 + matplotlib 混合）")
    parser.add_argument("script", nargs="?", help="视频脚本 .md 路径（不指定则处理所有）")
    parser.add_argument("--strict", action="store_true", help="有未覆盖场景时退出（返回码1）")
    parser.add_argument("--check-only", action="store_true", help="仅检查覆盖率，不生成图片")
    parser.add_argument("--no-t2i", action="store_true", help="禁用 T2I，全部用 matplotlib 渲染")
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
            generate_scenes_for_script(script, nn, article_name, use_t2i=not args.no_t2i)
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
                generate_scenes_for_script(script, nn, script.stem, use_t2i=not args.no_t2i)
