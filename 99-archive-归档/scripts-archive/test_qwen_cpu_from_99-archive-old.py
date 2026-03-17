#!/usr/bin/env python3
"""使用 CPU 测试 Qwen3.5-2B 推理"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time

model_path = "D:/AI-Models/Qwen3.5-2B"

print("="*60)
print("Qwen3.5-2B CPU 推理测试")
print("="*60)

print(f"\n加载模型：{model_path}")
print("首次加载需要 2-5 分钟...")

# 加载 tokenizer
print("\n加载 tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
print("✅ Tokenizer 加载成功")

# 加载模型 (CPU)
print("\n加载模型到 CPU...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    device_map="cpu",
    torch_dtype=torch.float32
)
print("✅ 模型加载成功")

# 推理测试
print("\n推理测试...")
prompt = "你好，请介绍一下你自己"

inputs = tokenizer(prompt, return_tensors="pt")
input_len = inputs['input_ids'].shape[1]

print(f"输入长度：{input_len} tokens")
print(f"生成中...")

start = time.time()
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    do_sample=False
)
infer_time = time.time() - start

# 解码
output_text = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)

print(f"\n生成完成！")
print(f"推理时间：{infer_time:.2f}秒")
print(f"生成速度：{50/infer_time:.1f} tokens/秒")
print(f"\n生成内容:\n{output_text}")

print(f"\n✅ CPU 推理测试成功！")
