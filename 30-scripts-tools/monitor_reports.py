import os, sys, hashlib, json  
from datetime import datetime  
from pathlib import Path  
  
WORKSPACE = Path('D:/OpenClaw/workspace')  
MONITOR_STATE = WORKSPACE / '20-data-reports' / 'report-monitor-state.json'  
STANDARD_DIRS = ['21-reports', '30-scripts-tools', '06-research', '13-memory', '15-docs']  
  
print('Report Monitor - Scanning...')  
reports = [f for root,_,files in os.walk(WORKSPACE) if 'backup' not in root for f in files if f.endswith('.md') and 'report' in f.lower()]  
print(f'Found {len(reports)} reports')  
print('OK')  
