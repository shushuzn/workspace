import os
temp_files = ['temp_create_dirs.py', 'temp_copy_modules.py']
for f in temp_files:
    if os.path.exists(f):
        os.remove(f)
        print(f"Removed: {f}")