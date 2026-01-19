@echo off
chcp 65001 >nul
echo ========================================
echo AI健康助手 - 一键启动脚本
echo ========================================
echo.

REM 检查Docker是否运行
echo [1/6] 检查Docker状态...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker运行正常
echo.

REM 检查.env文件
echo [2/6] 检查环境配置...
if not exist .env (
    echo ⚠️  未找到.env文件，正在创建...
    (
        echo # 数据库配置
        echo DATABASE_URL=postgresql+asyncpg://aihealth:aihealth123@postgres:5432/aihealth
        echo.
        echo # Redis配置
        echo REDIS_URL=redis://redis:6379/0
        echo.
        echo # JWT配置
        echo SECRET_KEY=your-super-secret-key-change-this-in-production-12345678
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=10080
        echo.
        echo # 微信小程序配置
        echo WECHAT_APP_ID=test_app_id
        echo WECHAT_APP_SECRET=test_app_secret
        echo.
        echo # 阿里云通义千问配置
        echo TONGYI_API_KEY=test_api_key
        echo TONGYI_MODEL=qwen-plus
        echo.
        echo # CORS配置
        echo ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
        echo.
        echo # 数据库配置
        echo POSTGRES_USER=aihealth
        echo POSTGRES_PASSWORD=aihealth123
        echo POSTGRES_DB=aihealth
    ) > .env
    echo ✅ .env文件创建成功
) else (
    echo ✅ .env文件已存在
)
echo.

REM 构建镜像
echo [3/6] 构建Docker镜像（首次运行需要几分钟）...
docker-compose build
if errorlevel 1 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)
echo ✅ 镜像构建成功
echo.

REM 启动服务
echo [4/6] 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)
echo ✅ 服务启动成功
echo.

REM 等待服务就绪
echo [5/6] 等待服务就绪（30秒）...
timeout /t 30 /nobreak >nul
echo ✅ 服务已就绪
echo.

REM 初始化数据库
echo [6/6] 初始化数据库...
docker-compose exec -T backend alembic upgrade head
if errorlevel 1 (
    echo ⚠️  数据库迁移失败（可能已经初始化过）
) else (
    echo ✅ 数据库初始化成功
)
echo.

REM 导入示例数据
echo [6/6] 导入示例数据...
docker-compose exec -T backend python scripts/import_resources.py
if errorlevel 1 (
    echo ⚠️  数据导入失败（可能已经导入过）
) else (
    echo ✅ 示例数据导入成功
)
echo.

REM 健康检查
echo 执行健康检查...
timeout /t 5 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  健康检查失败，请稍后手动访问 http://localhost:8000/health
) else (
    echo ✅ 健康检查通过
)
echo.

echo ========================================
echo 🎉 部署完成！
echo ========================================
echo.
echo 📍 服务地址：
echo    - API服务: http://localhost:8000
echo    - API文档: http://localhost:8000/docs
echo    - 健康检查: http://localhost:8000/health
echo.
echo 📝 常用命令：
echo    - 查看日志: docker-compose logs -f
echo    - 查看状态: docker-compose ps
echo    - 停止服务: docker-compose stop
echo    - 重启服务: docker-compose restart
echo.
echo 📚 详细文档：
echo    - 从零开始部署测试指南.md
echo    - docs/API文档.md
echo.
echo 按任意键打开API文档...
pause >nul
start http://localhost:8000/docs
