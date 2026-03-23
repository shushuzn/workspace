#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import fitz
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "D:/OpenClaw/workspace/10-ai-research/02-Models/_assets/2602.23958/2602.23958.pdf"
page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0

doc = fitz.open(pdf_path)
page = doc[page_num]
blocks = page.get_text("dict")["blocks"]

page_width = page.rect.width
center_x = page_width / 2

text_blocks = [b for b in blocks if b.get("type") == 0]

# 过滤显著块
min_height = page_width * 0.02
significant = []
for b in text_blocks:
    bbox = b["bbox"]
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if height > min_height and width > page_width * 0.05:
        significant.append({
            "center_x": (bbox[0] + bbox[2]) / 2,
            "width": width,
            "height": height,
            "y": bbox[1]
        })

print(f"Page {page_num +1}: {len(significant)} significant blocks")
print(f"Center X: {center_x}")
print()

left = [b for b in significant if b["center_x"] < center_x * 0.85]
right = [b for b in significant if b["center_x"] > center_x * 1.15]

print("Left blocks:")
for b in left:
    print(f"  W={b['width']:.1f} H={b['height']:.1f} Y={b['y']:.1f}")

print("\nRight blocks:")
for b in right:
    print(f"  W={b['width']:.1f} H={b['height']:.1f} Y={b['y']:.1f}")

if left:
    left_avg_h = sum(b["height"] for b in left) / len(left)
    print(f"\nLeft avg height: {left_avg_h:.1f}")

if right:
    right_avg_h = sum(b["height"] for b in right) / len(right)
    print(f"Right avg height: {right_avg_h:.1f}")

doc.close()
