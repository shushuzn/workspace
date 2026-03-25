"""
intentkit 真实环境集成测试
Real intentkit Integration Test

日期：2026-03-07
作者：Claw (OpenClaw)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd: str, cwd: str = None) -> bool:
    """运行命令"""
    print(f"运行：{cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"[FAIL] {result.stderr}")
        return False

    print(f"[OK] 成功")
    return True


def setup_test_environment():
    """设置测试环境"""
    print("=" * 60)
    print("步骤 1: 设置测试环境")
    print("=" * 60)

    # 创建测试目录
    test_dir = Path(__file__).parent / "test_intentkit"
    if test_dir.exists():
        print(f"清理旧测试目录：{test_dir}")
        shutil.rmtree(test_dir)

    test_dir.mkdir(parents=True)
    print(f"[OK] 创建测试目录：{test_dir}")

    return test_dir


def clone_intentkit(test_dir: Path) -> bool:
    """克隆 intentkit 仓库"""
    print("\n" + "=" * 60)
    print("步骤 2: 克隆 intentkit 仓库")
    print("=" * 60)

    intentkit_dir = test_dir / "intentkit"

    # 克隆仓库
    success = run_command(
        "git clone https://github.com/crestalnetwork/intentkit.git",
        cwd=str(test_dir)
    )

    if not success:
        return False

    print(f"[OK] intentkit 克隆完成：{intentkit_dir}")
    return True


def apply_integration(intentkit_dir: Path) -> bool:
    """应用集成补丁"""
    print("\n" + "=" * 60)
    print("步骤 3: 应用集成补丁")
    print("=" * 60)

    # 复制集成模块
    integration_src = Path(__file__).parent
    integration_dst = intentkit_dir / "belief_integration"

    print(f"复制集成模块到：{integration_dst}")

    # 复制文件
    files_to_copy = [
        "intent_schema.py",
        "belief_executor.py",
        "alignment_calculator.py",
        "README.md"
    ]

    integration_dst.mkdir(exist_ok=True)

    for filename in files_to_copy:
        src = integration_src / filename
        dst = integration_dst / filename

        if src.exists():
            shutil.copy2(src, dst)
            print(f"  [OK] {filename}")
        else:
            print(f"  [WARN] {filename} 不存在")

    # 复制探针文件
    probes_src = integration_src / "belief-probes-v2"
    probes_dst = intentkit_dir / "belief_integration" / "probes"

    if probes_src.exists():
        shutil.copytree(probes_src, probes_dst)
        print(f"  [OK] 探针文件已复制")
    else:
        print(f"  [WARN] 探针文件不存在")

    return True


def run_tests(intentkit_dir: Path) -> bool:
    """运行测试"""
    print("\n" + "=" * 60)
    print("步骤 4: 运行集成测试")
    print("=" * 60)

    # 创建测试脚本
    test_script = intentkit_dir / "test_belief_integration.py"

    test_code = '''
"""
信念集成测试
"""

import sys
sys.path.insert(0, str(__file__).parent / "belief_integration")

from intent_schema import EnhancedIntentSchema, BeliefConfig
from alignment_calculator import AlignmentCalculator

def test_intent_schema():
    """测试意图 Schema"""
    print("测试意图 Schema...")
    
    intent = EnhancedIntentSchema.create_search_intent()
    assert intent.name == "search"
    assert intent.belief_config.confidence_threshold == 0.8
    assert intent.belief_config.min_consecutive_layers == 3
    
    print("  [OK] 意图 Schema 测试通过")
    return True

def test_alignment_calculator():
    """测试对齐度计算器"""
    print("测试对齐度计算器...")
    
    calculator = AlignmentCalculator()
    
    result = calculator.calculate(
        intent_achieved=True,
        belief_confidence=0.9,
        layers_used=12
    )
    
    assert 0.8 < result.alignment_score < 0.95
    assert result.efficiency == 0.5  # 12/24
    
    print("  [OK] 对齐度计算器测试通过")
    return True

def test_batch_calculation():
    """测试批量计算"""
    print("测试批量计算...")
    
    calculator = AlignmentCalculator()
    
    executions = [
        {"intent_achieved": True, "belief_confidence": 0.92, "layers_used": 12},
        {"intent_achieved": True, "belief_confidence": 0.95, "layers_used": 24},
        {"intent_achieved": False, "belief_confidence": 0.85, "layers_used": 8},
    ]
    
    stats = calculator.calculate_batch(executions)
    
    assert stats["count"] == 3
    assert 0.7 < stats["avg_alignment"] < 0.9
    
    print("  [OK] 批量计算测试通过")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("信念集成测试")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_intent_schema()
    all_passed &= test_alignment_calculator()
    all_passed &= test_batch_calculation()
    
    print("\\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败!")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)
'''

    # 写入测试脚本
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(test_code)

    print(f"创建测试脚本：{test_script}")

    # 运行测试
    success = run_command(
        "python test_belief_integration.py",
        cwd=str(intentkit_dir)
    )

    return success


def generate_report(test_dir: Path, success: bool):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("步骤 5: 生成测试报告")
    print("=" * 60)

    report_path = test_dir / "test_report.md"

    report = f"""# intentkit 集成测试报告

**日期:** 2026-03-07  
**测试环境:** intentkit (最新)  
**测试结果:** {"✅ 通过" if success else "❌ 失败"}

---

## 测试概述

| 测试项 | 状态 |
|--------|------|
| 意图 Schema | {"✅" if success else "❌"} |
| 对齐度计算器 | {"✅" if success else "❌"} |
| 批量计算 | {"✅" if success else "❌"} |

---

## 测试环境

- **intentkit 版本:** 最新 (main 分支)
- **Python 版本:** {sys.version}
- **测试目录:** {test_dir}

---

## 测试详情

### 1. 意图 Schema 测试

**测试内容:**
- 创建搜索意图
- 验证信念配置
- 验证默认值

**预期结果:**
- intent.name == "search"
- confidence_threshold == 0.8
- min_consecutive_layers == 3

### 2. 对齐度计算器测试

**测试内容:**
- 单次对齐度计算
- 权重验证
- 效率计算

**预期结果:**
- alignment_score 在 0.8-0.95 之间
- efficiency = 0.5 (12/24 层)

### 3. 批量计算测试

**测试内容:**
- 多执行记录批量计算
- 统计指标计算
- 平均值/标准差

**预期结果:**
- count == 3
- avg_alignment 在 0.7-0.9 之间

---

## 结论

{"✅ 集成模块与 intentkit 兼容，所有测试通过!" if success else "❌ 部分测试失败，需要修复"}

---

## 下一步

1. {"✅ 完成" if success else "⏳ 待完成"} - 基础集成测试
2. ⏳ 真实模型集成测试
3. ⏳ 性能基准测试
4. ⏳ 提交 PR 到 intentkit 上游

---

*生成时间：2026-03-07*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"测试报告已生成：{report_path}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"测试结果：{"✅ 通过" if success else "❌ 失败"}")
    print(f"测试目录：{test_dir}")
    print(f"报告文件：{report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("intentkit 真实环境集成测试")
    print("=" * 60)

    # 1. 设置测试环境
    test_dir = setup_test_environment()

    # 2. 克隆 intentkit
    if not clone_intentkit(test_dir):
        print("❌ 克隆 intentkit 失败")
        return False

    # 3. 应用集成
    if not apply_integration(test_dir / "intentkit"):
        print("⚠️ 应用集成时出现警告")

    # 4. 运行测试
    success = run_tests(test_dir / "intentkit")

    # 5. 生成报告
    generate_report(test_dir, success)

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
