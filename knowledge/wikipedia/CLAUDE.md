# Wikipedia 知识库项目规范

> 版本：v1.6 | 更新日期：2026-04-07

## 项目定位

维基百科风格知识库，用 Obsidian 作为编辑器。核心资产是 `articles/` 下的知识点条目（.md 文件），通过 `[[wiki-link]]` 互相引用形成知识网络。

## 目录结构

```
wikipedia/
├── wiki.mjs              # 主CLI工具（create/ingest/sync/search等）
├── index.json            # 条目索引（自动生成）
├── index.html            # 百科首页（自动生成）
├── articles/             # 条目Markdown文件（按知识点文件夹组织）
│   ├── math/             # 数学类
│   ├── security/         # 安全类
│   └── ai/              # AI类
│   └── */NN-标题-阅读文案.txt          # 干净阅读文案（无frontmatter/画面标注）
│   └── */NN-标题-阅读文案-speech.txt   # 送入TTS的文本（数学符号已替换）
│   └── */NN-标题.mp3                   # 语音
│   └── */NN-标题.mp4                   # 视频
│   └── */NN-标题/                      # 视频打包目录
│       └── NN-标题论文解读.mp4          # 打包的视频
│       └── 标题简介.md                  # 打包的简介
├── video/               # 视频生产流水线源码
│   ├── draw_scene.py    # 配图生成（matplotlib，白板风格）
│   ├── generate_speech.py  # 语音合成（edge-tts，zh-CN-XiaoyiNeural）
│   ├── make_video.py   # 视频合成（imageio-ffmpeg + PIL，多画面按时序切换）
│   ├── package_videos.py  # 视频打包脚本
│   └── fig-*.png        # 通用配图
├── stubs/               # API/函数存根
├── concept-similarity-api.mjs  # 概念相似度API
└── embed-cluster.mjs    # 嵌入聚类
```

## 核心工作流

### arXiv 论文 ingest

```bash
node wiki.mjs ingest <arxiv-url>   # API获取元数据 → 生成带引导章节的笔记骨架
node wiki.mjs edit <标题>           # Obsidian中人工填充"研究动机/核心方法/关键发现/个人评价"
node wiki.mjs sync                  # 同步索引，检测wiki-link断链
```

### 视频生产流水线

### 半自动化模式（批量）
```bash
python video/pipeline.py --dir articles --batch 5 --workers 4 --resume
```
- 增量缓存：SHA256 hash 跳过未变更的 speech/mp3/scene/mp4
- 断点续传：失败后可 --resume 从中断处继续
- 质量门禁前置：文案质检（issues 或 <60分）阻塞生成
- 批量队列：超过 5 个时分批处理
- 质量报告：`.video-cache/reports/` 下生成 JSON 报告

### 质量监控（pipeline.py 内置）

| 阶段 | 检查项 | 阻塞 |
|------|--------|------|
| Step 0 文案质检 | 数学符号替换、可读性（句长/逗号密度）、学术腔 | BLOCK |
| Step 2.5 音频质检 | 时长、码率、采样率、声道 | WARN |
| Step 4.5 视频质检 | 分辨率、帧率、编码器、音频流 | WARN（无音频/编码错误 BLOCK） |

### 手动模式（单篇精修）
1. `node wiki.mjs edit <标题>` 编辑带 frontmatter 和 `[画面：]` 标注的视频脚本（01-xxx.md）
2. **手动**：去掉 frontmatter 和所有 `[画面：...]` 行，保存为 `NN-标题-阅读文案.txt`
3. **手动**：替换文案中 Unicode 数学符号为可读英文发音（σ₁→sigma 1，λᵢ→lambda i，Yang-Baxter→杨-巴克斯特 等），保存为 `NN-标题-阅读文案-speech.txt`
4. **手动**：按上述规则创建英文专业版文案 `NN-标题-阅读文案-speech-en.txt`
5. `python video/check_script.py` 质量门禁（禁用词、术语解释、字数），不通过则修改文案
6. `python video/generate_speech.py` 生成语音 MP3（自动识别 -en 文件用 en-US-AriaNeural）
7. `python video/draw_scene.py` 生成封面图和所有配图
   - 封面图：只显示标题，不显示简介，比例 12×8
   - 配图：与文案中的 `[画面：...]` 标注一一对应，比例统一 12×8
8. `python video/make_video.py` 合成视频 MP4（多画面按时序切换，自动处理双版本）
9. `python video/package_videos.py` 打包：
   - 中文版（论文解读.mp4 + 标题简介.md）→ `dist/`
   - 英文版（论文解读-en.mp4 + Title-Introduction.md）→ `dist-en/`

### 配图规范

- **比例统一**：所有图片（封面+配图）比例均为 12×8
- **封面图**：只显示视频标题，不显示简介
- **编号规则**：配图编号与视频文案编号一一对应，存放在各知识点目录下，与 MP3 同级
- **绘制函数**：`draw_scene.py` 中 `SCENE_DRAWERS` 字典映射 scene key 到对应 draw 函数

### 知识条目维护

```bash
node wiki.mjs sync            # 从磁盘扫描重建index.json，检测断链
node wiki.mjs linkcheck       # 检测断链
node wiki.mjs backlinks <标题> # 查询引用某条目的所有条目
node wiki.mjs orphan          # 列出孤立条目（无引用）
node wiki.mjs search <query>  # 搜索
```

## 视频打包规则

视频完成后，在对应论文目录下创建 `NN-标题/` 子文件夹，打包以下两个文件：
- `NN-标题论文解读.mp4` — 视频文件
- `标题简介.md` — 纯文本简介，格式如下：

```
零参数跨域泛化——拓扑数学在云安全的新突破

简介

论文：Out-of-Domain Stress Test for Temporal Braid Group Privilege Escalation Detection
作者：Christophe Parisel | arXiv：2604.02366

在云身份与访问管理（IAM）系统中...
（正文）
```

**注意：**
- 文件名：`标题简介.md`（固定格式）
- 论文和作者放在"简介"标签下面
- 纯文本，无 `#` 标题标记，无 `**` 粗体标记
- 打包脚本：`python video/package_videos.py`

## 知识点提取规则

从论文笔记拆出独立知识点条目（如数学概念、安全术语），在相关条目中添加 `[[wiki-link]]` 互相引用。知识点命名：用简洁的中文术语，不用英文缩写。

## 视频脚本结构（frontmatter）

```yaml
---
title: 标题
duration: ~3min
style: 轻松
target_audience: 科普观众
---
# 章节标题

正文内容（口语化，科普风格）
[画面：具体描述]  ← 视频脚本标注，不朗读
```

## Git 规范

所有改动必须在 24 小时内提交（单文件改动可直接 commit，多文件批量修复 commit 前先 `git add`）。commit message 格式：

```
<type>(<scope>): <subject>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

类型：feat / fix / refactor / docs / test / chore

## 禁止事项

- arXiv 论文不得用 LLM summarization，必须走 API 获取元数据
- 视频文案不得包含 `[画面：...]` 等非朗读内容
- 数学符号（σ、λ、下标）必须替换为可读英文再送入 TTS
- 视频文案不得使用"本论文/本文/该论文"等学术腔，用科普讲解腔替代
- 封面图不得包含简介内容，只需标题
- 所有图片比例必须统一为 12×8
- **brainstorm 暂停规则**：用户说"暂停头脑风暴"后，完全停止 brainstorm 空闲循环；下次 session 不自动触发 brainstorm
