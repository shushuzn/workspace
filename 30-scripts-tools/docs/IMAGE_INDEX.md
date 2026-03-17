# 图片文件索引

**创建:** 2026-03-07 02:16

## 索引文件

| 类型 | CSV 文件 | 数量 |
|------|---------|------|
| PNG | `IMAGE_INDEX_PNG_2026-03-07.csv` | ~50 |
| JPG | `IMAGE_INDEX_JPG_2026-03-07.csv` | ~10 |
| SVG | `IMAGE_INDEX_SVG_2026-03-07.csv` | ~5 |

## 按位置查找

```
11-research/figures/          # 研究图表
11-research/cnt-research/figures/  # CNT 图表
41-medium/Archive/            # Medium 截图
```

## 常用命令

```powershell
# 查找 PNG
Get-ChildItem -Recurse -Filter "*.png"

# 查找 JPG
Get-ChildItem -Recurse -Filter "*.jpg"

# 按大小查找 (>1MB)
Get-ChildItem -Recurse -Filter "*.png" | Where-Object Length -gt 1MB
```

## 标签系统 (v3 - 图形化界面)

**文件:** `IMAGE_TAGS.csv` `tag-tree.html`

**用法:**
```powershell
# 图形化查看标签树
.\view-tags.ps1

# 命令行管理
.\IMAGE_TAGGER.ps1 -Add "文件" -Tags "子标签" -Parent "父标签" -Desc "描述"
.\IMAGE_TAGGER.ps1 -List
.\IMAGE_TAGGER.ps1 -Tree
.\IMAGE_TAGGER.ps1 -Search "GP"
.\IMAGE_TAGGER.ps1 -Import "tags.csv"
```

**功能:**
- 📁 点击父标签展开/收起
- 🏷️  点击子标签查看图片
- 🔍 搜索标签或描述
- 📊 统计信息展示

## 不足

1. 无缩略图预览
2. 标签需手动添加
3. 未包含其他格式 (gif/webp)
