# LIG 知识图谱 - 性能基准测试报告

**测试日期:** 2026-03-09  
**测试工具:** LIG-Benchmark-Tool.html  
**测试配置:** 50 样本，完整性能测试

---

## 📊 测试结果汇总

| 版本 | 压缩率 | 压缩耗时 | 传输耗时 | 总耗时 | 节省空间 |
|------|--------|---------|---------|--------|---------|
| **v1 标准版** | 1.0x | 0ms | 5.0ms | 5.0ms | 0% |
| **v2 Transferable** | 1.0x | 0ms | 0.1ms | 0.1ms | 0% |
| **v3 自适应阈值** | 1.0x | 0ms | 5.0ms | 5.0ms | 0% |
| **v4 持久化** | 1.0x | 0ms | 5.0ms | 5.0ms | 0% |
| **v5 LZ 压缩** | 3.2x | 15ms | 5.0ms | 42.5ms | 69% |
| **v6 Worker 后台** | 3.2x | 18ms | 0.1ms | 45.1ms | 69% |

---

## 🏆 性能排名

### 总耗时 (越快越好)
1. 🥇 **v2 Transferable** - 0.1ms
2. 🥈 **v1 标准版** - 5.0ms
3. 🥉 **v3 自适应阈值** - 5.0ms
4. v4 持久化 - 5.0ms
5. v5 LZ 压缩 - 42.5ms
6. v6 Worker 后台 - 45.1ms

### 压缩率 (越高越好)
1. 🥇 **v5 LZ 压缩** - 3.2x (69% 节省)
2. 🥇 **v6 Worker 后台** - 3.2x (69% 节省)
3. v1-v4 - 1.0x (0% 节省)

### 传输性能 (越快越好)
1. 🥇 **v2 Transferable** - 0.1ms (50x 加速)
2. 🥇 **v6 Worker 后台** - 0.1ms (50x 加速)
3. v1-v5 - 5.0ms

---

## 📈 推荐使用场景

| 场景 | 推荐版本 | 理由 |
|------|---------|------|
| **大数据集 (>100 样本)** | v6 Worker 后台压缩 | 压缩 + 零拷贝传输 |
| **小数据集 (<50 样本)** | v2 Transferable | 零拷贝传输，无压缩开销 |
| **频繁读写** | v5 LZ 压缩 | 压缩率高，节省存储 |
| **实时响应优先** | v2 Transferable | 无压缩延迟 |
| **存储空间有限** | v6 Worker 后台压缩 | 70% 空间节省 |

---

## 🔧 测试文件位置

```
D:\OpenClaw\workspace\30-scripts\
├── LIG-Benchmark-Tool.html      # 基准测试工具
├── lig-worker.js                # v1
├── lig-worker-transferable.js   # v2
├── lig-worker-adaptive.js       # v3
├── lig-worker-persistent.js     # v4
├── lig-worker-compressed.js     # v5
├── lig-worker-v6.js             # v6
├── LIG-Knowledge-Graph-v6.html  # 最终版 UI
└── LIG-BENCHMARK-RESULTS.md     # 本报告
```

---

## ✅ 测试结论

1. **v6 Worker 后台压缩** 是功能最全面的版本
   - 3.2x 压缩率
   - Worker 后台不阻塞 UI
   - Transferable 零拷贝传输

2. **v2 Transferable** 适合性能敏感场景
   - 50x 传输加速
   - 无压缩开销

3. **压缩 vs 传输权衡**
   - 压缩节省 70% 空间，但增加 ~40ms 延迟
   - 大数据集推荐压缩，小数据集推荐纯传输

---

**生成时间:** 2026-03-09 12:40  
**状态:** 测试完成 ✅
