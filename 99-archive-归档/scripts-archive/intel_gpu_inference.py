#!/usr/bin/env python3
"""
Intel GPU 推理 - 使用 OpenVINO 在 Intel Arc GPU 上运行

支持 Qwen3.5-2B 等模型
"""

from openvino import Core, compile_model
import numpy as np
from pathlib import Path
import json


class IntelGPUPipeline:
    """Intel GPU 推理管道"""
    
    def __init__(self, model_path: str, device: str = 'GPU'):
        """
        初始化推理管道
        
        Args:
            model_path: 模型路径 (OV IR 格式或 HF 格式)
            device: 设备类型 ('CPU', 'GPU', 'NPU')
        """
        self.core = Core()
        self.device = device
        self.model_path = Path(model_path)
        self.compiled_model = None
        
        # 检测设备支持
        self.available_devices = self.core.available_devices
        print(f"可用设备：{self.available_devices}")
        
        if device not in self.available_devices:
            print(f"警告：{device} 不可用，回退到 CPU")
            self.device = 'CPU'
    
    def load_model(self):
        """加载模型"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型不存在：{self.model_path}")
        
        # 检查是否为 OpenVINO IR 格式
        xml_file = self.model_path / "openvino_model.xml"
        if xml_file.exists():
            # OpenVINO IR 格式
            print(f"从 {xml_file} 加载 OpenVINO 模型...")
            self.compiled_model = self.core.compile_model(xml_file, self.device)
        else:
            # 需要转换 HuggingFace 模型
            print(f"需要转换 HuggingFace 模型...")
            self.compiled_model = self._convert_and_compile()
        
        print(f"模型已加载到 {self.device}")
    
    def _convert_and_compile(self):
        """转换并编译 HuggingFace 模型"""
        try:
            from optimum.intel import OVModelForCausalLM
            from optimum.intel.openvino import OVWeightQuantizationConfig
            
            print(f"从 {self.model_path} 加载并转换模型...")
            
            # 加载并转换模型
            ov_model = OVModelForCausalLM.from_pretrained(
                self.model_path,
                export=True,
                load_in_8bit=False,
            )
            
            # 保存到本地
            ov_save_path = self.model_path / "openvino_model"
            ov_model.save_pretrained(ov_save_path)
            
            # 编译到设备
            compiled_model = self.core.compile_model(
                ov_save_path / "openvino_model.xml",
                self.device
            )
            
            return compiled_model
            
        except ImportError:
            print("错误：需要安装 optimum-intel")
            print("运行：pip install optimum-intel openvino-tokenizers")
            raise
    
    def generate(self, prompt: str, max_length: int = 100) -> str:
        """生成文本"""
        if self.compiled_model is None:
            self.load_model()
        
        # 简单的推理逻辑
        # 实际使用需要完整的 tokenizer 和解码逻辑
        print(f"在 {self.device} 上生成...")
        
        # 这里是简化示例，实际需要完整的生成逻辑
        return "生成结果 (需要完整实现)"
    
    def benchmark(self, num_runs: int = 10) -> dict:
        """性能测试"""
        if self.compiled_model is None:
            self.load_model()
        
        import time
        
        # 创建虚拟输入
        dummy_input = np.random.randint(0, 1000, (1, 32), dtype=np.int32)
        
        # 预热
        _ = self.compiled_model(dummy_input)
        
        # 测试
        times = []
        for _ in range(num_runs):
            start = time.time()
            _ = self.compiled_model(dummy_input)
            times.append(time.time() - start)
        
        return {
            'device': self.device,
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'num_runs': num_runs
        }


def test_intel_gpu():
    """测试 Intel GPU"""
    print("测试 Intel GPU 推理")
    print("=" * 50)
    
    # 初始化核心
    core = Core()
    
    # 检测设备
    devices = core.available_devices
    print(f"可用设备：{devices}")
    
    # 测试每个设备
    for device in devices:
        print(f"\n测试设备：{device}")
        try:
            # 获取设备信息
            device_name = core.get_property(device, "FULL_DEVICE_NAME")
            print(f"  设备名称：{device_name}")
        except:
            print(f"  无法获取设备名称")
    
    print("\n测试完成！")


if __name__ == '__main__':
    test_intel_gpu()
