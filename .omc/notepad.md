# Notepad
<!-- Auto-managed by OMC. Manual edits preserved in MANUAL section. -->

## Priority Context
<!-- ALWAYS loaded. Keep under 500 chars. Critical discoveries only. -->
⚡ brainstorm 20260409完成：8 seeds/批，4 shipped，4 remaining | run-seed新增--focus/--skip | analyze-seed新增--clean-shipped-days

⚡ INSIGHT TRIGGER: 10 tool calls (threshold 10) — generate insight from work output | Read trigger: .omc/state/auto-insight-trigger.json

⚠️ BUG FIXED: hook-auto-seed PostToolUse not firing — settings.json used `cmd /c node ...` which blocks stdin on Windows. Removed `cmd /c` wrapper. Verified: counter increments correctly.

⚠️ FIX ADDED: insight prompt now requires `omc-insight-action.mjs --add` registration for all non-N/A Fixes — closes the execute-verify闭环.

⚠️ CRITICAL: added hook-pretool-block.mjs — PreToolUse now DENIES all tools when pending-actions not empty. TRUE blocking (not advisory).

⚠️ FIX: Fix must be executable shell command, not "modify file X". | insight-effectiveness now records ALL executed Fixes (not just error-class).
⚡ ACTIVE LEARN: Bash — 创新工作触发 insight | Read trigger: .omc/state/active-learn-trigger.json
## Working Memory
<!-- Session notes. Auto-pruned after 7 days. -->

## MANUAL
<!-- User content. Never auto-pruned. -->
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:00:50.013Z
**Why**: 工具 Bash 调用失败: exit 1 — 匹配已知错误模式: rm-rf

**Better alternatives:**
  1. 用trash命令替代rm -rf

**Skill fragments to create:**
  - [rm-rf] 用trash命令替代rm -rf — 来自: rm -rf /

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:00:56.283Z
**Why**: 工具 Bash 调用失败: Permission denied — 匹配已知错误模式: rm-rf

**Better alternatives:**
  1. 用trash命令替代rm -rf

**Skill fragments to create:**
  - [rm-rf] 用trash命令替代rm -rf — 来自: rm -rf /

---
## PostTool Reflect [consecutive]

**Tool**: Read
**Time**: 2026-04-10T13:01:21.255Z
**Why**: 连续 3 次 Read 调用无实质进展

**Better alternatives:**
  1. 暂停并重新分析问题
  2. 用不同工具打破连续

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:06:02.860Z
**Why**: 工具 Bash 调用失败: exit 1 — 匹配已知错误模式: rm-rf

**Better alternatives:**
  1. 用trash命令替代rm -rf

**Skill fragments to create:**
  - [rm-rf] 用trash命令替代rm -rf ||from: rm -rf /tmp

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:06:33.139Z
**Why**: 工具 Bash 调用失败: exit 1 — 匹配已知错误模式: rm-rf

**Better alternatives:**
  1. 用trash命令替代rm -rf

**Skill fragments to create:**
  - [rm-rf] 用trash命令替代rm -rf ||from: rm -rf /tmp

---
## PostTool Reflect [error]

**Tool**: Edit
**Time**: 2026-04-10T13:16:27.648Z
**Why**: 工具 Edit 调用失败: exit 1 — 匹配已知错误模式: rm-rf

**Better alternatives:**
  1. 用trash命令替代rm -rf

**Skill fragments to create:**
  - [rm-rf] 用trash命令替代rm -rf ||from: rm -rf /

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:16:51.649Z
**Why**: 工具 Bash 调用失败: exit 1 — 匹配已知错误模式: git-push-force

**Better alternatives:**
  1. 用git push --force-with-lease

**Skill fragments to create:**
  - [git-push-force] 用git push --force-with-lease ||from: git push --force

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:32:55.279Z
**Why**: 工具 Bash 调用失败: exit 128 — 匹配已知错误模式: git-clean-fd

**Better alternatives:**
  1. 先git status确认

**Skill fragments to create:**
  - [git-clean-fd] 先git status确认 ||from: git clean -f -d

---
## PostTool Reflect [error]

**Tool**: Bash
**Time**: 2026-04-10T13:38:35.480Z
**Why**: 工具 Bash 调用失败: exit 128 — 匹配已知错误模式: git-clean-fd

**Better alternatives:**
  1. 先git status确认

**Skill fragments to create:**
  - [git-clean-fd] 先git status确认 ||from: git clean -f -d

---
