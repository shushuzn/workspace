#!/usr/bin/env python
import subprocess
msg = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True).stdout
print(f"feat: Updated {len(msg.split(chr(10)))-2} files")
