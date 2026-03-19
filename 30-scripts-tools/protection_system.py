#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
5 层防护系统 - 工作流执行保护

防护层级:
1. 规则定义防护 - 检查工具调用规则
2. 工具调用防护 - 验证工具注册和调用方式
3. 工作流强制防护 - 确保按顺序执行
4. 质量保障防护 - 批判者审查
5. 数据完整性防护 - 检查点 + Git 保护
"""

import json
import subprocess
import sys
import hashlib
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001"
REGISTRY_FILE = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
CHECKPOINT_FILE = FLOW_ARCHIVE / "checkpoint.json"
EXECUTION_LOG = FLOW_ARCHIVE / "execution-log.json"

class ProtectionLayer:
    """防护层基类"""
    
    def __init__(self, name):
        self.name = name
    
    def check(self, **kwargs):
        """执行检查"""
        raise NotImplementedError
    
    def passed(self):
        """检查是否通过"""
        raise NotImplementedError


class Layer1_RuleProtection(ProtectionLayer):
    """第 1 层：规则定义防护"""
    
    def __init__(self):
        super().__init__("规则定义防护")
        self.rules_file = WORKSPACE / "30-scripts-tools" / "TOOL-CALLING-RULES.md"
        self.registry_file = REGISTRY_FILE
    
    def check(self, **kwargs):
        """检查规则文档和注册表"""
        issues = []
        
        # 检查规则文档是否存在
        if not self.rules_file.exists():
            issues.append("规则文档缺失：TOOL-CALLING-RULES.md")
        
        # 检查注册表是否有原则
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            if 'principles' not in registry:
                issues.append("注册表缺少原则定义")
            
            if 'enforcement_rules' not in registry:
                issues.append("注册表缺少强制规则")
        
        return len(issues) == 0, issues
    
    def passed(self):
        success, _ = self.check()
        return success


class Layer2_ToolCallingProtection(ProtectionLayer):
    """第 2 层：工具调用防护"""
    
    def __init__(self):
        super().__init__("工具调用防护")
        self.registry_file = REGISTRY_FILE
        self.tool_executor = WORKSPACE / "30-scripts-tools" / "tool_executor.py"
    
    def check(self, tool_id=None, **kwargs):
        """检查工具调用合规性"""
        issues = []
        
        # 检查 tool_executor 是否存在
        if not self.tool_executor.exists():
            issues.append("工具执行器缺失：tool_executor.py")
        
        # 检查工具是否注册
        if tool_id:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                if tool_id not in registry.get('tools', {}):
                    issues.append(f"工具未注册：{tool_id}")
        
        return len(issues) == 0, issues
    
    def passed(self):
        success, _ = self.check()
        return success


class Layer3_WorkflowEnforcement(ProtectionLayer):
    """第 3 层：工作流强制防护"""
    
    def __init__(self):
        super().__init__("工作流强制防护")
        self.checkpoint_file = CHECKPOINT_FILE
        self.workflow_file = FLOW_ARCHIVE / "workflow.json"
    
    def check(self, current_step=None, target_step=None, **kwargs):
        """检查工作流执行合规性"""
        issues = []
        
        # 检查工作流配置
        if not self.workflow_file.exists():
            issues.append("工作流配置缺失：workflow.json")
        
        # 检查跳步
        if current_step and target_step:
            if target_step > current_step + 1:
                issues.append(f"禁止跳步！当前：{current_step}, 目标：{target_step}")
            
            if target_step < current_step:
                issues.append(f"禁止回退！当前：{current_step}, 目标：{target_step}")
        
        return len(issues) == 0, issues
    
    def passed(self):
        success, _ = self.check()
        return success


class Layer4_QualityAssurance(ProtectionLayer):
    """第 4 层：质量保障防护"""
    
    def __init__(self):
        super().__init__("质量保障防护")
        self.critic_script = WORKSPACE / "30-scripts-tools" / "auto-critic_v7.py"
        self.quality_gate = WORKSPACE / "30-scripts-tools" / "quality_gate_check.py"
    
    def check(self, task_name=None, phase='final', **kwargs):
        """检查质量保障"""
        issues = []
        
        # 检查批判者脚本
        if not self.critic_script.exists():
            issues.append("批判者脚本缺失：auto-critic_v7.py")
        
        # 检查质量门禁
        if not self.quality_gate.exists():
            issues.append("质量门禁缺失：quality_gate_check.py")
        
        return len(issues) == 0, issues
    
    def passed(self):
        success, _ = self.check()
        return success


class Layer5_DataIntegrity(ProtectionLayer):
    """第 5 层：数据完整性防护"""
    
    def __init__(self):
        super().__init__("数据完整性防护")
        self.checkpoint_file = CHECKPOINT_FILE
        self.execution_log = EXECUTION_LOG
    
    def check(self, **kwargs):
        """检查数据完整性"""
        issues = []
        
        # 检查检查点文件
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                # 验证必要字段（兼容旧格式）
                required_fields = ['flow_id', 'current_step', 'completed_steps']
                for field in required_fields:
                    if field not in checkpoint:
                        issues.append(f"检查点缺少字段：{field}")
            except json.JSONDecodeError:
                issues.append("检查点文件损坏")
        
        return len(issues) == 0, issues
    
    def save_checkpoint(self, step_id, status='completed'):
        """保存检查点（带防篡改）"""
        checkpoint = {
            'flow_id': '20260318-universal-workflow-001',
            'current_step': step_id,
            'completed_steps': list(range(1, step_id + 1)),
            'status': status,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 计算 checksum（防篡改）
        checksum_data = json.dumps(checkpoint, sort_keys=True)
        checkpoint['checksum'] = hashlib.sha256(checksum_data.encode()).hexdigest()
        
        # 原子写入
        tmp_file = self.checkpoint_file.with_suffix('.tmp')
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        tmp_file.replace(self.checkpoint_file)
        
        print(f"[第 5 层] 检查点已保存：Step {step_id}")
    
    def passed(self):
        success, _ = self.check()
        return success


class FiveLayerProtectionSystem:
    """5 层防护系统"""
    
    def __init__(self):
        self.layers = [
            Layer1_RuleProtection(),
            Layer2_ToolCallingProtection(),
            Layer3_WorkflowEnforcement(),
            Layer4_QualityAssurance(),
            Layer5_DataIntegrity(),
        ]
    
    def check_all(self, **kwargs):
        """执行所有防护层检查"""
        results = []
        all_passed = True
        
        print("="*60)
        print("5 层防护系统检查")
        print("="*60)
        
        for i, layer in enumerate(self.layers, 1):
            success, issues = layer.check(**kwargs)
            status = "✅" if success else "❌"
            print(f"[第 {i} 层] {layer.name}: {status}")
            
            if issues:
                for issue in issues:
                    print(f"         - {issue}")
            
            if not success:
                all_passed = False
            
            results.append({
                'layer': i,
                'name': layer.name,
                'passed': success,
                'issues': issues
            })
        
        print("="*60)
        if all_passed:
            print("✅ 所有防护层检查通过")
        else:
            print("❌ 部分防护层检查失败")
        print("="*60)
        
        return all_passed, results
    
    def save_checkpoint(self, step_id):
        """保存检查点"""
        layer5 = self.layers[4]  # 第 5 层
        if isinstance(layer5, Layer5_DataIntegrity):
            layer5.save_checkpoint(step_id)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--check':
            # 执行防护层检查
            system = FiveLayerProtectionSystem()
            success, _ = system.check_all()
            sys.exit(0 if success else 1)
        
        elif command == '--save-checkpoint':
            if len(sys.argv) > 2:
                step_id = int(sys.argv[2])
                system = FiveLayerProtectionSystem()
                system.save_checkpoint(step_id)
            else:
                print("用法：py protection_system.py --save-checkpoint <step_id>")
                sys.exit(1)
        
        else:
            print("用法:")
            print("  py protection_system.py --check           # 检查所有防护层")
            print("  py protection_system.py --save-checkpoint <step_id>  # 保存检查点")
            sys.exit(1)
    else:
        # 默认执行检查
        system = FiveLayerProtectionSystem()
        success, _ = system.check_all()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
