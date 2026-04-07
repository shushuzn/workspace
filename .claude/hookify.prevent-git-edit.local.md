---
name: prevent-git-edit
enabled: true
event: file
pattern: (^\.git\/|\\\.git\\)
---

阻止对 .git 目录的编辑操作。该目录包含重要的版本控制元数据，修改可能导致 git 仓库状态破坏或历史丢失。
