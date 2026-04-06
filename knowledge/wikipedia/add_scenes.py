# Read draw_scene.py and add new scene functions + SCENE_DRAWERS entries
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\video\draw_scene.py', 'r', encoding='utf-8') as f:
    content = f.read()

# New scene functions to add before the main function section
NEW_FUNCS = '''
# ─── 2604.02427 论文配图 ─────────────────────────────────

def draw_valley_cover(out_path, title):
    """场景1: 封面图 - 谷极化探测"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    # 背景渐变效果（用矩形模拟）
    bg = FancyBboxPatch((0, 0), 12, 8, boxstyle="square", facecolor='#f0f4ff', edgecolor='none')
    ax.add_patch(bg)
    # 标题
    ax.text(6, 5.5, title, ha='center', va='center', fontsize=22, fontweight='bold', color='#1e3a5f', wrap=True)
    # 副标题
    ax.text(6, 4.2, 'van der Waals 材料中的谷极化态探测', ha='center', fontsize=14, color='#4a6fa5')
    ax.text(6, 3.5, '热电效应 · 电流整流 · 零磁场', ha='center', fontsize=12, color='#7a8fa8', style='italic')
    # 装饰线
    ax.plot([1.5, 10.5], [2.8, 2.8], color='#c5d4e8', linewidth=1.5)
    ax.text(6, 1.5, 'arXiv: 2604.02427 | Ising 超导体与谷极化', ha='center', fontsize=10, color='#94a3b8')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

def draw_vdw_heterojunction(out_path, desc):
    """场景2: 范德瓦尔斯异质结示意图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[02] ' + desc, fontsize=11, color='#444')
    # Ising超导体层
    ising = FancyBboxPatch((1, 4), 4, 1.5, boxstyle="round,pad=0.1", facecolor='#93c5fd', edgecolor='#3b82f6', linewidth=2)
    ax.add_patch(ising)
    ax.text(3, 4.75, 'Ising 超导体', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
    ax.text(3, 4.25, '强自旋轨道耦合', ha='center', fontsize=10, color='#3b82f6')
    # 范德瓦尔斯界面
    ax.annotate('', xy=(5.2, 4.75), xytext=(5, 4.75), arrowprops=dict(arrowstyle='<->', color='#6b7280', lw=2))
    ax.text(5.1, 5.1, 'vdW', ha='center', fontsize=9, color='#6b7280')
    # TMDC层
    tmdc = FancyBboxPatch((6, 4), 4.5, 1.5, boxstyle="round,pad=0.1", facecolor='#86efac', edgecolor='#22c55e', linewidth=2)
    ax.add_patch(tmdc)
    ax.text(8.25, 4.75, 'TMDC / 谷极化材料', ha='center', fontsize=13, fontweight='bold', color='#166534')
    ax.text(8.25, 4.25, 'MoSe2 / WS2 / 少层', ha='center', fontsize=10, color='#22c55e')
    # 谷符号
    ax.text(2, 2.5, '↑ spin', ha='center', fontsize=12, color='#3b82f6')
    ax.text(8, 2.5, 'K / K\' 谷', ha='center', fontsize=12, color='#22c55e')
    ax.plot([3, 7.5], [2, 2], 'k--', alpha=0.3)
    ax.text(5.25, 1.8, '谷自由度 ↔ 自旋自由度  拓扑关联', ha='center', fontsize=11, color='#6b7280', style='italic')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_ising_tmdc_junction(out_path, desc):
    """场景3: Ising超导体与TMDC异质结 - 能带示意"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[03] ' + desc, fontsize=11, color='#444')
    # 左侧 Ising
    ising_e = FancyBboxPatch((0.5, 3.5), 3.5, 2.5, boxstyle="round,pad=0.1", facecolor='#dbeafe', edgecolor='#3b82f6', linewidth=2)
    ax.add_patch(ising_e)
    ax.text(2.25, 5.0, 'Ising 超导体', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
    ax.text(2.25, 4.4, '伊辛配对', ha='center', fontsize=11, color='#3b82f6')
    ax.text(2.25, 3.8, '↑↑ ↓↓ 自旋极化', ha='center', fontsize=10, color='#60a5fa')
    # 中间能带
    ax.plot([4.2, 4.2], [2.5, 6.5], color='#9ca3af', linewidth=2, linestyle='--')
    ax.plot([4.7, 4.7], [2.5, 6.5], color='#9ca3af', linewidth=2, linestyle='--')
    ax.text(4.45, 6.8, '界面', ha='center', fontsize=10, color='#6b7280')
    # Andreev反射箭头
    ax.annotate('', xy=(4.5, 5.0), xytext=(4.0, 5.3), arrowprops=dict(arrowstyle='->', color='#ef4444', lw=2))
    ax.text(4.0, 5.6, 'Andreev', ha='center', fontsize=8, color='#ef4444')
    # 右侧 TMDC
    tmdc_e = FancyBboxPatch((6.5, 3.5), 4, 2.5, boxstyle="round,pad=0.1", facecolor='#dcfce7', edgecolor='#22c55e', linewidth=2)
    ax.add_patch(tmdc_e)
    ax.text(8.5, 5.0, 'TMDC', ha='center', fontsize=13, fontweight='bold', color='#166534')
    ax.text(8.5, 4.4, '谷 K 与 K\'', ha='center', fontsize=11, color='#22c55e')
    ax.text(8.5, 3.8, '谷极化态', ha='center', fontsize=10, color='#4ade80')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_thermoelectric(out_path, desc):
    """场景4: 热电效应示意图"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[04] ' + desc, fontsize=11, color='#444')
    # 温度梯度符号
    ax.text(1, 5.8, 'T_high', ha='center', fontsize=14, color='#ef4444', fontweight='bold')
    ax.text(1, 2.2, 'T_low', ha='center', fontsize=14, color='#3b82f6', fontweight='bold')
    ax.annotate('', xy=(1, 3), xytext=(1, 5.5), arrowprops=dict(arrowstyle='<->', color='#ef4444', lw=2))
    # 材料区域
    mat = FancyBboxPatch((2.5, 2.5), 5, 4, boxstyle="round,pad=0.2", facecolor='#f3f4f6', edgecolor='#6b7280', linewidth=2)
    ax.add_patch(mat)
    ax.text(5, 5.5, 'Ising/TMDC 异质结', ha='center', fontsize=13, fontweight='bold', color='#374151')
    # 热电电压表
    ax.text(5, 4.2, 'ΔT', ha='center', fontsize=12, color='#ef4444', fontweight='bold')
    ax.annotate('', xy=(5, 3.8), xytext=(5, 4.6), arrowprops=dict(arrowstyle='->', color='#ef4444', lw=1.5))
    ax.text(5, 3.5, 'V_thermo', ha='center', fontsize=11, color='#1e40af', fontweight='bold')
    # 说明文字
    result = FancyBboxPatch((8, 3.5), 3.5, 2, boxstyle="round,pad=0.1", facecolor='#fef9c3', edgecolor='#eab308', linewidth=1.5)
    ax.add_patch(result)
    ax.text(9.75, 5.0, '热电系数', ha='center', fontsize=11, fontweight='bold', color='#854d0e')
    ax.text(9.75, 4.3, '∝ 谷极化强度', ha='center', fontsize=11, color='#a16207')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_iv_curve(out_path, desc):
    """场景5: 电流整流 I-V 曲线"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[05] ' + desc, fontsize=11, color='#444')
    # I-V 曲线示意
    # 非对称整流曲线
    v = [i/10 for i in range(-50, 51)]
    i_vals = [0.3*v_i + 0.05*v_i**2 for v_i in v]  # 非线性非对称
    ax.plot([i*20+6 for i in v], [i*2+4 for i in i_vals], color='#3b82f6', linewidth=2.5)
    ax.axhline(y=4, color='#d1d5db', linewidth=1, linestyle='--')
    ax.axvline(x=6, color='#d1d5db', linewidth=1, linestyle='--')
    ax.text(6, 2.0, 'V', ha='center', fontsize=12, color='#6b7280')
    ax.text(10.5, 4, 'I', ha='center', fontsize=12, color='#6b7280', rotation=90)
    # 整流标注
    ax.annotate('整流不对称', xy=(9, 5.5), xytext=(8, 6.5), fontsize=11, color='#dc2626',
                arrowprops=dict(arrowstyle='->', color='#dc2626'))
    # 公式
    formula = FancyBboxPatch((0.5, 1.2), 4.5, 1.8, boxstyle="round,pad=0.1", facecolor='#fef2f2', edgecolor='#dc2626', linewidth=1.5)
    ax.add_patch(formula)
    ax.text(2.75, 2.5, 'R = (V/I) 非对称', ha='center', fontsize=12, fontweight='bold', color='#dc2626')
    ax.text(2.75, 1.8, '整流系数 ∝ 谷极化', ha='center', fontsize=11, color='#7f1d1d')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

def draw_band_structure(out_path, desc):
    """场景6: 能带结构与谷极化示意"""
    fig, ax = new_fig((12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8)
    ax.axis('off')
    ax.text(0.5, 7.5, '[06] ' + desc, fontsize=11, color='#444')
    # 能带示意 - K谷
    ax.plot([1, 5], [3, 5], color='#22c55e', linewidth=2.5, label='K 谷')
    ax.plot([1, 5], [3, 1], color='#3b82f6', linewidth=2.5, label='K\' 谷')
    ax.text(1, 2.4, 'K\'', ha='center', fontsize=11, color='#3b82f6', fontweight='bold')
    ax.text(1, 5.2, 'K', ha='center', fontsize=11, color='#22c55e', fontweight='bold')
    # 谷极化分裂
    ax.annotate('', xy=(3.5, 4.2), xytext=(3.5, 1.8), arrowprops=dict(arrowstyle='<->', color='#9ca3af', lw=1.5))
    ax.text(3.8, 3.0, '谷\n极化', ha='left', fontsize=9, color='#6b7280')
    # 谷极化标签
    ax.text(2.5, 6.5, '谷极化态', ha='center', fontsize=14, fontweight='bold', color='#16a34a')
    ax.text(2.5, 5.8, '↑ 自旋', ha='center', fontsize=11, color='#22c55e')
    # 右侧说明
    box = FancyBboxPatch((6.5, 2), 5, 4, boxstyle="round,pad=0.15", facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=2)
    ax.add_patch(box)
    ax.text(9, 5.3, '谷极化探测结果', ha='center', fontsize=13, fontweight='bold', color='#166534')
    lines = ['热电效应 → 电压信号', '电流整流 → I-V 非对称', '零磁场下可分辨', '无需光学测量']
    for j, line in enumerate(lines):
        ax.text(7, 4.5 - j*0.65, '✓ ' + line, ha='left', fontsize=10, color='#374151')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()

'''

# Insert new functions before the main function section
main_marker = '# ─── 主函数：从脚本提取场景并生成 ────────────────────────────'
content = content.replace(main_marker, NEW_FUNCS + main_marker)

# Update SCENE_DRAWERS to include new entries
old_drawers = """SCENE_DRAWERS = {
    'cloud_graph': draw_cloud_graph,
    'three_methods': draw_three_methods,
    'graph_to_braid': draw_graph_to_braid,
    'burau_pipeline': draw_burau_pipeline,
    'abelian_proof': draw_abelian_proof,
    'cross_domain_effect': draw_cross_domain_effect,
    'attack_disperse': draw_attack_disperse,
    'le_formula': draw_le_formula,
}"""

new_drawers = """SCENE_DRAWERS = {
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
}"""

content = content.replace(old_drawers, new_drawers)

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\video\draw_scene.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added 6 new draw functions and updated SCENE_DRAWERS")
