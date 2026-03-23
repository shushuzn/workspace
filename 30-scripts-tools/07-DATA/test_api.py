#!/usr/bin/env python3
# test_api.py - OpenClaw API 完整测试脚本

import requests
import json

base = 'http://127.0.0.1:8000'

print('=' *60)
print('OpenClaw API 完整测试')
print('=' *60)

# 测试 1: 健康检查
print('\n1. 健康检查...')
r = requests.get(f'{base}/api/v1/health')
print(f'   状态：{r.status_code}')
print(f'   响应：{r.json()}')

# 测试 2: PDF 提取
print('\n2. PDF 提取...')
r = requests.post(f'{base}/api/v1/pdf/extract', json={
    'file_path': 'D:/OpenClaw/workspace/90-archive/PDFs/2026-03/2602.23373.pdf',
    'max_pages': 3
})
print(f'   状态：{r.status_code}')
data = r.json()
print(f'   成功：{data["success"]}')
print(f'   时间：{data["processing_time"]:.2f}s')

# 测试 3: 图表增强
print('\n3. 图表增强...')
r = requests.post(f'{base}/api/v1/figure/enhance', json={
    'image_path': 'D:/OpenClaw/workspace/11-research/cnt-research/figures/active_learning_best_conductivity.png'
})
print(f'   状态：{r.status_code}')
data = r.json()
print(f'   成功：{data["success"]}')
print(f'   时间：{data["processing_time"]:.2f}s')
if data.get('data'):
    print(f'   建议：{data["data"].get("recommendation", "N/A")}')

# 测试 4: 每日简报
print('\n4. 每日简报...')
r = requests.post(f'{base}/api/v1/brief/generate', json={'date': '2026-03-10'})
print(f'   状态：{r.status_code}')
data = r.json()
print(f'   成功：{data["success"]}')
print(f'   时间：{data["processing_time"]:.2f}s')

print('\n' + '=' *60)
print('[OK] 所有端点测试完成!')
print('=' *60)
