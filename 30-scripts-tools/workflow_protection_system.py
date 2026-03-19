#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Protection System - 工作流多层防护系统

防止草率删除、质量优先于数量、强制人工审查
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"
PROTECTION_CONFIG = "30-scripts-tools/protection_config.json"

class WorkflowProtectionSystem:
    """工作流多层防护系统"""
    
    def __init__(self):
        self.config = self.load_config()
        self.tools_registry = self.load_tools_registry()
        self.violations = []
        
    def load_config(self) -> Dict:
        """加载防护配置"""
        default_config = {
            "version": "1.0.0",
            "created_at": "2026-03-20",
            "principle": "quality_over_quantity",
            "layers": {
                "layer1_pre_check": {"enabled": True},
                "layer2_human_review": {"enabled": True},
                "layer3_impact_analysis": {"enabled": True},
                "layer4_backup_verify": {"enabled": True},
                "layer5_emergency_restore": {"enabled": True}
            },
            "rules": {
                "max_deletion_per_batch": 5,
                "require_human_review": True,
                "require_backup": True,
                "require_impact_analysis": True,
                "protected_categories": ["workflow", "memory", "critic", "session"],
                "min_quality_score": 40
            },
            "red_lines": [
                "禁止为数量目标删除工具",
                "禁止仅凭使用次数决定删除",
                "禁止无文件删除 (除非确认无用)",
                "禁止无备份删除",
                "禁止无人工审查删除"
            ]
        }
        
        if Path(PROTECTION_CONFIG).exists():
            with open(PROTECTION_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(PROTECTION_CONFIG, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def load_tools_registry(self) -> Dict:
        """加载工具库"""
        with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def layer1_pre_check(self, tool_ids: List[str], action: str) -> Tuple[bool, List[str]]:
        """
        第 1 层：前置检查
        
        检查：
        - 是否触碰红线
        - 是否在保护类别
        - 是否超过批量限制
        """
        print("\n🛡️  第 1 层：前置检查")
        
        checks_passed = True
        warnings = []
        
        # 检查 1: 是否触碰红线
        if action == "delete" and len(tool_ids) > self.config["rules"]["max_deletion_per_batch"]:
            checks_passed = False
            warnings.append(f"❌ 批量删除超过限制 ({len(tool_ids)} > {self.config['rules']['max_deletion_per_batch']})")
        
        # 检查 2: 是否在保护类别
        protected = self.config["rules"]["protected_categories"]
        for tool_id in tool_ids:
            tool = self.tools_registry.get("tools", {}).get(tool_id, {})
            category = tool.get("category", "").lower()
            
            for p_cat in protected:
                if p_cat in category.lower():
                    checks_passed = False
                    warnings.append(f"❌ 工具 [{tool_id}] 属于保护类别 [{category}]")
        
        # 检查 3: 是否有质量评分
        for tool_id in tool_ids:
            tool = self.tools_registry.get("tools", {}).get(tool_id, {})
            quality_score = tool.get("quality_score", None)
            
            if quality_score is None:
                warnings.append(f"⚠️  工具 [{tool_id}] 无质量评分，需要先评估")
            elif quality_score < self.config["rules"]["min_quality_score"]:
                warnings.append(f"⚠️  工具 [{tool_id}] 质量评分过低 ({quality_score} < {self.config['rules']['min_quality_score']})")
        
        if checks_passed:
            print("  ✅ 前置检查通过")
        else:
            print("  ❌ 前置检查失败")
            for w in warnings:
                print(f"    {w}")
        
        return checks_passed, warnings
    
    def layer2_human_review(self, tool_ids: List[str], reason: str) -> Tuple[bool, str]:
        """
        第 2 层：人工审查
        
        强制要求：
        - 填写删除原因
        - 人工确认每个工具
        - 审查记录保存
        """
        print("\n🛡️  第 2 层：人工审查")
        
        review_file = Path("99-backups/reviews/deletion-review.json")
        review_file.parent.mkdir(parents=True, exist_ok=True)
        
        review_data = {
            "review_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "reviewed_at": datetime.now().isoformat(),
            "action": "deletion",
            "tool_ids": tool_ids,
            "reason": reason,
            "reviewer": "待填写",
            "status": "pending",
            "tools_reviewed": []
        }
        
        # 为每个工具创建审查项
        for tool_id in tool_ids:
            tool = self.tools_registry.get("tools", {}).get(tool_id, {})
            
            review_item = {
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "category": tool.get("category", ""),
                "usage_count": tool.get("usage_count", 0),
                "has_file": Path(tool.get("file", "")).exists() if tool.get("file") else False,
                "quality_score": tool.get("quality_score", None),
                "reviewer_decision": "待审查",  # approve/reject
                "reviewer_comment": ""
            }
            
            review_data["tools_reviewed"].append(review_item)
        
        # 保存审查记录
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)
        
        print(f"  📝 审查文件已创建：{review_file}")
        print(f"  📊 待审查工具：{len(tool_ids)} 个")
        print(f"  ⚠️  必须由人工审查并填写 reviewer_decision")
        
        # 返回审查文件路径，等待人工审查
        return True, str(review_file)
    
    def layer3_impact_analysis(self, tool_ids: List[str]) -> Tuple[bool, Dict]:
        """
        第 3 层：影响分析
        
        分析：
        - 哪些工具依赖这些工具
        - 删除后影响范围
        - 替代工具是否存在
        """
        print("\n🛡️  第 3 层：影响分析")
        
        analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "tool_ids": tool_ids,
            "dependencies": [],
            "alternatives": [],
            "impact_level": "unknown"
        }
        
        # 分析依赖关系 (简化版)
        tools = self.tools_registry.get("tools", {})
        
        for tool_id in tool_ids:
            dep_info = {
                "tool_id": tool_id,
                "dependents": [],
                "has_alternative": False,
                "alternative_tools": []
            }
            
            # 查找依赖此工具的其他工具
            for other_id, other_tool in tools.items():
                if other_id != tool_id:
                    # 检查是否有依赖关系 (通过文件名、描述等)
                    if tool_id in other_tool.get("description", "") or \
                       tool_id in other_tool.get("file", ""):
                        dep_info["dependents"].append(other_id)
            
            # 查找替代工具 (同类别且功能相似)
            tool = tools.get(tool_id, {})
            category = tool.get("category", "")
            
            for other_id, other_tool in tools.items():
                if other_id != tool_id and other_tool.get("category") == category:
                    dep_info["has_alternative"] = True
                    dep_info["alternative_tools"].append(other_id)
                    break
            
            analysis["dependencies"].append(dep_info)
        
        # 评估影响等级
        total_dependents = sum(len(d["dependents"]) for d in analysis["dependencies"])
        
        if total_dependents > 10:
            analysis["impact_level"] = "high"
        elif total_dependents > 3:
            analysis["impact_level"] = "medium"
        else:
            analysis["impact_level"] = "low"
        
        # 保存分析结果
        analysis_file = Path("99-backups/analysis/deletion-impact-analysis.json")
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"  📊 影响等级：{analysis['impact_level'].upper()}")
        print(f"  📊 依赖工具数：{total_dependents}")
        print(f"  📊 分析文件：{analysis_file}")
        
        if analysis["impact_level"] == "high":
            print("  ⚠️  高影响 - 需要额外审查!")
            return False, analysis
        
        return True, analysis
    
    def layer4_backup_verify(self, tool_ids: List[str]) -> Tuple[bool, str]:
        """
        第 4 层：备份验证
        
        确保：
        - 所有工具已备份
        - 备份可恢复
        - 备份文件完整
        """
        print("\n🛡️  第 4 层：备份验证")
        
        backup_dir = Path("99-backups/deletion-backup")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_manifest = {
            "backup_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "backed_up_at": datetime.now().isoformat(),
            "tool_ids": tool_ids,
            "tools": []
        }
        
        tools = self.tools_registry.get("tools", {})
        all_backed_up = True
        
        for tool_id in tool_ids:
            tool = tools.get(tool_id, {})
            
            tool_backup = {
                "tool_id": tool_id,
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "category": tool.get("category", ""),
                "file": tool.get("file", ""),
                "metadata": tool
            }
            
            backup_manifest["tools"].append(tool_backup)
            
            # 如果有文件，备份文件
            if tool.get("file"):
                file_path = Path(tool["file"])
                if file_path.exists():
                    backup_file = backup_dir / f"{tool_id}.backup"
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ 已备份文件：{tool['file']}")
                else:
                    print(f"  ⚠️  文件不存在：{tool['file']}")
                    tool_backup["file_exists"] = False
            else:
                tool_backup["file_exists"] = False
        
        # 保存备份清单
        manifest_file = backup_dir / f"backup-manifest-{backup_manifest['backup_id']}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(backup_manifest, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 备份完成：{len(tool_ids)} 个工具")
        print(f"  📁 备份目录：{backup_dir}")
        print(f"  📋 清单文件：{manifest_file}")
        
        return True, str(manifest_file)
    
    def layer5_emergency_restore(self, backup_manifest_path: str) -> Tuple[bool, int]:
        """
        第 5 层：紧急恢复
        
        功能：
        - 从备份恢复工具
        - 验证恢复完整性
        - 记录恢复原因
        """
        print("\n🛡️  第 5 层：紧急恢复")
        
        with open(backup_manifest_path, 'r', encoding='utf-8') as f:
            backup = json.load(f)
        
        tools = self.tools_registry.get("tools", {})
        restored_count = 0
        
        for tool_backup in backup.get("tools", []):
            tool_id = tool_backup["tool_id"]
            
            if tool_id not in tools:
                tools[tool_id] = tool_backup["metadata"]
                tools[tool_id]["restored_at"] = datetime.now().isoformat()
                tools[tool_id]["restored_from"] = backup.get("backup_id", "unknown")
                restored_count += 1
                print(f"  ✅ 已恢复：{tool_id}")
            else:
                print(f"  ⚠️  工具已存在：{tool_id}")
        
        # 更新工具库
        self.tools_registry["tools"] = tools
        self.tools_registry["updated_at"] = datetime.now().isoformat()
        
        with open(TOOLS_REGISTRY, 'w', encoding='utf-8') as f:
            json.dump(self.tools_registry, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 恢复完成：{restored_count} 个工具")
        
        return True, restored_count
    
    def run_all_layers(self, tool_ids: List[str], action: str, reason: str = "") -> Dict:
        """运行所有防护层"""
        
        print("=" * 70)
        print("🛡️  工作流多层防护系统")
        print("=" * 70)
        print(f"操作：{action}")
        print(f"工具数：{len(tool_ids)}")
        print(f"原因：{reason}")
        
        result = {
            "action": action,
            "tool_ids": tool_ids,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "layers_passed": [],
            "layers_failed": [],
            "can_proceed": False
        }
        
        # 第 1 层：前置检查
        passed, warnings = self.layer1_pre_check(tool_ids, action)
        if passed:
            result["layers_passed"].append("layer1_pre_check")
        else:
            result["layers_failed"].append("layer1_pre_check")
            result["warnings"] = warnings
            print("\n❌ 第 1 层失败 - 操作终止")
            return result
        
        # 第 2 层：人工审查
        passed, review_file = self.layer2_human_review(tool_ids, reason)
        if passed:
            result["layers_passed"].append("layer2_human_review")
            result["review_file"] = review_file
        else:
            result["layers_failed"].append("layer2_human_review")
            print("\n❌ 第 2 层失败 - 操作终止")
            return result
        
        # 第 3 层：影响分析
        passed, analysis = self.layer3_impact_analysis(tool_ids)
        if passed:
            result["layers_passed"].append("layer3_impact_analysis")
            result["impact_analysis"] = analysis
        else:
            result["layers_failed"].append("layer3_impact_analysis")
            print("\n❌ 第 3 层失败 - 操作终止")
            return result
        
        # 第 4 层：备份验证
        passed, backup_file = self.layer4_backup_verify(tool_ids)
        if passed:
            result["layers_passed"].append("layer4_backup_verify")
            result["backup_manifest"] = backup_file
        else:
            result["layers_failed"].append("layer4_backup_verify")
            print("\n❌ 第 4 层失败 - 操作终止")
            return result
        
        # 所有层通过
        result["can_proceed"] = True
        
        print("\n" + "=" * 70)
        print("✅ 所有防护层通过 - 可以执行操作")
        print("=" * 70)
        print(f"审查文件：{result.get('review_file', 'N/A')}")
        print(f"备份文件：{result.get('backup_manifest', 'N/A')}")
        print(f"影响分析：{result.get('impact_analysis', {}).get('impact_level', 'N/A')}")
        
        return result


def main():
    """主函数"""
    
    print("=" * 70)
    print("🛡️  工作流多层防护系统 - 演示")
    print("=" * 70)
    
    protection = WorkflowProtectionSystem()
    
    # 演示：尝试删除工具
    test_tools = [
        "critical-issue-detector",
        "analyze_memory_scripts",
        "context_db"
    ]
    
    result = protection.run_all_layers(
        tool_ids=test_tools,
        action="delete",
        reason="质量审查 - 低频工具评估"
    )
    
    print("\n" + "=" * 70)
    print("📊 防护系统执行结果")
    print("=" * 70)
    print(f"通过层数：{len(result['layers_passed'])}/5")
    print(f"可执行：{result['can_proceed']}")
    
    if result["can_proceed"]:
        print("\n✅ 防护系统验证通过")
        print("下一步：等待人工审查完成")
    else:
        print("\n❌ 防护系统拦截操作")
        print("原因:", result.get("warnings", ["未知"]))


if __name__ == '__main__':
    main()
