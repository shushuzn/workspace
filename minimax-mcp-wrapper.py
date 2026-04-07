#!/usr/bin/env python3
"""MiniMax MCP wrapper that ensures environment variables are set."""
import os
import sys

# Ensure required environment variables
if "MINIMAX_API_KEY" not in os.environ:
    os.environ["MINIMAX_API_KEY"] = "sk-cp-zNNt30MolJOgSwdsdgA8BJbLoKmiV3Zttz_IgZkapeyjoPPq-qYFSw-XiMZIIUyeH4PTB4Y86QXu_wKR8JvmZ9PbkkMmMwDTC6QgHznXopDTl0nBZ9AQHQ8"
if "MINIMAX_API_HOST" not in os.environ:
    os.environ["MINIMAX_API_HOST"] = "https://api.minimaxi.com"

# Import and run the actual server
from minimax_mcp.server import main

if __name__ == "__main__":
    sys.exit(main())
