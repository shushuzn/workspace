# AI 圆桌讨论 — Cognitive Annealing 版

多人格 AI 圆桌讨论 CLI，通过动态温度调度探索观点多样性。

## 特性

- **6 人格圆桌**：乐观者、怀疑者、分析师、调和者、历史家、务实者
- **自适应温度调度**：模拟退火算法，动态调整 LLM 采样温度
- **概念跳跃测量**：ΔS = cosineDistance( roundMean_t, roundMean_{t-1} )
- **早停机制**：连续 4 轮 ΔS < 0.05 时自动结束
- **Ollama 本地嵌入**：MiniMax 余额不足时自动降级

## 快速开始

```bash
# 安装依赖
npm install

# 运行讨论（交互模式）
node index.js

# 命令行模式
node index.js "AI是否会取代人类工作"
node index.js "气候变化" -r 6 -t 1.0

# 查看帮助
node index.js --help
```

## 命令行选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-r, --rounds <N>` | 8 | 讨论轮数（最大 10） |
| `-t, --temp <T>` | 1.2 | 初始温度（最大 2.0） |
| `-h, --help` | — | 显示帮助 |

## 温度调度

- 初始温度：1.2
- 冷却率：0.88（每轮乘以 0.88）
- 最低温度：0.3
- ΔS 峰值检测：超过阈值时进入 plateau（温度不变 2 轮）
- 早停：连续 4 轮 ΔS < 0.05

## 嵌入 API

默认使用 MiniMax Embedding API。余额不足时自动降级到 Ollama 本地：

```bash
# 确保 Ollama 运行中
ollama run llama3.2:1b
```

## 输出

每轮讨论结束后保存到 `讨论_<话题>_<时间>.txt`，包含完整发言记录和退火报告。

## 项目结构

```
index.js                  # 主入口
shared/
  temperatureScheduler.js  # 温度调度器
  conceptJumpTracker.js   # ΔS 测量
  embedder.js             # 嵌入接口（MiniMax + Ollama）
  vectorUtils.js           # cosineDistance
  identityStore.js         # 跨项目身份存储（预留）
```

## 环境变量

```env
MINIMAX_API_KEY=your_key          # MiniMax API 密钥
MINIMAX_MODEL=MiniMax-M2.7-highspeed  # 聊天模型
EMBEDDER_MODEL=embedding-2        # 嵌入模型（MiniMax）
EMBEDDER_API_URL=https://api.minimaxi.com/v1/embeddings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```
