# Intel Arc GPU 运行 Qwen3.5-2B 指南

## 当前状态

✅ OpenVINO 已安装
✅ Intel Arc GPU 已检测
✅ 性能测试完成 (GPU 最快)
❌ 模型需转换为 OpenVINO 格式
❌ optimum-intel 未安装

## 性能测试结果

| 设备 | 速度 | 排名 |
|------|------|------|
| **GPU (Intel Arc)** | 0.0077 秒 | 🥇 最快 |
| **NPU (AI Boost)** | 0.0111 秒 | 🥈 |
| **CPU** | 0.0116 秒 | 🥉 |

## 下一步

### 1. 安装依赖 (10-20 分钟)

```bash
py install_requirements.py
```

或手动安装:
```bash
py -m pip install optimum-intel openvino-tokenizers
```

### 2. 转换模型 (5-10 分钟)

```bash
py convert_to_openvino.py D:/AI-Models/Qwen3.5-2B
```

### 3. GPU 推理测试

```bash
py run_qwen_gpu.py
```

### 4. 集成到信号提取器

修改 `auto_signal_extractor.py`:
```python
from run_qwen_gpu import load_to_gpu, simple_inference

# 加载模型到 GPU
model = load_to_gpu(model_xml)

# 使用 GPU 进行信号分析
signal = analyze_with_gpu(user_reply, model)
```

## 预期效果

**转换后:**
- GPU 推理速度：~10-30 tokens/秒
- 信号提取时间：<1 秒
- 对话响应：实时

## 故障排除

### 问题 1: optimum-intel 安装失败

**解决:**
```bash
py -m pip install --upgrade pip
py -m pip install optimum-intel --pre
```

### 问题 2: 模型转换失败

**解决:**
```bash
# 检查磁盘空间
# 确保 D: 盘有足够空间 (至少 10GB)
```

### 问题 3: GPU 加载失败

**解决:**
```bash
# 更新 Intel 显卡驱动
# 访问 Intel 官网下载最新驱动
```
