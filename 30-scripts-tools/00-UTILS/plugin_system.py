#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin System
插件系统
"""

import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """插件基类"""

    name: str = "base"
    version: str = "1.0.0"
    description: str = "Base plugin"

    @abstractmethod
    def initialize(self, config: Dict) -> None:
        """初始化插件"""
        pass

    @abstractmethod
    def process(self, data: Dict) -> Dict:
        """处理数据"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭插件"""
        pass


class PluginManager:
    """插件管理器"""

    def __init__(self, plugins_dir: str = None):
        """
        初始化插件管理器

        Args:
            plugins_dir: 插件目录
        """
        if plugins_dir is None:
            plugins_dir = Path(__file__).parent.parent / "plugins"

        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, BasePlugin] = {}
        self.config: Dict[str, Dict] = {}

    def discover_plugins(self) -> List[str]:
        """
        发现可用插件

        Returns:
            插件名称列表
        """
        plugin_files = list(self.plugins_dir.glob("plugin_*.py"))
        plugin_names = []

        for plugin_file in plugin_files:
            try:
                module_name = plugin_file.stem
                module = importlib.import_module(f"plugins.{module_name}")

                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr != BasePlugin
                    ):
                        plugin_names.append(attr.name)
            except Exception as e:
                print(f"Error discovering plugin {plugin_file}: {e}")

        return plugin_names

    def load_plugin(self, plugin_name: str, config: Dict = None) -> bool:
        """
        加载插件

        Args:
            plugin_name: 插件名称
            config: 插件配置

        Returns:
            是否成功
        """
        try:
            # 查找插件文件
            plugin_files = list(self.plugins_dir.glob("plugin_*.py"))

            for plugin_file in plugin_files:
                module_name = plugin_file.stem
                module = importlib.import_module(f"plugins.{module_name}")

                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr != BasePlugin
                    ):
                        if attr.name == plugin_name:
                            # 实例化插件
                            plugin = attr()
                            plugin.initialize(config or {})
                            self.plugins[plugin_name] = plugin
                            self.config[plugin_name] = config or {}
                            print(f"Loaded plugin: {plugin_name} v{plugin.version}")
                            return True

            print(f"Plugin not found: {plugin_name}")
            return False
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件

        Args:
            plugin_name: 插件名称

        Returns:
            是否成功
        """
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].shutdown()
                del self.plugins[plugin_name]
                del self.config[plugin_name]
                print(f"Unloaded plugin: {plugin_name}")
                return True
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {e}")
                return False

        return False

    def process_all(self, data: Dict) -> Dict:
        """
        使用所有插件处理数据

        Args:
            data: 输入数据

        Returns:
            处理后的数据
        """
        result = data

        for plugin_name, plugin in self.plugins.items():
            try:
                result = plugin.process(result)
            except Exception as e:
                print(f"Error processing with plugin {plugin_name}: {e}")

        return result

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        获取插件信息

        Args:
            plugin_name: 插件名称

        Returns:
            插件信息
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            return {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "config": self.config.get(plugin_name, {}),
            }
        return None

    def list_plugins(self) -> List[Dict]:
        """
        列出所有插件

        Returns:
            插件信息列表
        """
        return [self.get_plugin_info(name) for name in self.plugins.keys()]

    def get_stats(self) -> Dict:
        """获取插件统计"""
        return {
            "total_plugins": len(self.plugins),
            "plugins": list(self.plugins.keys()),
        }


# 示例插件
class ExamplePlugin(BasePlugin):
    """示例插件"""

    name = "example"
    version = "1.0.0"
    description = "Example plugin for testing"

    def initialize(self, config: Dict) -> None:
        print(f"ExamplePlugin initialized with config: {config}")

    def process(self, data: Dict) -> Dict:
        # 添加处理标记
        data["processed_by"] = self.name
        return data

    def shutdown(self) -> None:
        print("ExamplePlugin shutdown")


class DataEnrichmentPlugin(BasePlugin):
    """数据增强插件"""

    name = "data_enrichment"
    version = "1.0.0"
    description = "Enrich data with metadata"

    def initialize(self, config: Dict) -> None:
        print(f"DataEnrichmentPlugin initialized")

    def process(self, data: Dict) -> Dict:
        from datetime import datetime

        # 添加元数据
        data["enriched_at"] = datetime.now().isoformat()
        data["enriched_by"] = self.name

        return data

    def shutdown(self) -> None:
        print("DataEnrichmentPlugin shutdown")


if __name__ == "__main__":
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        sys.exit(1)

    print("[OK] Critic Review Passed")

    # 测试插件系统
    manager = PluginManager()

    # 发现插件
    available = manager.discover_plugins()
    print(f"Available plugins: {available}")

    # 加载示例插件
    manager.load_plugin("example", {"setting": "value"})

    # 处理数据
    test_data = {"input": "test"}
    result = manager.process_all(test_data)
    print(f"Processed data: {result}")

    # 列出插件
    plugins = manager.list_plugins()
    print(f"Loaded plugins: {plugins}")

    # 获取统计
    stats = manager.get_stats()
    print(f"Stats: {stats}")

    # 卸载插件
    manager.unload_plugin("example")
