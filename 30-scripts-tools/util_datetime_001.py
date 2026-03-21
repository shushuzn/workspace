import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UTIL-003 DateTime Utility
【日期时间工具】

功能:
  - 日期格式转换
  - 时区处理
  - 时间计算
"""
import json
import sys
from datetime import datetime, timedelta


class DateTimeUtil:
    """日期时间工具"""
    
    @staticmethod
    def now(format: str = "iso") -> str:
        """获取当前时间"""
        now = datetime.now()
        
        formats = {
            "iso": lambda: now.isoformat(),
            "date": lambda: now.strftime("%Y-%m-%d"),
            "time": lambda: now.strftime("%H:%M:%S"),
            "full": lambda: now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return formats.get(format, formats["iso"])()
    
    @staticmethod
    def parse(date_str: str, format: str = "%Y-%m-%d") -> str:
        """解析日期"""
        try:
            dt = datetime.strptime(date_str, format)
            return dt.isoformat()
        except (Exception,):
            return "Invalid date"
    
    @staticmethod
    def add_days(date_str: str, days: int) -> str:
        """加减天数"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            result = dt + timedelta(days=days)
            return result.strftime("%Y-%m-%d")
        except (Exception,):
            return "Invalid date"
    
    @staticmethod
    def diff_days(date1: str, date2: str) -> int:
        """计算日期差"""
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            return abs((d2 - d1).days)
        except (Exception,):
            return -1


logging.basicConfig(level=logging.INFO)
def main():
    util = DateTimeUtil()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--now":
            fmt = sys.argv[2] if len(sys.argv) > 2 else "iso"
            print(util.now(fmt))
            return 0
        
        if cmd == "--parse":
            date_str = sys.argv[2] if len(sys.argv) > 2 else "2024-01-01"
            print(util.parse(date_str))
            return 0
        
        if cmd == "--add":
            date_str = sys.argv[2] if len(sys.argv) > 2 else "2024-01-01"
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            print(util.add_days(date_str, days))
            return 0
        
        if cmd == "--diff":
            d1 = sys.argv[2] if len(sys.argv) > 2 else "2024-01-01"
            d2 = sys.argv[3] if len(sys.argv) > 3 else "2024-01-31"
            print(util.diff_days(d1, d2))
            return 0
    
    print("UTIL-003 DateTime Utility")
    print("Usage:")
    print("  py util_003.py --now [format]       # Current time")
    print("  py util_003.py --parse <date>       # Parse date")
    print("  py util_003.py --add <date> <days>  # Add days")
    print("  py util_003.py --diff <d1> <d2>     # Days between")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())