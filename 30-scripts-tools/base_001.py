#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BASE-001 Base Module
Created by AUTO-ARCHITECT-001
Common utilities for all tools
"""
import logging
import json
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load {{path}}: {{e}}")
        return {{}}

def save_json(data, path):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True
