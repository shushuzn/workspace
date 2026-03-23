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

print(f"PDF: {pdf_path}")
print(f"Total blocks: {len(blocks)}")

text_blocks = [b for b in blocks if b.get("type") == 0]
print(f"Text blocks: {len(text_blocks)}")

page_width = page.rect.width
page_height = page.rect.height
center_x = page_width / 2

print(f"Page size: {page_width} x {page_height}")
print(f"Center X: {center_x}")
print()

print("First 15 text blocks:")
print("-" * 80)

wide_blocks = 0
narrow_blocks = 0

for i, b in enumerate(text_blocks[:15]):
    bbox = b["bbox"]
    center_x_block = (bbox[0] + bbox[2]) / 2
    width = bbox[2] - bbox[0]
    width_ratio = width / page_width

    if width_ratio > 0.5:
        wide_blocks += 1
    else:
        narrow_blocks += 1

    text_preview = ""
    for line in b.get("lines", [])[:1]:
        for span in line.get("spans", []):
            text_preview += span.get("text", "")[:40]

    print(f"#{i:2d}: X={bbox[0]:6.1f}-{bbox[2]:6.1f} Ctr={center_x_block:6.1f} W={width:6.1f} ({width_ratio:.2f}) Y={bbox[1]:6.1f} | {text_preview}")

print()
print(f"Wide blocks (>50%): {wide_blocks}")
print(f"Narrow blocks: {narrow_blocks}")

doc.close()
