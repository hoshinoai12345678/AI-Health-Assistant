#!/bin/bash

# 数据库备份脚本

BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
echo "开始备份数据库..."
docker-compose -f docker-compose.prod.yml exec -T postgres \
    pg_dump -U aihealth aihealth | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

if [ $? -eq 0 ]; then
    echo "备份成功: backup_$DATE.sql.gz"
else
    echo "备份失败"
    exit 1
fi

# 删除旧备份
echo "清理旧备份..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$KEEP_DAYS -delete

echo "备份完成"
