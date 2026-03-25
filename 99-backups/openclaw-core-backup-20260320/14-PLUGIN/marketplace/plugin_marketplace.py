#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Marketplace
插件市场系统
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional

class PluginMarketplace:
    """插件市场"""

    def __init__(self, registry_url='https://plugins.example.com'):
        self.registry_url = registry_url
        self.plugins_dir = Path('plugins')
        self.registry_file = self.plugins_dir / 'registry.json'

    def register_plugin(self, name: str, version: str, description: str, author: str) -> Dict:
        """注册插件"""
        plugin_info = {
            'name': name,
            'version': version,
            'description': description,
            'author': author,
            'downloads': 0,
            'rating': 0.0
        }

        # 保存到本地注册表
        registry = self.load_registry()
        registry['plugins'].append(plugin_info)
        self.save_registry(registry)

        return plugin_info

    def load_registry(self) -> Dict:
        """加载插件注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {'plugins': []}

    def save_registry(self, registry: Dict):
        """保存插件注册表"""
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)

    def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        registry = self.load_registry()
        return registry.get('plugins', [])

    def search_plugins(self, query: str) -> List[Dict]:
        """搜索插件"""
        plugins = self.list_plugins()
        return [
            p for p in plugins
            if query.lower() in p['name'].lower() or query.lower() in p['description'].lower()
        ]

    def install_plugin(self, name: str) -> bool:
        """安装插件"""
        # 从注册表查找插件
        registry = self.load_registry()
        plugin = next((p for p in registry['plugins'] if p['name'] == name), None)

        if not plugin:
            print(f"插件 {name} 不存在")
            return False

        # 下载插件
        plugin_url = f"{self.registry_url}/plugins/{name}/{name}.py"
        try:
            response = requests.get(plugin_url)
            if response.status_code == 200:
                plugin_path = self.plugins_dir / f"{name}.py"
                with open(plugin_path, 'w') as f:
                    f.write(response.text)

                # 更新下载计数
                plugin['downloads'] += 1
                self.save_registry(registry)

                print(f"插件 {name} 安装成功")
                return True
            else:
                print(f"下载失败：{response.status_code}")
                return False
        except Exception as e:
            print(f"安装失败：{e}")
            return False

    def uninstall_plugin(self, name: str) -> bool:
        """卸载插件"""
        plugin_path = self.plugins_dir / f"{name}.py"

        if plugin_path.exists():
            plugin_path.unlink()
            print(f"插件 {name} 已卸载")
            return True
        else:
            print(f"插件 {name} 不存在")
            return False

    def show_plugins(self):
        """显示插件列表"""
        plugins = self.list_plugins()

        if not plugins:
            print("没有已注册的插件")
            return

        print("\n插件列表:")
        print("=" * 60)
        for plugin in plugins:
            print(f"\n名称：{plugin['name']}")
            print(f"版本：{plugin['version']}")
            print(f"描述：{plugin['description']}")
            print(f"作者：{plugin['author']}")
            print(f"下载：{plugin['downloads']}")
            print(f"评分：{plugin['rating']:.1f}")
        print("=" * 60)

if __name__ == '__main__':
    marketplace = PluginMarketplace()

    # 示例：注册插件
    # marketplace.register_plugin(
    #     name='validator',
    #     version='1.0.0',
    #     description='数据验证插件',
    #     author='Developer'
    # )

    # 显示插件列表
    marketplace.show_plugins()
