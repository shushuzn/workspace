with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\video\draw_scene.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes = {
    533: ("    ax.text(8, 2.5, 'K / K' 谷', ha='center', fontsize=12, color='#22c55e')\n",
           '    ax.text(8, 2.5, "K / K_prime 谷", ha=\'center\', fontsize=12, color=\'#22c55e\')\n'),
    563: ("    ax.text(8.5, 4.4, '谷 K 与 K'', ha='center', fontsize=11, color='#22c55e')\n",
           '    ax.text(8.5, 4.4, "谷 K 与 K_prime", ha=\'center\', fontsize=11, color=\'#22c55e\')\n'),
    636: ('    ax.text(3.8, 3.0, \'谷极化\', ha=\'left\', fontsize=9, color=\'#6b7280\')\n',
           '    ax.text(3.8, 3.0, "谷极化", ha=\'left\', fontsize=9, color=\'#6b7280\')\n'),
    633: ("    ax.text(1, 5.2, 'K', ha='center', fontsize=11, color='#22c55e', fontweight='bold')\n",
           '    ax.text(1, 5.2, "K", ha=\'center\', fontsize=11, color=\'#22c55e\', fontweight=\'bold\')\n'),
}
for lineno, (old, new) in fixes.items():
    if lines[lineno-1] == old:
        lines[lineno-1] = new
        print(f"Fixed line {lineno}")
    else:
        print(f"Line {lineno} mismatch, has: {repr(lines[lineno-1][:60])}")

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\video\draw_scene.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Done")
