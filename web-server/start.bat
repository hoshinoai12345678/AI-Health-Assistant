@echo off
chcp 65001 >nul
echo ======================================
echo   AI大健康助手 Web服务器版启动脚本
echo ======================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否在web-server目录
if not exist "main.py" (
    echo 错误: 请在web-server目录下运行此脚本
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 检查环境变量文件
if not exist ".env" (
    echo 警告: 未找到.env文件，使用示例配置...
    copy env.example .env
    echo 请编辑.env文件配置数据库和AI服务
)

echo.
echo ======================================
echo   启动Web服务器 (端口: 9000)
echo ======================================
echo.
echo 访问地址: http://localhost:9000
echo 按 Ctrl+C 停止服务器
echo.

REM 启动服务器
python main.py

pause
