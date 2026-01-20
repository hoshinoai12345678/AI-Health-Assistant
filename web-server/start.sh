#!/bin/bash

# AI大健康助手 - CentOS一键部署启动脚本
# 适用于CentOS 7/8系统
# 自动安装所有依赖组件并启动服务

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  AI大健康助手 Web服务器版一键部署脚本"
echo "  适用于CentOS 7/8系统"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_warn "建议使用root权限运行此脚本以安装系统组件"
        log_info "如需安装系统组件，请使用: sudo ./start.sh"
    fi
}

# 检查是否在web-server目录
if [ ! -f "main.py" ]; then
    log_error "请在web-server目录下运行此脚本"
    exit 1
fi

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "项目根目录: $PROJECT_ROOT"
log_info "Web服务器目录: $SCRIPT_DIR"
echo ""

# ==================== 1. 安装系统依赖 ====================
log_info "步骤 1/8: 检查并安装系统依赖..."

install_system_deps() {
    if command -v yum &> /dev/null; then
        log_info "检测到YUM包管理器 (CentOS/RHEL)"
        
        # 更新系统
        log_info "更新系统包列表..."
        sudo yum update -y || log_warn "系统更新失败，继续执行..."
        
        # 安装基础工具
        log_info "安装基础开发工具..."
        sudo yum groupinstall -y "Development Tools" || true
        sudo yum install -y wget curl git vim net-tools || true
        
    else
        log_warn "未检测到YUM包管理器，跳过系统依赖安装"
    fi
}

# 如果是root用户或使用sudo，则安装系统依赖
if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    install_system_deps
else
    log_warn "无sudo权限，跳过系统依赖安装"
fi

echo ""

# ==================== 2. 安装Python 3.8+ ====================
log_info "步骤 2/8: 检查并安装Python 3.8+..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "已安装Python: $PYTHON_VERSION"
else
    log_info "未找到Python3，开始安装..."
    if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
        sudo yum install -y python3 python3-pip python3-devel
        log_info "Python3安装完成"
    else
        log_error "需要sudo权限安装Python3"
        exit 1
    fi
fi

# 确保pip可用
if ! command -v pip3 &> /dev/null; then
    log_info "安装pip3..."
    sudo yum install -y python3-pip
fi

echo ""

# ==================== 3. 安装PostgreSQL ====================
log_info "步骤 3/8: 检查并安装PostgreSQL..."

install_postgresql() {
    if command -v psql &> /dev/null; then
        PG_VERSION=$(psql --version | awk '{print $3}')
        log_info "已安装PostgreSQL: $PG_VERSION"
    else
        log_info "未找到PostgreSQL，开始安装..."
        
        # 安装PostgreSQL 12
        sudo yum install -y postgresql-server postgresql-contrib
        
        # 初始化数据库
        if [ ! -d "/var/lib/pgsql/data/base" ]; then
            log_info "初始化PostgreSQL数据库..."
            sudo postgresql-setup initdb
        fi
        
        # 启动并设置开机自启
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        
        log_info "PostgreSQL安装完成"
    fi
    
    # 确保PostgreSQL正在运行
    if ! sudo systemctl is-active --quiet postgresql; then
        log_info "启动PostgreSQL服务..."
        sudo systemctl start postgresql
    fi
    
    # 创建数据库和用户
    log_info "配置数据库..."
    sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'health_db'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE health_db;" || log_warn "数据库可能已存在"
    
    sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'postgres'" | grep -q 1 && \
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '123456';" || log_warn "用户配置可能失败"
    
    log_info "数据库配置完成 (用户: postgres, 密码: 123456)"
}

if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    install_postgresql
else
    log_warn "无sudo权限，跳过PostgreSQL安装"
fi

echo ""

# ==================== 4. 安装Redis ====================
log_info "步骤 4/8: 检查并安装Redis..."

install_redis() {
    if command -v redis-server &> /dev/null; then
        REDIS_VERSION=$(redis-server --version | awk '{print $3}')
        log_info "已安装Redis: $REDIS_VERSION"
    else
        log_info "未找到Redis，开始安装..."
        
        # 安装EPEL仓库
        sudo yum install -y epel-release
        
        # 安装Redis
        sudo yum install -y redis
        
        # 配置Redis
        sudo sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/' /etc/redis.conf || true
        sudo sed -i 's/^# requirepass foobared/requirepass 123456/' /etc/redis.conf || true
        
        # 启动并设置开机自启
        sudo systemctl start redis
        sudo systemctl enable redis
        
        log_info "Redis安装完成 (密码: 123456)"
    fi
    
    # 确保Redis正在运行
    if ! sudo systemctl is-active --quiet redis; then
        log_info "启动Redis服务..."
        sudo systemctl start redis
    fi
}

if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    install_redis
else
    log_warn "无sudo权限，跳过Redis安装"
fi

echo ""

# ==================== 5. 配置防火墙 ====================
log_info "步骤 5/8: 配置防火墙..."

configure_firewall() {
    if command -v firewall-cmd &> /dev/null; then
        if sudo systemctl is-active --quiet firewalld; then
            log_info "开放端口9000..."
            sudo firewall-cmd --permanent --add-port=9000/tcp || true
            sudo firewall-cmd --reload || true
            log_info "防火墙配置完成"
        else
            log_warn "firewalld未运行，跳过防火墙配置"
        fi
    else
        log_warn "未找到firewalld，跳过防火墙配置"
    fi
}

if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    configure_firewall
else
    log_warn "无sudo权限，跳过防火墙配置"
fi

echo ""

# ==================== 6. 配置Python虚拟环境 ====================
log_info "步骤 6/8: 配置Python虚拟环境..."

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    log_info "创建Python虚拟环境..."
    python3 -m venv venv
    log_info "虚拟环境创建完成"
else
    log_info "虚拟环境已存在"
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source venv/bin/activate

# 升级pip
log_info "升级pip..."
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
log_info "安装Python依赖包..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

log_info "Python依赖安装完成"
echo ""

# ==================== 7. 配置环境变量 ====================
log_info "步骤 7/8: 配置环境变量..."

if [ ! -f ".env" ]; then
    log_info "创建.env配置文件..."
    cp env.example .env
    
    # 自动配置数据库密码
    sed -i 's/postgres:postgres@/postgres:123456@/' .env
    
    # 自动配置Redis（如果设置了密码）
    # sed -i 's|redis://localhost:6379/0|redis://:123456@localhost:6379/0|' .env
    
    log_info ".env文件创建完成"
    log_warn "已使用默认配置，数据库密码: 123456"
else
    log_info ".env文件已存在，跳过创建"
fi

echo ""

# ==================== 8. 初始化数据库 ====================
log_info "步骤 8/8: 初始化数据库..."

if [ -f "$PROJECT_ROOT/backend/scripts/init_db.py" ]; then
    log_info "运行数据库初始化脚本..."
    cd "$PROJECT_ROOT/backend"
    
    # 临时设置环境变量
    export DATABASE_URL="postgresql+asyncpg://postgres:123456@localhost:5432/health_db"
    
    python3 scripts/init_db.py || log_warn "数据库初始化可能失败，如果是首次运行请检查"
    
    cd "$SCRIPT_DIR"
    log_info "数据库初始化完成"
else
    log_warn "未找到数据库初始化脚本，跳过"
fi

echo ""

# ==================== 显示系统信息 ====================
echo "=========================================="
echo "  系统组件状态"
echo "=========================================="

# Python版本
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python: 未安装"
fi

# PostgreSQL状态
if command -v psql &> /dev/null; then
    if sudo systemctl is-active --quiet postgresql 2>/dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL: 运行中"
    else
        echo -e "${YELLOW}!${NC} PostgreSQL: 已安装但未运行"
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL: 未安装"
fi

# Redis状态
if command -v redis-server &> /dev/null; then
    if sudo systemctl is-active --quiet redis 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Redis: 运行中"
    else
        echo -e "${YELLOW}!${NC} Redis: 已安装但未运行"
    fi
else
    echo -e "${RED}✗${NC} Redis: 未安装"
fi

echo ""
echo "=========================================="
echo "  配置信息"
echo "=========================================="
echo "数据库: postgresql://postgres:123456@localhost:5432/health_db"
echo "Redis: redis://localhost:6379/0"
echo "API Key: sk-a67e8c874a694d48a81b72dcdebeb045"
echo "Web端口: 9000"
echo ""

# ==================== 启动Web服务器 ====================
echo "=========================================="
echo "  启动Web服务器"
echo "=========================================="
echo ""
log_info "服务器地址: http://localhost:9000"

# 获取公网IP（优先）和内网IP
PUBLIC_IP=$(curl -s --connect-timeout 3 ifconfig.me || curl -s --connect-timeout 3 icanhazip.com || echo "")
PRIVATE_IP=$(hostname -I | awk '{print $1}')

if [ -n "$PUBLIC_IP" ]; then
    log_info "公网地址: http://$PUBLIC_IP:9000"
fi

if [ -n "$PRIVATE_IP" ]; then
    log_info "内网地址: http://$PRIVATE_IP:9000"
fi

echo ""
log_warn "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
cd "$SCRIPT_DIR"
python main.py
