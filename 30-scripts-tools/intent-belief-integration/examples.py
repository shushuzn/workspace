"""
intentkit 集成示例项目
Intentkit Integration Example

日期：2026-03-07
作者：Claw (OpenClaw)
"""

import asyncio
import numpy as np
from pathlib import Path

# 模拟 intentkit 导入
# from intentkit.intents.base import Intent, BeliefConfig
# from intentkit.agents.belief_executor import BeliefAwareExecutor
# from intentkit.probes.alignment import AlignmentCalculator

# 使用本地实现
import sys
sys.path.insert(0, str(Path(__file__).parent))

from intent_schema import EnhancedIntentSchema, BeliefConfig
from belief_executor import BeliefAwareExecutor
from alignment_calculator import AlignmentCalculator


# ============================================
# 示例 1: 基础集成
# ============================================

async def example_basic():
    """基础集成示例"""
    print("=" * 60)
    print("示例 1: 基础集成")
    print("=" * 60)

    # 1. 创建意图
    intent = EnhancedIntentSchema.create_search_intent()
    print(f"\n意图：{intent.name}")
    print(f"置信度阈值：{intent.belief_config.confidence_threshold}")

    # 2. 创建执行器
    executor = BeliefAwareExecutor()

    # 3. 模拟激活获取
    def mock_activation(layer_idx: int) -> np.ndarray:
        base = 0.5 + (layer_idx / 24) * 0.4
        return (np.random.randn(2048) * 0.1 + base).astype(np.float32)

    # 4. 执行
    result = await executor.execute_with_early_exit(intent, mock_activation)

    # 5. 生成报告
    report = executor.generate_report(intent, result)
    print(f"\n执行结果:")
    print(f"  退出类型：{report['exit_type']}")
    print(f"  使用层数：{report['layers_used']}/24")
    print(f"  效率得分：{report['efficiency']:.2%}")
    print(f"  对齐度：{report['alignment_score']:.4f}")


# ============================================
# 示例 2: 多意图批处理
# ============================================

async def example_batch():
    """多意图批处理示例"""
    print("\n" + "=" * 60)
    print("示例 2: 多意图批处理")
    print("=" * 60)

    # 创建多个意图
    intents = [
        EnhancedIntentSchema.create_search_intent(),
        EnhancedIntentSchema.create_math_intent(),
        EnhancedIntentSchema.create_creative_intent(),
    ]

    executor = BeliefAwareExecutor()
    calculator = AlignmentCalculator()

    results = []

    for intent in intents:
        print(f"\n处理意图：{intent.name}")

        # 模拟激活 (不同类型意图不同模式)
        def mock_activation(layer_idx: int) -> np.ndarray:
            if intent.name == "math_calculation":
                base = 0.6 + (layer_idx / 24) * 0.35  # 数学需要更多层
            elif intent.name == "creative_writing":
                base = 0.5 + (layer_idx / 24) * 0.45  # 创意可以早退
            else:
                base = 0.5 + (layer_idx / 24) * 0.4  # 默认

            return (np.random.randn(2048) * 0.1 + base).astype(np.float32)

        result = await executor.execute_with_early_exit(intent, mock_activation)
        report = executor.generate_report(intent, result)

        results.append({
            "name": intent.name,
            "layers_used": report["layers_used"],
            "efficiency": report["efficiency"],
            "alignment": report["alignment_score"]
        })

        print(f"  层数：{report['layers_used']}, 效率：{report['efficiency']:.2%}")

    # 批量统计
    print(f"\n批量统计:")
    avg_layers = sum(r["layers_used"] for r in results) / len(results)
    avg_efficiency = sum(r["efficiency"] for r in results) / len(results)
    avg_alignment = sum(r["alignment"] for r in results) / len(results)

    print(f"  平均层数：{avg_layers:.1f}/24")
    print(f"  平均效率：{avg_efficiency:.2%}")
    print(f"  平均对齐度：{avg_alignment:.4f}")


# ============================================
# 示例 3: 自定义权重配置
# ============================================

async def example_custom_weights():
    """自定义权重配置示例"""
    print("\n" + "=" * 60)
    print("示例 3: 自定义权重配置")
    print("=" * 60)

    # 创建不同权重配置的计算器

    # 配置 1: 重视意图达成
    calculator_intent = AlignmentCalculator(
        weights={"intent": 0.7, "belief": 0.2, "efficiency": 0.1}
    )

    # 配置 2: 重视信念置信
    calculator_belief = AlignmentCalculator(
        weights={"intent": 0.3, "belief": 0.5, "efficiency": 0.2}
    )

    # 配置 3: 重视效率
    calculator_efficiency = AlignmentCalculator(
        weights={"intent": 0.4, "belief": 0.2, "efficiency": 0.4}
    )

    # 测试数据
    test_cases = [
        {"achieved": True, "confidence": 0.9, "layers": 10},
        {"achieved": True, "confidence": 0.95, "layers": 24},
        {"achieved": False, "confidence": 0.85, "layers": 8},
    ]

    print("\n不同权重配置对比:")
    print(f"{'场景':<20} {'意图优先':<12} {'信念优先':<12} {'效率优先':<12}")
    print("-" * 60)

    for i, case in enumerate(test_cases):
        result_intent = calculator_intent.calculate(
            case["achieved"], case["confidence"], case["layers"]
        )
        result_belief = calculator_belief.calculate(
            case["achieved"], case["confidence"], case["layers"]
        )
        result_eff = calculator_efficiency.calculate(
            case["achieved"], case["confidence"], case["layers"]
        )

        scenario = f"场景 {i +1}"
        print(f"{scenario:<20} {result_intent.alignment_score:.4f}      "
              f"{result_belief.alignment_score:.4f}      "
              f"{result_eff.alignment_score:.4f}")


# ============================================
# 示例 4: 真实场景模拟
# ============================================

async def example_realistic():
    """真实场景模拟"""
    print("\n" + "=" * 60)
    print("示例 4: 真实场景模拟")
    print("=" * 60)

    # 模拟用户查询队列
    queries = [
        {"type": "search", "query": "天气如何"},
        {"type": "math", "query": "234 * 567"},
        {"type": "creative", "query": "写一首关于春天的诗"},
        {"type": "search", "query": "Python 教程"},
        {"type": "math", "query": "sqrt(144)"},
    ]

    executor = BeliefAwareExecutor()
    calculator = AlignmentCalculator()

    total_layers = 0
    total_saved = 0

    for i, query in enumerate(queries, 1):
        print(f"\n查询 {i}: {query['type']} - {query['query']}")

        # 根据类型创建意图
        if query["type"] == "search":
            intent = EnhancedIntentSchema.create_search_intent()
        elif query["type"] == "math":
            intent = EnhancedIntentSchema.create_math_intent()
        else:
            intent = EnhancedIntentSchema.create_creative_intent()

        # 模拟激活 (带噪声)
        def mock_activation(layer_idx: int) -> np.ndarray:
            base = 0.5 + (layer_idx / 24) * 0.4
            noise = np.random.randn(2048) * 0.05  # 添加噪声
            return (np.random.randn(2048) * 0.1 + base + noise).astype(np.float32)

        result = await executor.execute_with_early_exit(intent, mock_activation)

        layers_saved = 24 - result["layers_used"]
        total_layers += result["layers_used"]
        total_saved += layers_saved

        print(f"  使用 {result['layers_used']} 层，节省 {layers_saved} 层")

    # 总体统计
    print(f"\n总体统计:")
    print(f"  总查询数：{len(queries)}")
    print(f"  总使用层数：{total_layers}/576 ({total_layers /len(queries):.1f} 平均)")
    print(f"  总节省层数：{total_saved}")
    print(f"  整体效率：{total_saved / (24 * len(queries)):.2%}")


# ============================================
# 主函数
# ============================================

async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("intentkit 集成示例")
    print("=" * 60)

    await example_basic()
    await example_batch()
    await example_custom_weights()
    await example_realistic()

    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
