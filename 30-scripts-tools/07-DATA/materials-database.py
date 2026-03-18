#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materials Database v1
材料科学数据库连接模块
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

class MaterialsDatabase:
    """材料科学数据库"""
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.mongodb_db = os.getenv("MONGODB_DB_NAME", "materials_db")
        self.client = None
        self.db = None
        self.connected = False
    
    def connect(self) -> bool:
        """连接数据库"""
        if not MONGODB_AVAILABLE:
            print("❌ pymongo 未安装，请运行：pip install pymongo")
            return False
        
        try:
            self.client = MongoClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            
            # 测试连接
            self.client.admin.command('ping')
            
            self.db = self.client[self.mongodb_db]
            self.connected = True
            
            print(f"✅ MongoDB 连接成功：{self.mongodb_db}")
            return True
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB 连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.connected = False
            print("✅ MongoDB 连接已关闭")
    
    def insert_material(self, material: Dict) -> Optional[str]:
        """插入材料数据"""
        if not self.connected:
            if not self.connect():
                return None
        
        collection = self.db['materials']
        material['created_at'] = datetime.now().isoformat()
        material['updated_at'] = datetime.now().isoformat()
        
        result = collection.insert_one(material)
        return str(result.inserted_id)
    
    def find_materials(self, query: Dict = None, limit: int = 10) -> List[Dict]:
        """查询材料"""
        if not self.connected:
            if not self.connect():
                return []
        
        collection = self.db['materials']
        query = query or {}
        
        results = list(collection.find(query).limit(limit))
        
        # 转换 ObjectId 为字符串
        for doc in results:
            doc['_id'] = str(doc['_id'])
        
        return results
    
    def update_material(self, material_id: str, updates: Dict) -> bool:
        """更新材料"""
        if not self.connected:
            if not self.connect():
                return False
        
        collection = self.db['materials']
        updates['updated_at'] = datetime.now().isoformat()
        
        result = collection.update_one(
            {'_id': material_id},
            {'$set': updates}
        )
        
        return result.modified_count > 0
    
    def delete_material(self, material_id: str) -> bool:
        """删除材料"""
        if not self.connected:
            if not self.connect():
                return False
        
        collection = self.db['materials']
        result = collection.delete_one({'_id': material_id})
        
        return result.deleted_count > 0
    
    def get_stats(self) -> Dict:
        """获取数据库统计"""
        if not self.connected:
            if not self.connect():
                return {}
        
        stats = {}
        for collection_name in self.db.list_collection_names():
            collection = self.db[collection_name]
            stats[collection_name] = collection.count_documents({})
        
        return stats
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

def demo():
    """演示使用"""
    print("=" * 60)
    print("Materials Database v1 Demo")
    print("=" * 60)
    
    # 使用上下文管理器
    with MaterialsDatabase() as db:
        if not db.connected:
            print("\n⚠️ 数据库未连接，使用模拟数据演示")
            
            # 模拟数据
            print("\n📊 模拟数据:")
            materials = [
                {"formula": "LiCoO2", "band_gap": 2.5},
                {"formula": "LiFePO4", "band_gap": 3.2},
                {"formula": "Si", "band_gap": 1.1},
            ]
            for mat in materials:
                print(f"  - {mat['formula']}: {mat['band_gap']} eV")
            
            return
        
        # 获取统计
        stats = db.get_stats()
        print(f"\n📊 数据库统计:")
        for collection, count in stats.items():
            print(f"  {collection}: {count} 个文档")
        
        # 插入示例数据
        print(f"\n📝 插入示例数据...")
        material = {
            "formula": "LiCoO2",
            "band_gap": 2.5,
            "formation_energy": -2.1,
            "space_group": "R-3m"
        }
        material_id = db.insert_material(material)
        if material_id:
            print(f"✅ 插入成功：{material_id}")
        
        # 查询数据
        print(f"\n🔍 查询材料...")
        materials = db.find_materials(limit=5)
        for mat in materials:
            print(f"  - {mat.get('formula', 'N/A')}: {mat.get('band_gap', 'N/A')} eV")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
