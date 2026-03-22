from pathlib import Path

temp_files = [
    'debug_args.py', 'test_nargs.py', 'test_fetch.py',
    'analyze_duplicates.py', 'scan_review_files.py', 'deep_scan_reg.py',
    'compare_reg_funcs.py', 'find_orphans.py', 'find_version_dups.py',
    'detailed_review.py', 'check_remaining.py', 'review_list.py',
    'phase2_delete.py', 'phase3_delete.py', 'phase4_delete.py',
    'cleanup_tools.py', 'tool_naming_convention.py',
    'stock_pro/check_modules.py',
]

for f in temp_files:
    p = Path(f)
    if p.exists():
        print(f'[DEL] {f}')
        p.unlink()
    else:
        print(f'[SKIP] {f}')

print(f'\nCleaned {sum(1 for f in temp_files if Path(f).exists() == False)} files')
