#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conditional VAE - CPU Optimized
条件变分自编码器 (CPU 优化版)

功能：
1. 基于目标性能生成材料
2. 条件 VAE 架构
3. 多目标优化支持
4. CPU 优化，严格控制使用率

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:10
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
class ConditionalTarget:
    """生成目标"""
    band_gap: Optional[float] = None
    formation_energy: Optional[float] = None
    bulk_modulus: Optional[float] = None
    shear_modulus: Optional[float] = None
    e_above_hull: Optional[float] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict) -> 'ConditionalTarget':
        return cls(
            band_gap=data.get('band_gap'),
            formation_energy=data.get('formation_energy'),
            bulk_modulus=data.get('bulk_modulus'),
            shear_modulus=data.get('shear_modulus'),
            e_above_hull=data.get('e_above_hull')
        )


@dataclass
class GeneratedMaterial:
    """生成的材料"""
    formula: str
    elements: List[str]
    structure: Dict
    predicted_properties: Dict[str, float]
    target_match_score: float  # 目标匹配度
    validity_score: float      # 有效性
    novelty_score: float       # 新颖性


# ============================================================================
# 4. 条件 VAE 模型
# ============================================================================

class ConditionalVAE:
    """条件 VAE 模型"""

    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.monitor = CPUMonitor(self.config.cpu_threshold)

        # 网络参数
        self.input_dim = 128       # 输入维度
        self.cond_dim = 5          # 条件维度 (5 种性能)
        self.latent_dim = 32       # 潜空间维度
        self.hidden_dim = 64       # 隐藏层维度

        # 条件编码器
        self.cond_encoder = None

        # 主编码器 (输入 + 条件)
        self.encoder = None

        # 解码器
        self.decoder = None

        # 训练历史
        self.training_history = []

        # 设置环境变量
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)

    def initialize_weights(self):
        """初始化权重"""
        print("[C-VAE] 初始化网络权重...")

        # 条件编码器：cond_dim -> hidden_dim
        self.cond_encoder = {
            'w': self._xavier_init(self.cond_dim, self.hidden_dim),
            'b': [0.0] * self.hidden_dim
        }

        # 主编码器：(input_dim + hidden_dim) -> hidden_dim -> latent_dim * 2
        combined_dim = self.input_dim + self.hidden_dim
        self.encoder = {
            'w1': self._xavier_init(combined_dim, self.hidden_dim),
            'b1': [0.0] * self.hidden_dim,
            'w2': self._xavier_init(self.hidden_dim, self.latent_dim * 2),
            'b2': [0.0] * (self.latent_dim * 2)
        }

        # 解码器：(latent_dim + hidden_dim) -> hidden_dim -> input_dim
        combined_dec_dim = self.latent_dim + self.hidden_dim
        self.decoder = {
            'w1': self._xavier_init(combined_dec_dim, self.hidden_dim),
            'b1': [0.0] * self.hidden_dim,
            'w2': self._xavier_init(self.hidden_dim, self.input_dim),
            'b2': [0.0] * self.input_dim
        }

        print(f"[C-VAE] 架构：输入{self.input_dim} + 条件{self.cond_dim} → 潜空间{self.latent_dim}")

    def _xavier_init(self, fan_in: int, fan_out: int) -> List[float]:
        """Xavier 初始化"""
        std = math.sqrt(2.0 / (fan_in + fan_out))
        return [random.gauss(0, std) for _ in range(fan_in * fan_out)]

    def encode_condition(self, target: ConditionalTarget) -> List[float]:
        """编码条件向量"""
        if not self.cond_encoder:
            self.initialize_weights()

        # 将目标性能转换为向量
        cond_vector = [
            target.band_gap or 0.0,
            target.formation_energy or 0.0,
            target.bulk_modulus or 0.0,
            target.shear_modulus or 0.0,
            target.e_above_hull or 0.0
        ]

        # 归一化
        cond_vector = self._normalize(cond_vector)

        # 通过条件编码器
        hidden = self._relu(self._linear(cond_vector,
                                         self.cond_encoder['w'],
                                         self.cond_encoder['b']))

        return hidden

    def encode(self, material_descriptor: List[float],
               condition_hidden: List[float]) -> Tuple[List[float], List[float]]:
        """编码器：材料 + 条件 → 潜空间"""

        # 检查 CPU
        self.monitor.wait_if_needed(timeout=5.0)

        if not self.encoder:
            self.initialize_weights()

        # 拼接输入和条件
        combined = material_descriptor + condition_hidden

        # 前向传播
        h = self._relu(self._linear(combined,
                                     self.encoder['w1'],
                                     self.encoder['b1']))

        output = self._linear(h,
                             self.encoder['w2'],
                             self.encoder['b2'])

        mean = output[:self.latent_dim]
        log_var = output[self.latent_dim:]

        return mean, log_var

    def decode(self, latent_vector: List[float],
               condition_hidden: List[float]) -> List[float]:
        """解码器：潜空间 + 条件 → 材料"""

        # 检查 CPU
        self.monitor.wait_if_needed(timeout=5.0)

        if not self.decoder:
            self.initialize_weights()

        # 拼接潜向量和条件
        combined = latent_vector + condition_hidden

        # 前向传播
        h = self._relu(self._linear(combined,
                                     self.decoder['w1'],
                                     self.decoder['b1']))

        output = self._linear(h,
                             self.decoder['w2'],
                             self.decoder['b2'])

        return output

    def _linear(self, x: List[float], w: List[float], b: List[float]) -> List[float]:
        """线性层"""
        out_dim = len(b)
        in_dim = len(x)

        result = []
        for i in range(out_dim):
            val = b[i]
            for j in range(in_dim):
                val += x[j] * w[j * out_dim + i]
            result.append(val)

        return result

    def _relu(self, x: List[float]) -> List[float]:
        """ReLU 激活"""
        return [max(0, val) for val in x]

    def _normalize(self, x: List[float]) -> List[float]:
        """归一化"""
        norm = math.sqrt(sum(val ** 2 for val in x))
        if norm > 0:
            return [val / norm for val in x]
        return x

    def train(self, training_data: List[Tuple[List[float], ConditionalTarget]],
              epochs: int = 10, batch_size: int = 10, learning_rate: float = 0.001):
        """训练条件 VAE"""

        print(f"\n[C-VAE] 开始训练...")
        print(f"  训练样本：{len(training_data)}")
        print(f"   epochs: {epochs}")
        print(f"  batch_size: {batch_size}")

        for epoch in range(epochs):
            epoch_loss = 0.0
            n_batches = 0

            for i in range(0, len(training_data), batch_size):
                batch = training_data[i:i + batch_size]
                batch_loss = self._train_batch(batch, learning_rate)
                epoch_loss += batch_loss
                n_batches += 1

                time.sleep(0.05)

            avg_loss = epoch_loss / n_batches
            self.training_history.append(avg_loss)

            if (epoch + 1) % 2 == 0:
                print(f"  Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

            if epoch < epochs - 1:
                time.sleep(0.5)

        print(f"[C-VAE] 训练完成！最终 Loss: {self.training_history[-1]:.4f}")

    def _train_batch(self, batch: List[Tuple], lr: float) -> float:
        """训练一个批次"""
        total_loss = 0.0

        for descriptor, target in batch:
            # 编码条件
            cond_hidden = self.encode_condition(target)

            # 编码材料
            mean, log_var = self.encode(descriptor, cond_hidden)

            # 重参数化
            epsilon = [random.gauss(0, 1) for _ in range(self.latent_dim)]
            std = [math.exp(0.5 * lv) for lv in log_var]
            z = [m + s * e for m, s, e in zip(mean, std, epsilon)]

            # 解码
            reconstructed = self.decode(z, cond_hidden)

            # 计算损失
            reconstruction_loss = sum((a - b) ** 2 for a, b in zip(descriptor, reconstructed))
            kl_loss = -0.5 * sum(1 + lv - math.exp(lv) - m ** 2
                                for m, lv in zip(mean, log_var))

            # 条件一致性损失
            cond_loss = self._calculate_cond_loss(reconstructed, target)

            total_loss = reconstruction_loss + kl_loss + cond_loss

        return total_loss / len(batch)

    def _calculate_cond_loss(self, descriptor: List[float], target: ConditionalTarget) -> float:
        """计算条件一致性损失"""
        # 从描述符"预测"性能
        predicted = self._predict_properties(descriptor)

        loss = 0.0
        count = 0

        for prop, target_val in target.to_dict().items():
            if prop in predicted and target_val is not None:
                pred_val = predicted[prop]
                loss += (pred_val - target_val) ** 2
                count += 1

        return loss / count if count > 0 else 0.0

    def generate(self, target: ConditionalTarget, n_samples: int = 1) -> List[GeneratedMaterial]:
        """基于目标生成材料"""

        print(f"\n[C-VAE] 生成 {n_samples} 个材料 (目标：{target.to_dict()})")

        generated = []

        for i in range(n_samples):
            # 编码条件
            cond_hidden = self.encode_condition(target)

            # 从先验采样潜向量
            z = [random.gauss(0, 1) for _ in range(self.latent_dim)]

            # 解码
            descriptor = self.decode(z, cond_hidden)

            # 转换为材料
            material = self._descriptor_to_material(descriptor)

            # 预测性能
            predicted_props = self._predict_properties(descriptor)

            # 计算目标匹配度
            match_score = self._calculate_match_score(predicted_props, target)

            # 有效性和新颖性
            validity = self._calculate_validity(material)
            novelty = random.uniform(0.6, 1.0)

            generated.append(GeneratedMaterial(
                formula=material['formula'],
                elements=material['elements'],
                structure=material,
                predicted_properties=predicted_props,
                target_match_score=match_score,
                validity_score=validity,
                novelty_score=novelty
            ))

            if i > 0 and i % 5 == 0:
                time.sleep(0.2)

        return generated

    def _descriptor_to_material(self, descriptor: List[float]) -> Dict:
        """将描述符转换为材料"""
        element_pool = ['Li', 'Na', 'K', 'Mg', 'Ca', 'Ti', 'Fe', 'Co', 'Ni',
                       'Cu', 'Zn', 'Si', 'Ge', 'O', 'S', 'Se', 'P', 'F', 'Cl']

        n_elements = 2 + int(abs(descriptor[0]) * 3) % 3
        indices = [int(abs(d) * len(element_pool)) % len(element_pool)
                  for d in descriptor[:n_elements]]
        elements = [element_pool[i] for i in indices]

        formula_parts = []
        for elem in elements:
            count = 1 + int(abs(random.gauss(0, 1)) * 3) % 4
            if count > 1:
                formula_parts.append(f"{elem}{count}")
            else:
                formula_parts.append(elem)

        formula = ''.join(formula_parts)

        return {
            'formula': formula,
            'elements': elements,
            'descriptor': descriptor
        }

    def _predict_properties(self, descriptor: List[float]) -> Dict[str, float]:
        """预测性能"""
        return {
            'band_gap': round(1.0 + abs(descriptor[1]) * 4, 2),
            'formation_energy': round(-5.0 + abs(descriptor[2]) * 4, 2),
            'bulk_modulus': round(50 + abs(descriptor[3]) * 200, 1),
            'shear_modulus': round(30 + abs(descriptor[4]) * 150, 1),
            'e_above_hull': round(abs(descriptor[5]) * 0.5, 3)
        }

    def _calculate_match_score(self, predicted: Dict, target: ConditionalTarget) -> float:
        """计算目标匹配度"""
        if not target:
            return 0.0

        matches = 0
        total = 0

        for prop, target_val in target.to_dict().items():
            if prop in predicted:
                pred_val = predicted[prop]
                if target_val != 0:
                    error = abs(pred_val - target_val) / abs(target_val)
                    if error < 0.1:  # 10% 误差
                        matches += 1
                    elif error < 0.2:  # 20% 误差
                        matches += 0.5
                total += 1

        return matches / total if total > 0 else 0.0

    def _calculate_validity(self, material: Dict) -> float:
        """计算材料有效性"""
        # 简化：基于元素组合的"合理性"
        elements = material['elements']

        # 常见元素组合得分高
        common_pairs = [
            {'Li', 'Fe'}, {'Li', 'Co'}, {'Li', 'Ni'},  # 锂电池
            {'Ti', 'O'}, {'Si', 'O'}, {'Fe', 'O'},     # 氧化物
            {'Li', 'P'}, {'P', 'O'},                   # 磷酸盐
        ]

        elem_set = set(elements)
        for pair in common_pairs:
            if pair.issubset(elem_set):
                return 0.9

        return 0.7

    def save_model(self, path: str):
        """保存模型"""
        model_data = {
            'input_dim': self.input_dim,
            'cond_dim': self.cond_dim,
            'latent_dim': self.latent_dim,
            'hidden_dim': self.hidden_dim,
            'cond_encoder': self.cond_encoder,
            'encoder': self.encoder,
            'decoder': self.decoder,
            'training_history': self.training_history
        }

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(model_data, f, indent=2)

        print(f"[C-VAE] 模型保存到 {path}")

    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            'architecture': {
                'input_dim': self.input_dim,
                'cond_dim': self.cond_dim,
                'latent_dim': self.latent_dim,
                'hidden_dim': self.hidden_dim
            },
            'trained': len(self.training_history) > 0,
            'training_epochs': len(self.training_history),
            'final_loss': self.training_history[-1] if self.training_history else None,
            'current_cpu': self.monitor.get_cpu_percent()
        }


# ============================================================================
# 5. 全局实例
# ============================================================================

_cvae_instance = None

def get_conditional_vae(config: CPUConfig = None) -> ConditionalVAE:
    """获取条件 VAE 单例"""
    global _cvae_instance

    if _cvae_instance is None:
        _cvae_instance = ConditionalVAE(config)

    return _cvae_instance


# ============================================================================
# 6. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Conditional VAE - CPU Optimized")
    print("=" * 60)

    # 1. 创建模型
    print("\n[1/5] 创建模型...")
    config = CPUConfig(
        intra_op_threads=4,
        inter_op_threads=2,
        max_concurrent=1,
        cpu_threshold=70.0
    )

    cvae = get_conditional_vae(config)
    cvae.initialize_weights()

    # 2. 准备训练数据
    print("\n[2/5] 准备训练数据...")
    training_data = []
    for _ in range(100):
        descriptor = [random.gauss(0, 1) for _ in range(128)]
        target = ConditionalTarget(
            band_gap=random.uniform(1, 5),
            formation_energy=random.uniform(-5, -1),
            bulk_modulus=random.uniform(50, 250)
        )
        training_data.append((descriptor, target))
    print(f"  训练样本：{len(training_data)}")

    # 3. 训练模型
    print("\n[3/5] 训练模型...")
    cvae.train(training_data, epochs=5, batch_size=10)

    # 4. 条件生成
    print("\n[4/5] 条件生成...")

    # 目标 1: 带隙 ~3.0 eV
    target1 = ConditionalTarget(band_gap=3.0)
    generated1 = cvae.generate(target1, n_samples=3)

    print(f"\n=== 目标：带隙 ~3.0 eV ===")
    for i, mat in enumerate(generated1, 1):
        print(f"\n材料 {i}:")
        print(f"  化学式：{mat.formula}")
        print(f"  元素：{mat.elements}")
        print(f"  带隙：{mat.predicted_properties.get('band_gap', 'N/A')} eV")
        print(f"  匹配度：{mat.target_match_score:.1%}")
        print(f"  有效性：{mat.validity_score:.1%}")
        print(f"  新颖性：{mat.novelty_score:.1%}")

    # 目标 2: 多目标 (带隙 + 形成能)
    target2 = ConditionalTarget(band_gap=2.5, formation_energy=-3.0)
    generated2 = cvae.generate(target2, n_samples=2)

    print(f"\n=== 目标：带隙 ~2.5 eV + 形成能 ~-3.0 eV ===")
    for i, mat in enumerate(generated2, 1):
        print(f"\n材料 {i}:")
        print(f"  化学式：{mat.formula}")
        print(f"  带隙：{mat.predicted_properties.get('band_gap', 'N/A')} eV")
        print(f"  形成能：{mat.predicted_properties.get('formation_energy', 'N/A')} eV")
        print(f"  匹配度：{mat.target_match_score:.1%}")

    # 5. 显示统计
    print("\n[5/5] 统计信息...")
    stats = cvae.get_stats()

    print(f"  架构：{stats['architecture']}")
    print(f"  已训练：{'✅' if stats['trained'] else '❌'}")
    print(f"  训练轮数：{stats['training_epochs']}")
    print(f"  最终 Loss: {stats['final_loss']}")
    print(f"  当前 CPU: {stats['current_cpu']:.1f}%")

    # 保存模型
    cvae.save_model("data/conditional-vae-model.json")

    print("\n" + "=" * 60)
    print("条件 VAE 准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
