#!/usr/bin/env python3
"""
Figure 1: Graphical Abstract - Research Pathway Diagram
Figure 1: 研究路径图

Journal: Nature Communications
Dimensions: 1200x800 px (300 dpi)
Format: TIFF + SVG + PNG
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Arrow
import numpy as np
from matplotlib.font_manager import FontProperties

# Set style
plt.style.use('default')
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5

# Create figure
fig = plt.figure(figsize=(16, 10.67), dpi=300)  # 1200x800 px at 300 dpi
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1200)
ax.set_ylim(0, 800)
ax.axis('off')

# Color scheme
colors = {
    'primary': '#2E86AB',      # Blue - Prediction/Design
    'secondary': '#A23B72',    # Purple - Graph/Deployment
    'accent': '#F18F01',       # Orange - Composite/Experimental
    'background': '#FFFFFF',
    'text': '#333333',
    'success': '#26A69A',
    'peak': '#FF5722'
}

# Background
ax.set_facecolor(colors['background'])

# Title
title_text = "Machine Learning-Guided Design of Multi-Component CNT-LIG Composites"
ax.text(600, 760, title_text, fontsize=16, fontweight='bold',
        ha='center', va='top', color=colors['text'], fontfamily='Arial')

subtitle_text = "Complete Closed-Loop Research Framework (Completed in ~2 hours)"
ax.text(600, 730, subtitle_text, fontsize=11, fontstyle='italic',
        ha='center', va='top', color='#666666', fontfamily='Arial')

# Research phases (6 phases in circular layout)
phases = [
    {
        'title': 'Phase 1: Prediction',
        'title_zh': '阶段 1: 预测',
        'time': '12:17-12:30',
        'items': ['CNT Prediction (R²=0.799)', 'CNT vs LIG (11 dimensions)'],
        'color': colors['primary'],
        'position': (200, 400)
    },
    {
        'title': 'Phase 2: Knowledge Graph',
        'title_zh': '阶段 2: 知识图谱',
        'time': '12:30-12:45',
        'items': ['26 entities', '360 relationships', 'HTML visualization'],
        'color': colors['secondary'],
        'position': (400, 200)
    },
    {
        'title': 'Phase 3: Composites ⭐',
        'title_zh': '阶段 3: 复合材料 ⭐',
        'time': '12:45-13:22',
        'items': ['Binary (1.29×)', 'Ternary (1.67×)', 'Quaternary (2.40×) ★', 'Quinary (1.78×)'],
        'color': colors['accent'],
        'position': (800, 200)
    },
    {
        'title': 'Phase 4: Intelligent Design',
        'title_zh': '阶段 4: 智能设计',
        'time': '13:22-13:50',
        'items': ['Inverse Design (407 samples)', 'Active Learning (1000 candidates)'],
        'color': colors['primary'],
        'position': (1000, 400)
    },
    {
        'title': 'Phase 5: Deployment',
        'title_zh': '阶段 5: 部署',
        'time': '13:50-14:05',
        'items': ['Knowledge Distillation (100×)', 'Python Package', 'Docker'],
        'color': colors['secondary'],
        'position': (800, 600)
    },
    {
        'title': 'Phase 6: Validation',
        'title_zh': '阶段 6: 验证',
        'time': '14:05-14:23',
        'items': ['3 Standardized SOPs', 'Automated Feedback', 'Model Auto-Update'],
        'color': colors['accent'],
        'position': (400, 600)
    }
]

# Draw phase boxes
for i, phase in enumerate(phases):
    x, y = phase['position']

    # Box
    box = FancyBboxPatch((x -130, y -80), 260, 160,
                         boxstyle='round,pad=10,rounding_size=15',
                         linewidth=2.5, edgecolor=phase['color'],
                         facecolor=phase['color'] + '20',  # 20% opacity
                         zorder=2)
    ax.add_patch(box)

    # Phase number
    circle = Circle((x -110, y +60), 18, color=phase['color'], zorder=3)
    ax.add_patch(circle)
    ax.text(x -110, y +60, str(i +1), fontsize=11, fontweight='bold',
            color='white', ha='center', va='center', zorder=4)

    # Title
    ax.text(x -80, y +65, phase['title'], fontsize=11, fontweight='bold',
            color=phase['color'], ha='left', va='top', fontfamily='Arial')

    # Time
    ax.text(x +110, y +65, phase['time'], fontsize=9, fontstyle='italic',
            color='#666666', ha='right', va='top', fontfamily='Arial')

    # Items
    for j, item in enumerate(phase['items']):
        y_pos = y + 35 - j * 35
        marker_color = colors['peak'] if '★' in item or '2.40' in item else phase['color']
        ax.text(x -105, y_pos, '●', fontsize=8, color=marker_color,
                ha='left', va='center', fontfamily='Arial')
        ax.text(x -95, y_pos, item, fontsize=9, color=colors['text'],
                ha='left', va='center', fontfamily='Arial')

# Draw arrows (circular flow)
arrow_positions = [
    ((330, 400), (400, 320)),   # Phase 1 → 2
    ((530, 200), (670, 200)),   # Phase 2 → 3
    ((930, 280), (1000, 360)),  # Phase 3 → 4
    ((1000, 520), (930, 600)),  # Phase 4 → 5
    ((670, 600), (530, 600)),   # Phase 5 → 6
    ((270, 520), (200, 440)),   # Phase 6 → 1 (feedback)
]

for (start, end) in arrow_positions:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle='->', color=colors['primary'],
                               lw=2.5, mutation_scale=20),
                zorder=1)

# Central highlight box (Key Metrics)
center_box = FancyBboxPatch((450, 320), 300, 160,
                            boxstyle='round,pad=15,rounding_size=20',
                            linewidth=3, edgecolor=colors['peak'],
                            facecolor=colors['peak'] + '15',
                            zorder=5)
ax.add_patch(center_box)

# Key metrics
metrics_y = [450, 420, 390, 360]
metrics = [
    ('📊', '1000+ Samples', '6 Datasets'),
    ('🤖', '10 ML Models', 'R² 0.75-0.90+'),
    ('🏆', 'Peak Synergy 2.40×', 'Quaternary System'),
    ('⚡', '8.61×10⁵ S/m', 'Max Conductivity')
]

for i, (icon, text1, text2) in enumerate(metrics):
    y_pos = metrics_y[i]
    ax.text(470, y_pos, icon, fontsize=14, ha='left', va='center')
    ax.text(500, y_pos +3, text1, fontsize=10, fontweight='bold',
            color=colors['text'], ha='left', va='bottom', fontfamily='Arial')
    ax.text(500, y_pos -8, text2, fontsize=9, color='#666666',
            ha='left', va='top', fontfamily='Arial')

# Bottom footer
footer_text = "Closed-Loop: Prediction → Design → Screening → Deployment → Validation → Feedback (Auto-Update)"
ax.text(600, 40, footer_text, fontsize=9, fontstyle='italic',
        ha='center', va='center', color='#666666', fontfamily='Arial')

# Add DOI placeholder
ax.text(600, 20, 'DOI: [pending] | GitHub: github.com/your-org/cnt-materials-ml | PyPI: cnt-materials-ml',
        fontsize=8, ha='center', va='center', color='#999999', fontfamily='Arial')

# Save figure
plt.savefig('Figure_1_Graphical_Abstract.png', dpi=300, bbox_inches='tight')
plt.savefig('Figure_1_Graphical_Abstract.svg', format='svg', bbox_inches='tight')
plt.savefig('Figure_1_Graphical_Abstract.tiff', dpi=300, compression='tiff_lzw', bbox_inches='tight')

print("✓ Figure 1 saved: PNG, SVG, TIFF (300 dpi)")
print("  Dimensions: 1200x800 px")
print("  Ready for Nature Communications submission")
