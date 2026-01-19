#!/bin/bash

# Web服务器启动脚本

echo "======================================"
echo "  AI大健康助手 Web服务器版启动脚本"
echo "======================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查是否在web-server目录
if [ ! -f "main.py" ]; then
    echo "错误: 请在web-server目录下运行此脚本"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，使用示例配置..."
    cp env.example .env
    echo "请编辑.env文件配置数据库和AI服务"
fi

echo ""
echo "======================================"
echo "  启动Web服务器 (端口: 9000)"
echo "======================================"
echo ""
echo "访问地址: http://localhost:9000"
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python main.py
