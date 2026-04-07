# Multi-modal Content Analysis Pipeline

分析视频、PDF、文章，输出结构化 Markdown。

## 使用方法

```bash
node docs/analysis/analyze.mjs <输入> [--output DIR]
```

## 支持类型

| 类型 | 示例 |
|------|------|
| 新闻/文章 URL | `node analyze.mjs https://news.example.com/article` |
| PDF 文件 | `node analyze.mjs /path/to/doc.pdf` |
| B站视频 | `node analyze.mjs https://bilibili.com/video/BVxxx` |
| YouTube视频 | `node analyze.mjs https://youtube.com/watch?v=xxx` |

## 输出

保存到 `docs/analysis/analysis-YYYY-MM-DD-TIMESTAMP.md`，包含：
- 概要（核心主题、来源类型）
- 关键内容（要点列表）
- 标签
- 原始摘要

## 示例

```bash
node docs/analysis/analyze.mjs https://www.bbc.com/news/tech
node docs/analysis/analyze.mjs ./paper.pdf --output ./output/
```
