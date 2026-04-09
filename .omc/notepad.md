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
