---
name: git-clean-danger
description: git clean -fd 在 workspace root 执行会递归删除所有 untracked 文件（含子目录未跟踪源码）
type: feedback
---

## 规则：禁止在 workspace root 执行 git clean -fd

**Why:** `git clean -fd` 递归强制删除所有 untracked 文件。workspace root 下的子目录（如 task-orchestrator/src/）中的未跟踪文件会被一并删除。2026-04-08 教训：task-orchestrator 全部 .mjs 源码被误删，从 submodule git 历史重建。

**How to apply:**
- 永远在具体子目录中运行 `git clean`
- 使用 `--dry-run` / `-n` 预览
- 如果必须在 root 执行，先用 `git clean -fd --dry-run` 确认范围
- 建议使用 `git alias.clean` 包装脚本（`scripts/git-hooks/git-clean-wrapper`），需手动安装到 `.git/hooks/`
