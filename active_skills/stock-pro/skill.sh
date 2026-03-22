#!/bin/bash
# Stock PRO Skill for CoPaw
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/../30-scripts-tools/stock_pro_v4.py" "$@"
