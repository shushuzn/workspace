#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB Connection Test
测试 MongoDB 连接
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("=" * 60)
print("MongoDB Connection Test")
print("=" * 60)

# 检查配置
mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
mongodb_db = os.getenv("MONGODB_DB_NAME", "materials_db")

print(f"\n📊 MongoDB 配置:")
print(f"   URL: {mongodb_url}")
print(f"   Database: {mongodb_db}")

# 测试 pymongo 导入
try:
    from pymongo import MongoClient
    print(f"\n✅ pymongo 模块已安装")
except ImportError:
    print(f"\n❌ pymongo 模块未安装")
    print(f"   请运行：pip install pymongo")
    exit(1)

# 测试连接
try:
    print(f"\n🔌 测试连接 MongoDB...")
    client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
    
    # 测试连接
    client.admin.command('ping')
    
    # 获取数据库信息
    db = client[mongodb_db]
    collections = db.list_collection_names()
    
    print(f"\n✅ MongoDB 连接成功!")
    print(f"   服务器：{client.address}")
    print(f"   数据库：{mongodb_db}")
    print(f"   集合数：{len(collections)}")
    
    if collections:
        print(f"   集合列表：{', '.join(collections[:5])}")
    
    client.close()
    
except Exception as e:
    print(f"\n⚠️ MongoDB 连接失败:")
    print(f"   {e}")
    print(f"\n💡 解决方案:")
    print(f"   1. 确保 MongoDB 服务已启动")
    print(f"   2. 检查 MONGODB_URL 配置")
    print(f"   3. 检查防火墙设置")
    print(f"   4. 使用 Docker 运行 MongoDB:")
    print(f"      docker run -d -p 27017:27017 --name mongodb mongo:7.0")

print("\n" + "=" * 60)
print("配置验证完成！")
print("=" * 60)
print("\n下一步:")
print("1. 创建数据库连接模块 (materials-database.py)")
print("2. 更新 API 服务使用 MongoDB")
print("3. 添加数据持久化功能")
