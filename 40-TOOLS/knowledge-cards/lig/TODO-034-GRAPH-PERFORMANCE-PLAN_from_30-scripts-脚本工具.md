# 多模态图谱性能优化计划

**任务 ID:** todo-034  
**优先级:** 🟡 MEDIUM  
**预计时间:** 1-2 周  
**创建日期:** 2026-03-10  
**状态:** 进行中

---

## 📋 任务描述

实现分页加载、虚拟滚动和 WebGL 渲染，支持 1000+ 图表秒级加载。

---

## 🎯 验收标准

| 标准 | 目标 | 验证方法 |
|------|------|----------|
| 分页加载 | ✅ 完成 | 支持 100/页 |
| 虚拟滚动 | ✅ 完成 | 仅渲染可见节点 |
| WebGL 渲染 | ✅ 完成 | GPU 加速 |
| 加载时间 | <1 秒 | 性能测试 |
| 用户体验 | ✅ 通过 | 交互流畅 |

---

## 📚 技术方案

### 方案 A: D3.js + WebGL (推荐)

**优势:**
- 成熟的知识图谱可视化库
- 支持力导向布局
- WebGL 加速渲染

**技术栈:**
- D3.js v7 (力导向图)
- regl (WebGL 封装)
- 虚拟滚动 (自定义实现)

### 方案 B: Three.js + Force Graph

**优势:**
- 3D 支持
- 大规模图渲染优化
- 交互丰富

### 方案 C: ECharts GL

**优势:**
- 配置简单
- 性能优秀
- 中文文档

---

## 📁 文件结构

```
30-scripts/graph-optimizer/
├── README.md                    # 使用文档
├── config.yaml                  # 配置文件
├── graph_data_loader.py         # 数据加载器
├── graph_renderer.html          # WebGL 渲染器
├── virtual_scroll.js            # 虚拟滚动
├── pagination.js                # 分页逻辑
├── test_suite/                  # 测试集
│   ├── small_graph.json         # 小型图谱 (<100 节点)
│   ├── medium_graph.json        # 中型图谱 (100-500 节点)
│   └── large_graph.json         # 大型图谱 (>1000 节点)
├── benchmarks/                  # 性能基准
│   └── performance_report.md
└── examples/                    # 使用示例
    └── demo.html
```

---

## 📊 性能优化策略

### 1. 分页加载
```javascript
class GraphPagination {
  constructor(data, pageSize = 100) {
    this.data = data;
    this.pageSize = pageSize;
    this.currentPage = 0;
  }
  
  getPage(page) {
    const start = page * this.pageSize;
    const end = start + this.pageSize;
    return this.data.nodes.slice(start, end);
  }
  
  getTotalPages() {
    return Math.ceil(this.data.nodes.length / this.pageSize);
  }
}
```

### 2. 虚拟滚动
```javascript
class VirtualScroll {
  constructor(container, renderItem) {
    this.container = container;
    this.renderItem = renderItem;
    this.scrollTop = 0;
    this.visibleRange = { start: 0, end: 0 };
    
    container.addEventListener('scroll', () => this.onScroll());
  }
  
  onScroll() {
    this.scrollTop = this.container.scrollTop;
    this.updateVisibleRange();
    this.render();
  }
  
  updateVisibleRange() {
    const itemHeight = 50; // 假设每项 50px
    const visibleCount = Math.ceil(this.container.clientHeight / itemHeight);
    const startIndex = Math.floor(this.scrollTop / itemHeight);
    
    this.visibleRange = {
      start: Math.max(0, startIndex - 5),  // 预加载 5 项
      end: startIndex + visibleCount + 5
    };
  }
  
  render() {
    // 仅渲染可见范围内的节点
  }
}
```

### 3. WebGL 渲染
```javascript
// 使用 regl 进行 WebGL 渲染
const regl = require('regl')();

const drawNodes = regl({
  vert: `
    precision mediump float;
    attribute vec2 position;
    uniform float scale;
    void main() {
      gl_Position = vec4(position * scale, 0, 1);
    }
  `,
  frag: `
    precision mediump float;
    uniform vec3 color;
    void main() {
      gl_FragColor = vec4(color, 1);
    }
  `,
  attributes: {
    position: ({ nodePositions }) => nodePositions
  },
  uniforms: {
    scale: ({ viewport }) => 2 / viewport.width
  },
  count: ({ nodeCount }) => nodeCount
});
```

---

## 📈 实施步骤

### Week 1: 基础功能
- [ ] Day 1-2: 分页加载实现
- [ ] Day 3-4: 虚拟滚动实现
- [ ] Day 5: WebGL 渲染基础

### Week 2: 优化与测试
- [ ] Day 6-7: 力导向布局优化
- [ ] Day 8-9: 性能基准测试
- [ ] Day 10: 文档完善

---

## 📏 性能基准

### 测试数据集
| 数据集 | 节点数 | 边数 | 大小 |
|--------|--------|------|------|
| Small | 50 | 100 | 10KB |
| Medium | 500 | 2000 | 100KB |
| Large | 2000 | 10000 | 500KB |
| XLarge | 10000 | 50000 | 2MB |

### 性能目标
| 操作 | 目标时间 | 当前时间 |
|------|----------|----------|
| 初始加载 (Large) | <1 秒 | - |
| 分页切换 | <100ms | - |
| 节点拖拽 | 60fps | - |
| 缩放/平移 | 60fps | - |
| 搜索过滤 | <500ms | - |

---

## 🔗 相关资源

- [D3.js](https://d3js.org/)
- [regl](http://regl.party/)
- [Three.js](https://threejs.org/)
- [ECharts GL](https://echarts.apache.org/zh/extension.html#echarts-gl)

---

## 📝 进度日志

### 2026-03-10
- ✅ 任务规划完成
- ✅ 技术方案确定
- ✅ 性能优化策略设计
- ⏸️ 等待实现

---

*最后更新：2026-03-10*
