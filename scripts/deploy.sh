#!/bin/bash

# 部署脚本

set -e

echo "========================================="
echo "开始部署 AI健康助手"
echo "========================================="

# 1. 拉取最新代码
echo "1. 拉取最新代码..."
git pull origin main

# 2. 构建镜像
echo "2. 构建Docker镜像..."
docker-compose -f docker-compose.prod.yml build

# 3. 停止旧服务
echo "3. 停止旧服务..."
docker-compose -f docker-compose.prod.yml down

# 4. 启动新服务
echo "4. 启动新服务..."
docker-compose -f docker-compose.prod.yml up -d

# 5. 等待服务启动
echo "5. 等待服务启动..."
sleep 10

# 6. 运行数据库迁移
echo "6. 运行数据库迁移..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# 7. 健康检查
echo "7. 执行健康检查..."
HEALTH_CHECK=$(curl -s http://localhost:8000/health | grep -o "healthy")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo "✅ 部署成功！"
else
    echo "❌ 部署失败，服务未正常启动"
    exit 1
fi

# 8. 清理旧镜像
echo "8. 清理旧镜像..."
docker image prune -f

echo "========================================="
echo "部署完成"
echo "========================================="
