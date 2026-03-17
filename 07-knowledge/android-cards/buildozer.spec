[app]
title = 知识卡片生成器
package.name = knowledgecard
package.domain = org.knowledgecard
source.dir = .
source.include_exts = py,pdf,html,txt,json
source.exclude_exts = spec
source.exclude_dirs = tests,__pycache__

version = 1.0.0
requirements = python3,kivy==1.11.1,pymupdf,requests,numpy,opencv-python-headless
presplash_filename = assets/presplash.png
icon.filename = assets/icon.png

orientation = portrait
fullscreen = 0
android.allow_backup = True
android.app_lifetime = 3600

android.api = 31
android.minapi = 21
android.ndk = 23b
android.arch = arm64-v8a
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]
profile = default
log_level = 2
warn_on_root = 1
