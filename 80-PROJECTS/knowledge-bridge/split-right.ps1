# Open Knowledge Graph in right panel of Windows Terminal
# Usage: Run this script from PowerShell

$kbPath = "D:\OpenClaw\workspace\80-PROJECTS\knowledge-bridge"

# Command to run in the new panel
$cmd = "node $kbPath\terminalView.js"

# Split vertically and run knowledge graph in the new pane
wt --window 0 split-pane -V -- node "$kbPath\terminalView.js"
