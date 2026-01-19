#!/bin/bash

echo "========================================"
echo "AI健康助手 - 一键启动脚本"
echo "========================================"
echo ""

# 检查Docker是否运行
echo "[1/6] 检查Docker状态..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi
echo "✅ Docker运行正常"
echo ""

# 检查.env文件
echo "[2/6] 检查环境配置..."
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    cat > .env << EOF
# 数据库配置
DATABASE_URL=postgresql+asyncpg://aihealth:aihealth123@postgres:5432/aihealth

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=your-super-secret-key-change-this-in-production-12345678
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 微信小程序配置
WECHAT_APP_ID=test_app_id
WECHAT_APP_SECRET=test_app_secret

# 阿里云通义千问配置
TONGYI_API_KEY=test_api_key
TONGYI_MODEL=qwen-plus

# CORS配置
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# 数据库配置
POSTGRES_USER=aihealth
POSTGRES_PASSWORD=aihealth123
POSTGRES_DB=aihealth
EOF
    echo "✅ .env文件创建成功"
else
    echo "✅ .env文件已存在"
fi
echo ""

# 构建镜像
echo "[3/6] 构建Docker镜像（首次运行需要几分钟）..."
if ! docker-compose build; then
    echo "❌ 镜像构建失败"
    exit 1
fi
echo "✅ 镜像构建成功"
echo ""

# 启动服务
echo "[4/6] 启动服务..."
if ! docker-compose up -d; then
    echo "❌ 服务启动失败"
    exit 1
fi
echo "✅ 服务启动成功"
echo ""

# 等待服务就绪
echo "[5/6] 等待服务就绪（30秒）..."
sleep 30
echo "✅ 服务已就绪"
echo ""

# 初始化数据库
echo "[6/6] 初始化数据库..."
if ! docker-compose exec -T backend alembic upgrade head; then
    echo "⚠️  数据库迁移失败（可能已经初始化过）"
else
    echo "✅ 数据库初始化成功"
fi
echo ""

# 导入示例数据
echo "[6/6] 导入示例数据..."
if ! docker-compose exec -T backend python scripts/import_resources.py; then
    echo "⚠️  数据导入失败（可能已经导入过）"
else
    echo "✅ 示例数据导入成功"
fi
echo ""

# 健康检查
echo "执行健康检查..."
sleep 5
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
else
    echo "⚠️  健康检查失败，请稍后手动访问 http://localhost:8000/health"
fi
echo ""

echo "========================================"
echo "🎉 部署完成！"
echo "========================================"
echo ""
echo "📍 服务地址："
echo "   - API服务: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo "   - 健康检查: http://localhost:8000/health"
echo ""
echo "📝 常用命令："
echo "   - 查看日志: docker-compose logs -f"
echo "   - 查看状态: docker-compose ps"
echo "   - 停止服务: docker-compose stop"
echo "   - 重启服务: docker-compose restart"
echo ""
echo "📚 详细文档："
echo "   - 从零开始部署测试指南.md"
echo "   - docs/API文档.md"
echo ""
