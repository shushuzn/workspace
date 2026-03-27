# Star Forge — 赛季系统设计文档

## 概述

为 `star-forge-web` 设计一套赛季制 + 赛季通行证机制，作为现有放置游戏的长留存驱动。

**核心原则**：
- 赛季数据与主存档完全隔离，不影响现有游戏数据
- 轻量优先，先跑通核心循环，后续易扩展到后端
- 功能性特权赛季奖励，赛季结束绝版，制造稀缺感

---

## 赛季周期

- **每月1日 00:00 UTC** 自动开启新赛季
- 赛季 ID 格式：`"2026-04"`（YYYY-MM）
- 赛季结束自动归档，玩家进度清零，开始新赛季
- 所有玩家同步同一个赛季日历

---

## 数据结构

### 赛季存档（独立 key）

存储位置：`localStorage key = "starforge_season"`

```typescript
interface SeasonState {
  seasonId: string;          // "2026-04"
  chapter: number;           // 当前章节 1-3
  tasks: SeasonTask[];
  rewards: SeasonReward[];
  freeProgress: number;      // 免费通行证进度 (0-100)
  premiumProgress: number;   // 高级通行证进度 (0-100)
  premiumOwned: boolean;      // 是否拥有高级通行证
  startTime: number;         // UTC 毫秒时间戳
  endTime: number;          // UTC 毫秒时间戳
  lastSaved: number;         // 最后保存时间戳
}

interface SeasonTask {
  id: string;
  type: 'auto' | 'manual';  // auto = 后台自动追踪, manual = 需玩家主动触发
  category: 'build' | 'click' | 'prestige' | 'special';
  title: string;            // 任务名称
  description: string;
  target: number;           // 目标值
  progress: number;          // 当前进度
  claimed: boolean;          // 是否已领奖
}

interface SeasonReward {
  id: string;
  chapter: number;           // 属于哪个章节
  tier: 'free' | 'premium'; // 通行证层
  type: 'resource' | 'buff' | 'skin' | 'feature';
  name: string;
  description: string;
  claimed: boolean;
  unlockAt: number;         // 进度阈值
}
```

---

## 赛季章节

每个赛季包含 **3个章节**，每章有独立主题、任务线、奖励。

### 第1章「星辰苏醒」

- **主题**：建造基础
- **任务**：
  1. 建造任意5个不同建筑（auto, build）
  2. 累计生产 10,000 资源（auto, produce）
  3. 升级任意建筑到10级（manual, build）
- **免费奖励**：500 游戏货币、经验药水 x3
- **高级奖励**：+5% 离线收益永久加成（buff）、高级皮肤箱 x1

### 第2章「星际征途」

- **主题**：活跃参与
- **任务**：
  1. 累计点击 500 次（manual, click）
  2. 使用加速道具 10 次（manual, use-item）
  3. 完成5次每日挑战（auto, daily）
- **免费奖励**：1000 游戏货币、加速药水 x5
- **高级奖励**：+10% 点击加成永久加成（buff）、新功能解锁（仓库容量+20）

### 第3章「宇宙主宰」

- **主题**：终极挑战
- **任务**：
  1. 完成一次声望重置（manual, prestige）
  2. 收集 100 颗成就星（auto, achievement）
  3. 在赛季结束前达到章节3（auto, progress）
- **免费奖励**：2000 游戏货币、限定头像框
- **高级奖励**：赛季专属「星环」建筑皮肤（外观）、称号「宇宙主宰」

---

## 通行证机制

### 进度系统

- 任务完成后获得进度点数（每任务 10-30 点）
- 免费层：完成任务自动获得进度，解锁免费奖励
- 高级层：需要玩家主动购买高级通行证（游戏内货币购买），解锁高级奖励

### 奖励领取

- **基础奖励（免费层）**：自动发放到背包/直接到账，无需手动操作
- **高阶奖励（高级层）**：需玩家在赛季界面手动点击领取

### 高级通行证定价

- **游戏内货币**：5000 星尘（游戏已有货币）
- 后续可扩展为付费（预留字段 `premiumPurchased`）

---

## UI 设计

### 入口

- 主界面底部导航栏新增「赛季」按钮（太阳/星星图标）
- 有进行中赛季时显示红点提示 + 当前章节编号

### 赛季主界面（SeasonPanel）

```
┌─────────────────────────────────────┐
│  赛季 2026-04        剩余 12 天      │
│  ══════════════════════════════════  │
│                                     │
│  第1章「星辰苏醒」  ✅ 已完成          │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░  80/100      │
│                                     │
│  第2章「星际征途」  🔄 进行中          │
│  ▓▓▓▓▓▓░░░░░░░░░░░░  30/100       │
│                                     │
│  第3章「宇宙主宰」  🔒 未解锁          │
│  ▓░░░░░░░░░░░░░░░░░  0/100         │
│                                     │
│  ─────────────────────────────────  │
│  任务        奖励        排行榜       │
│  [当前Tab: 任务]                      │
│                                     │
│  ┌─ 章节1任务 ─────────────────────┐ │
│  │ ☐ 建造5个不同建筑   [0/5]      │ │
│  │ ☐ 累计生产10000资源 [3200/10000]│ │
│  │ ☑ 升级建筑到10级   [已完成]     │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 奖励面板

```
┌─ 免费奖励 ──────────────────────────┐
│  ☑ 500 游戏货币      [已领取]       │
│  ☑ 经验药水 x3       [已领取]       │
│  🔓 +5% 离线收益     [可领取!]  ← 点击│
└─────────────────────────────────────┘
┌─ 高级奖励 ──────────────────────────┐
│  🔒 +10% 点击加成   [进度 30/100]   │
│  🔒 仓库容量+20      [进度 30/100]   │
│  🔒 赛季专属皮肤     [进度 80/100]   │
│                                     │
│  [购买高级通行证 - 5000 星尘]        │
└─────────────────────────────────────┘
```

---

## 赛季判定逻辑

### 自动检测

```javascript
// 每次游戏加载时检测是否需要开启新赛季
function checkAndInitSeason() {
  const now = Date.now();
  const state = loadSeasonState();
  const seasonId = getCurrentSeasonId(); // "2026-04"

  if (!state || state.seasonId !== seasonId) {
    // 开启新赛季，归档旧数据
    archiveSeason(state);
    initNewSeason(seasonId);
  }
}
```

### 赛季结束检测

```javascript
function isSeasonEnded(endTime) {
  return Date.now() > endTime;
}
```

---

## 持久化策略

| 数据 | 存储位置 | 频率 |
|------|---------|------|
| 赛季进度 | `localStorage.starforge_season` | 每分钟 + 关键操作 |
| 赛季任务进度 | 同上 | 每次进度变化时 |
| 已领取奖励记录 | 同上 | 每次领取时 |

> **注意**：与主存档 `localStorage.starforge_save` 完全独立，互不影响。

---

## 文件改动范围

### 新增文件

```
src/components/
  SeasonPanel.jsx           # 赛季主界面
  SeasonPanel.module.css
  SeasonTaskItem.jsx        # 任务条目组件
  SeasonRewardItem.jsx      # 奖励条目组件
  SeasonChapterProgress.jsx  # 章节进度条

src/hooks/
  useSeason.js              # 赛季状态管理 hook

src/store/
  SeasonContext.jsx         # 赛季独立 Context

src/data/
  seasonTasks.js            # 赛季任务配置
  seasonRewards.js          # 赛季奖励配置
```

### 修改文件

```
src/App.jsx                  # 注入 SeasonContext
src/components/TabPanel.jsx  # 赛季入口按钮
src/components/GameBoard.jsx # 赛季数据 onSave 时同步
src/hooks/useSaveLoad.js     # 保存时同时持久化赛季数据
```

---

## 实现优先级

1. **Phase 1（核心循环）**：赛季数据模型、赛季加载/重置逻辑、基础 UI
2. **Phase 2（任务系统）**：任务追踪（auto + manual）、进度计算、奖励领取
3. **Phase 3（高级通行证）**：购买逻辑、高级奖励解锁
4. **Phase 4（赛季结束）**：结算、归档、数据展示

---

## 后续扩展方向

- **后端持久化**：接 Vercel Blob 或 Upstash Redis 支持跨设备同步
- **赛季排行榜**：联盟贡献积分排行
- **赛季商城**：用赛季代币兑换限定内容
- **赛季回顾**：赛季结束时的数据总结页面
