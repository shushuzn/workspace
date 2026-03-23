#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL Optimizer - CPU Optimized
强化学习优化器 (CPU 优化版)

功能：
1. 材料生成环境
2. 奖励函数设计
3. Policy Gradient Agent
4. CPU 优化，严格控制使用率

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:15
"""

import os
import json
import time
import math
import random
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
import threading

# ============================================================================
# 1. CPU 保护配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 保护配置"""
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    max_concurrent: int = 1
    cpu_threshold: float = 70.0
    batch_size: int = 10


# ============================================================================
# 2. CPU 监控
# ============================================================================

class CPUMonitor:
    """CPU 使用监控器"""

    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
        self.lock = threading.Lock()

    def get_cpu_percent(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    def should_wait(self) -> bool:
        current = self.get_cpu_percent()
        with self.lock:
            self.history.append(current)
            if current > self.threshold:
                return True
            if len(self.history) >= 5:
                avg = sum(self.history) / len(self.history)
                if avg > self.threshold * 0.9:
                    return True
        return False

    def wait_if_needed(self, timeout: float = 5.0):
        start = time.time()
        while self.should_wait():
            if time.time() - start > timeout:
                break
            time.sleep(0.5)


# ============================================================================
# 3. 数据结构
# ============================================================================

@dataclass
class MaterialAction:
    """材料生成动作"""
    action_type: str  # 'add_element', 'remove_element', 'modify_ratio'
    element: Optional[str] = None
    ratio: Optional[float] = None


@dataclass
class MaterialState:
    """材料状态"""
    formula: str
    elements: List[str]
    ratios: List[float]
    properties: Dict[str, float]


@dataclass
class RLEpisode:
    """RL 回合"""
    states: List[MaterialState]
    actions: List[MaterialAction]
    rewards: List[float]
    total_reward: float


# ============================================================================
# 4. 材料生成环境
# ============================================================================

class MaterialEnv:
    """材料生成环境"""

    def __init__(self, target_properties: Dict[str, float]):
        self.target = target_properties
        self.element_pool = ['Li', 'Na', 'K', 'Mg', 'Ca', 'Ti', 'Fe', 'Co', 'Ni',
                            'Cu', 'Zn', 'Si', 'Ge', 'O', 'S', 'Se', 'P', 'F', 'Cl']

        self.current_state = None
        self.step_count = 0
        self.max_steps = 20

    def reset(self) -> MaterialState:
        """重置环境"""
        # 随机初始材料
        n_elements = random.randint(2, 4)
        elements = random.sample(self.element_pool, n_elements)
        ratios = [random.uniform(0.5, 2.0) for _ in range(n_elements)]

        formula = self._elements_to_formula(elements, ratios)
        properties = self._predict_properties(elements, ratios)

        self.current_state = MaterialState(
            formula=formula,
            elements=elements,
            ratios=ratios,
            properties=properties
        )
        self.step_count = 0

        return self.current_state

    def step(self, action: MaterialAction) -> Tuple[MaterialState, float, bool]:
        """执行动作"""
        self.step_count += 1

        # 应用动作
        if action.action_type == 'add_element':
            if action.element and action.element not in self.current_state.elements:
                self.current_state.elements.append(action.element)
                self.current_state.ratios.append(action.ratio or 1.0)

        elif action.action_type == 'remove_element':
            if action.element and action.element in self.current_state.elements:
                idx = self.current_state.elements.index(action.element)
                self.current_state.elements.pop(idx)
                self.current_state.ratios.pop(idx)

        elif action.action_type == 'modify_ratio':
            if action.element and action.ratio:
                if action.element in self.current_state.elements:
                    idx = self.current_state.elements.index(action.element)
                    self.current_state.ratios[idx] = action.ratio

        # 更新化学式和性能
        self.current_state.formula = self._elements_to_formula(
            self.current_state.elements,
            self.current_state.ratios
        )
        self.current_state.properties = self._predict_properties(
            self.current_state.elements,
            self.current_state.ratios
        )

        # 计算奖励
        reward = self._calculate_reward()

        # 检查是否结束
        done = (self.step_count >= self.max_steps or
                len(self.current_state.elements) < 2 or
                len(self.current_state.elements) > 6)

        return self.current_state, reward, done

    def _elements_to_formula(self, elements: List[str], ratios: List[float]) -> str:
        """元素转换为化学式"""
        parts = []
        for elem, ratio in zip(elements, ratios):
            count = max(1, min(4, int(ratio * 2)))
            if count > 1:
                parts.append(f"{elem}{count}")
            else:
                parts.append(elem)
        return ''.join(parts)

    def _predict_properties(self, elements: List[str], ratios: List[float]) -> Dict[str, float]:
        """预测性能"""
        # 简化实现
        n_elements = len(elements)
        avg_ratio = sum(ratios) / len(ratios) if ratios else 1.0

        return {
            'band_gap': round(1.0 + n_elements * 0.5 + avg_ratio * 0.3, 2),
            'formation_energy': round(-3.0 - n_elements * 0.5, 2),
            'bulk_modulus': round(50 + n_elements * 20 + avg_ratio * 10, 1),
            'e_above_hull': round(random.uniform(0, 0.5), 3)
        }

    def _calculate_reward(self) -> float:
        """计算奖励"""
        if not self.target:
            return 0.0

        reward = 0.0
        count = 0

        for prop, target_val in self.target.items():
            if prop in self.current_state.properties:
                pred_val = self.current_state.properties[prop]
                if target_val != 0:
                    error = abs(pred_val - target_val) / abs(target_val)
                    # 误差越小奖励越高
                    if error < 0.1:
                        reward += 10
                    elif error < 0.2:
                        reward += 5
                    elif error < 0.5:
                        reward += 2
                    else:
                        reward -= 1
                count += 1

        # 稳定性奖励
        if self.current_state.properties.get('e_above_hull', 1) < 0.1:
            reward += 5

        return reward / count if count > 0 else 0.0


# ============================================================================
# 5. RL Agent (Policy Gradient)
# ============================================================================

class PolicyGradientAgent:
    """Policy Gradient Agent"""

    def __init__(self, state_dim: int, action_dim: int, learning_rate: float = 0.01):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = learning_rate

        # 简单策略网络权重
        self.weights = self._initialize_weights()

        # 训练历史
        self.saved_log_probs = []
        self.rewards = []

    def _initialize_weights(self) -> List[float]:
        """初始化权重"""
        fan_in = self.state_dim
        fan_out = self.action_dim
        std = math.sqrt(2.0 / (fan_in + fan_out))
        return [random.gauss(0, std) for _ in range(fan_in * self.action_dim)]

    def select_action(self, state: MaterialState) -> MaterialAction:
        """选择动作"""
        # 将状态转换为向量
        state_vector = self._state_to_vector(state)

        # 计算动作概率
        action_probs = self._forward(state_vector)

        # 采样动作
        action_idx = self._sample_action(action_probs)

        # 转换为 MaterialAction
        action = self._idx_to_action(action_idx, state)

        return action

    def _state_to_vector(self, state: MaterialState) -> List[float]:
        """状态转向量"""
        # 简化：元素 one-hot + ratios
        element_pool = ['Li', 'Na', 'K', 'Mg', 'Ca', 'Ti', 'Fe', 'Co', 'Ni',
                       'Cu', 'Zn', 'Si', 'Ge', 'O', 'S', 'Se', 'P', 'F', 'Cl']

        vector = []
        for elem in element_pool:
            vector.append(1.0 if elem in state.elements else 0.0)

        for ratio in state.ratios[:6]:  # 最多 6 个元素
            vector.append(ratio)

        # 填充到固定长度
        while len(vector) < self.state_dim:
            vector.append(0.0)

        return vector[:self.state_dim]

    def _forward(self, state_vector: List[float]) -> List[float]:
        """前向传播"""
        # 简单线性层 + softmax
        output = []
        for i in range(self.action_dim):
            val = 0.0
            for j, s in enumerate(state_vector):
                if j * self.action_dim + i < len(self.weights):
                    val += s * self.weights[j * self.action_dim + i]
            output.append(val)

        # Softmax
        max_val = max(output)
        exp_vals = [math.exp(v - max_val) for v in output]
        sum_exp = sum(exp_vals)
        probs = [e / sum_exp for e in exp_vals]

        return probs

    def _sample_action(self, probs: List[float]) -> int:
        """采样动作"""
        r = random.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i
        return len(probs) - 1

    def _idx_to_action(self, idx: int, state: MaterialState) -> MaterialAction:
        """索引转动作"""
        action_types = ['add_element', 'remove_element', 'modify_ratio']
        element_pool = ['Li', 'Na', 'K', 'Mg', 'Ca', 'Ti', 'Fe', 'Co', 'Ni',
                       'Cu', 'Zn', 'Si', 'Ge', 'O', 'S', 'Se', 'P', 'F', 'Cl']

        action_type = action_types[idx % len(action_types)]
        element_idx = (idx // len(action_types)) % len(element_pool)
        element = element_pool[element_idx]

        ratio = random.uniform(0.5, 2.0) if action_type == 'modify_ratio' else None

        return MaterialAction(
            action_type=action_type,
            element=element,
            ratio=ratio
        )

    def store_transition(self, log_prob: float, reward: float):
        """存储转移"""
        self.saved_log_probs.append(log_prob)
        self.rewards.append(reward)

    def update_policy(self, gamma: float = 0.99):
        """更新策略"""
        # 计算折扣回报
        discounted_returns = []
        G = 0
        for r in reversed(self.rewards):
            G = r + gamma * G
            discounted_returns.insert(0, G)

        # 标准化
        if len(discounted_returns) > 1:
            mean = sum(discounted_returns) / len(discounted_returns)
            std = math.sqrt(sum((r - mean) ** 2 for r in discounted_returns) / len(discounted_returns))
            if std > 0:
                discounted_returns = [(r - mean) / std for r in discounted_returns]

        # 更新权重 (简化)
        for i, (log_prob, G) in enumerate(zip(self.saved_log_probs, discounted_returns)):
            # 梯度上升
            gradient = log_prob * G
            # 更新权重 (简化实现)
            for j in range(len(self.weights)):
                self.weights[j] += self.lr * gradient * 0.01

        # 清空
        self.saved_log_probs = []
        self.rewards = []


# ============================================================================
# 6. RL 优化器
# ============================================================================

class RLOptimizer:
    """RL 优化器"""

    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.monitor = CPUMonitor(self.config.cpu_threshold)

        # Agent 参数
        self.state_dim = 25  # 状态维度
        self.action_dim = 60  # 动作维度 (3 类型 × 20 元素)

        self.agent = None
        self.episodes_history = []

        # 设置环境变量
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)

    def initialize(self):
        """初始化"""
        print("[RL] 初始化 Agent...")
        self.agent = PolicyGradientAgent(self.state_dim, self.action_dim)
        print(f"[RL] Agent: 状态{self.state_dim}维，动作{self.action_dim}维")

    def train(self, target_properties: Dict[str, float],
              n_episodes: int = 50, max_steps: int = 20):
        """训练"""

        print(f"\n[RL] 开始训练...")
        print(f"  目标性能：{target_properties}")
        print(f"  回合数：{n_episodes}")
        print(f"  最大步数：{max_steps}")

        best_reward = -float('inf')
        best_material = None

        for ep_idx in range(n_episodes):
            # 检查 CPU
            self.monitor.wait_if_needed(timeout=5.0)

            # 创建环境
            env = MaterialEnv(target_properties)
            state = env.reset()

            episode = RLEpisode(states=[], actions=[], rewards=[], total_reward=0)

            for step in range(max_steps):
                # 选择动作
                action = self.agent.select_action(state)

                # 执行动作
                next_state, reward, done = env.step(action)

                # 存储转移
                log_prob = math.log(0.1)  # 简化
                self.agent.store_transition(log_prob, reward)

                # 记录
                episode.states.append(state)
                episode.actions.append(action)
                episode.rewards.append(reward)
                episode.total_reward += reward

                state = next_state

                if done:
                    break

            # 更新策略
            self.agent.update_policy()

            self.episodes_history.append(episode)

            # 记录最佳
            if episode.total_reward > best_reward:
                best_reward = episode.total_reward
                best_material = state

            # 打印进度
            if (ep_idx + 1) % 10 == 0:
                print(f"  Episode {ep_idx + 1}/{n_episodes}, "
                      f"Reward: {episode.total_reward:.2f}, "
                      f"Best: {best_reward:.2f}")

            # 回合间休息
            time.sleep(0.1)

        print(f"\n[RL] 训练完成！最佳奖励：{best_reward:.2f}")
        print(f"  最佳材料：{best_material.formula if best_material else 'N/A'}")

        return best_material

    def optimize(self, target_properties: Dict[str, float],
                initial_material: Optional[MaterialState] = None) -> MaterialState:
        """优化给定材料"""

        print(f"\n[RL] 优化材料...")
        print(f"  目标：{target_properties}")

        env = MaterialEnv(target_properties)

        if initial_material:
            env.current_state = initial_material
        else:
            env.reset()

        best_state = env.current_state
        best_reward = env._calculate_reward()

        for step in range(20):
            # 检查 CPU
            self.monitor.wait_if_needed(timeout=5.0)

            # 选择动作
            action = self.agent.select_action(env.current_state)

            # 执行动作
            next_state, reward, done = env.step(action)

            if reward > best_reward:
                best_reward = reward
                best_state = next_state

            if done:
                break

        print(f"  优化后：{best_state.formula}")
        print(f"  奖励：{best_reward:.2f}")

        return best_state

    def get_stats(self) -> Dict:
        """获取统计"""
        if not self.episodes_history:
            return {'trained': False}

        avg_rewards = [ep.total_reward for ep in self.episodes_history]

        return {
            'trained': True,
            'n_episodes': len(self.episodes_history),
            'avg_reward': sum(avg_rewards) / len(avg_rewards),
            'best_reward': max(avg_rewards),
            'current_cpu': self.monitor.get_cpu_percent()
        }


# ============================================================================
# 7. 全局实例
# ============================================================================

_optimizer_instance = None

def get_rl_optimizer(config: CPUConfig = None) -> RLOptimizer:
    """获取 RL 优化器单例"""
    global _optimizer_instance

    if _optimizer_instance is None:
        _optimizer_instance = RLOptimizer(config)

    return _optimizer_instance


# ============================================================================
# 8. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("RL Optimizer - CPU Optimized")
    print("=" * 60)

    # 1. 创建优化器
    print("\n[1/4] 创建优化器...")
    config = CPUConfig(
        intra_op_threads=4,
        inter_op_threads=2,
        max_concurrent=1,
        cpu_threshold=70.0
    )

    optimizer = get_rl_optimizer(config)
    optimizer.initialize()

    # 2. 训练
    print("\n[2/4] 训练...")
    target = {'band_gap': 3.0, 'formation_energy': -3.0}

    best_material = optimizer.train(target, n_episodes=30, max_steps=15)

    # 3. 优化
    print("\n[3/4] 优化...")
    if best_material:
        optimized = optimizer.optimize(target, best_material)
        print(f"  最终材料：{optimized.formula}")
        print(f"  性能：{optimized.properties}")

    # 4. 统计
    print("\n[4/4] 统计信息...")
    stats = optimizer.get_stats()

    print(f"  已训练：{'✅' if stats.get('trained') else '❌'}")
    print(f"  回合数：{stats.get('n_episodes', 0)}")
    print(f"  平均奖励：{stats.get('avg_reward', 0):.2f}")
    print(f"  最佳奖励：{stats.get('best_reward', 0):.2f}")
    print(f"  当前 CPU: {stats.get('current_cpu', 0):.1f}%")

    print("\n" + "=" * 60)
    print("RL 优化器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
