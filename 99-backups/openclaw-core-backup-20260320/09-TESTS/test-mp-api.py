#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Materials Project API
测试 API 连接
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("=" * 60)
print("Materials Project API Connection Test")
print("=" * 60)

# 检查 API Key
api_key = os.getenv("MP_API_KEY")
if api_key:
    print(f"\n✅ API Key 已配置")
    print(f"   Key: {api_key[:10]}...{api_key[-5:]}")
else:
    print(f"\n❌ API Key 未配置")
    print(f"   请检查 .env 文件")
    exit(1)

# 测试导入
try:
    from materials_project_api import MaterialsProjectClient
    print(f"\n✅ 模块导入成功")
except Exception as e:
    print(f"\n❌ 模块导入失败：{e}")
    exit(1)

# 测试连接
try:
    client = MaterialsProjectClient()
    print(f"\n✅ 客户端初始化成功")
    print(f"   Base URL: {client.base_url}")
except Exception as e:
    print(f"\n❌ 客户端初始化失败：{e}")
    exit(1)

# 测试搜索 (限流保护，仅测试)
try:
    print(f"\n🔍 测试搜索 LiCoO2...")
    # materials = client.search_materials(formula="LiCoO2", limit=1)
    # if materials:
    #     print(f"✅ 搜索成功，找到 {len(materials)} 个材料")
    # else:
    #     print(f"⚠️ 未找到材料")
    print(f"   (跳过实际请求，避免消耗配额)")
except Exception as e:
    print(f"\n❌ 搜索失败：{e}")

print("\n" + "=" * 60)
print("✅ 配置验证完成！")
print("=" * 60)
print("\n下一步:")
print("1. 运行 materials-project-api.py 测试完整功能")
print("2. 更新 API 服务使用真实数据")
print("3. 监控 API 配额使用情况")
