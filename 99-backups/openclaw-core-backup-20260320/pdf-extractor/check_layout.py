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
            "height": height
        })

print(f"Page {page_num +1}: {len(significant)} significant blocks")
print(f"Center X: {center_x}")
print()

left = [b for b in significant if b["center_x"] < center_x * 0.85]
right = [b for b in significant if b["center_x"] > center_x * 1.15]

print(f"Left blocks: {len(left)}")
print(f"Right blocks: {len(right)}")

if left:
    left_avg = sum(b["width"] for b in left) / len(left)
    print(f"Left avg width: {left_avg:.1f} ({left_avg /page_width:.2f})")

if right:
    right_avg = sum(b["width"] for b in right) / len(right)
    print(f"Right avg width: {right_avg:.1f} ({right_avg /page_width:.2f})")

    if left:
        ratio = right_avg / left_avg
        print(f"Width ratio (R/L): {ratio:.2f}")

doc.close()
