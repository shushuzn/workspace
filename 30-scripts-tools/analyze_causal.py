#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze causal_inference_engine.py"""
import os
import sys

# Ensure UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

with open('causal_inference_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
empty_lines = sum(1 for l in lines if l.strip() == '')
long_lines = sum(1 for l in lines if len(l.rstrip()) > 120)
trailing = sum(1 for l in lines if l.rstrip() != l.rstrip('\n').rstrip())

print(f"Total: {total_lines}")
print(f"Empty: {empty_lines}")
print(f"Long (>120): {long_lines}")
print(f"Trailing: {trailing}")
print(f"Code: {total_lines - empty_lines}")
