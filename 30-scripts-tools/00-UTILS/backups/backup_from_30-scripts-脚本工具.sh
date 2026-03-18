#!/bin/bash
# 备份脚本

set -e

echo "========================================"
echo "备份 AI Research OS 数据"
echo "========================================"

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "备份目录：$BACKUP_DIR"

# 备份日志
echo "备份日志..."
if [ -d "logs" ]; then
    cp -r logs $BACKUP_DIR/
    echo "✓ 日志备份完成"
fi

# 备份配置
echo "备份配置..."
if [ -f "config.yaml" ]; then
    cp config.yaml $BACKUP_DIR/
    echo "✓ 配置备份完成"
fi

# 备份数据库
echo "备份数据库..."
# TODO: 实现数据库备份

# 压缩备份
echo "压缩备份..."
cd $BACKUP_DIR/..
tar -czf $(basename $BACKUP_DIR).tar.gz $(basename $BACKUP_DIR)
rm -rf $(basename $BACKUP_DIR)

echo ""
echo "========================================"
echo "备份完成！"
echo "备份文件：backups/$(basename $BACKUP_DIR).tar.gz"
echo "========================================"
