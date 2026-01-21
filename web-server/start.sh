#!/bin/bash

# AI大健康助手 - Web服务器一键部署启动脚本
# 适用于CentOS 7/8系统
# 版本: 2.0.0 (2026-01-21)
# 更新: 四端分离数据管理功能

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  AI大健康助手 Web服务器版一键部署脚本"
echo "  适用于CentOS 7/8系统"
echo "  版本: 2.0.0 (2026-01-21)"
echo "=========================================="
echo ""
echo "📝 更新日志 v2.0.0:"
echo "  ✨ 新增四端分离数据管理功能"
echo "  ✨ 支持体测数据上传（Excel/CSV）"
echo "  ✨ 支持动作库上传（1260例课课练）"
echo "  ✨ 学号关联查询功能"
echo "  ✨ 智能训练推荐系统"
echo "  ✨ 班级数据统计分析"
echo "  🔧 集成数据库自动初始化"
echo "  🔧 添加数据处理依赖（pandas、openpyxl）"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

# ==================== 1. 检查后端代码更新 ====================
log_step "步骤 1/11: 检查后端代码更新..."

check_backend_files() {
    local files_to_check=(
        "$PROJECT_ROOT/backend/app/core/security.py"
        "$PROJECT_ROOT/backend/app/core/database.py"
        "$PROJECT_ROOT/backend/app/api/chat.py"
        "$PROJECT_ROOT/backend/app/api/conversation.py"
        "$PROJECT_ROOT/backend/app/api/auth.py"
        "$PROJECT_ROOT/backend/app/api/data_upload.py"
        "$PROJECT_ROOT/backend/app/models/student_data.py"
    )
    
    local all_exist=true
    local missing_files=()
    
    for file in "${files_to_check[@]}"; do
        if [ ! -f "$file" ]; then
            log_warn "缺少文件: $(basename $file)"
            missing_files+=("$file")
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        log_info "✓ 后端代码文件检查通过"
        
        # 检查关键函数是否存在
        if grep -q "get_current_user" "$PROJECT_ROOT/backend/app/core/security.py" 2>/dev/null; then
            log_info "✓ 认证函数已更新 (get_current_user)"
        else
            log_warn "⚠ 认证函数可能未更新，请检查 security.py"
        fi
        
        if grep -q "StudentFitnessData" "$PROJECT_ROOT/backend/app/models/student_data.py" 2>/dev/null; then
            log_info "✓ 数据模型已创建 (StudentFitnessData)"
        else
            log_warn "⚠ 数据模型可能未创建"
        fi
        
        if grep -q "upload/fitness-data" "$PROJECT_ROOT/backend/app/api/data_upload.py" 2>/dev/null; then
            log_info "✓ 数据上传API已创建"
        else
            log_warn "⚠ 数据上传API可能未创建"
        fi
    else
        log_error "后端代码文件不完整，缺少以下文件:"
        for file in "${missing_files[@]}"; do
            echo "  - $(basename $file)"
        done
        log_warn "将继续执行，但部分功能可能不可用"
    fi
}

check_backend_files
echo ""

# ==================== 2. 安装系统依赖 ====================
log_step "步骤 2/11: 检查并安装系统依赖..."

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

# ==================== 3. 安装Python 3.8+ ====================
log_step "步骤 3/11: 检查并安装Python 3.8+..."

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

# ==================== 4. 安装PostgreSQL ====================
log_step "步骤 4/11: 检查并安装PostgreSQL..."

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
    log_info "将使用SQLite作为数据库"
fi

echo ""

# ==================== 5. 安装Redis ====================
log_step "步骤 5/11: 检查并安装Redis..."

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

# ==================== 6. 配置防火墙 ====================
log_step "步骤 6/11: 配置防火墙..."

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

# ==================== 7. 配置Python虚拟环境 ====================
log_step "步骤 7/11: 配置Python虚拟环境..."

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

# 安装依赖（按顺序安装，确保兼容性）
log_info "安装Python依赖包..."
log_info "先安装numpy（基础依赖）..."
pip install numpy==1.24.3 -i https://pypi.tuna.tsinghua.edu.cn/simple

log_info "安装pandas和数据处理库..."
pip install pandas==2.0.3 openpyxl==3.1.2 xlrd==2.0.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

log_info "安装其他依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

log_info "Python依赖安装完成"
echo ""

# ==================== 8. 配置环境变量 ====================
log_step "步骤 8/10: 配置环境变量..."

if [ ! -f ".env" ]; then
    log_info "创建.env配置文件..."
    cp env.example .env
    
    # 自动配置数据库密码
    sed -i 's/postgres:postgres@/postgres:123456@/' .env
    
    log_info ".env文件创建完成"
    log_warn "已使用默认配置，数据库密码: 123456"
else
    log_info ".env文件已存在，跳过创建"
fi

echo ""

# ==================== 9. 初始化数据库 ====================
log_step "步骤 9/10: 初始化数据库..."

# 使用SQLite作为默认数据库（简化部署）
export DATABASE_URL="sqlite:///./ctz_data.db"

log_info "使用SQLite数据库: ctz_data.db"
log_info "数据库位置: $PROJECT_ROOT/backend/ctz_data.db"

# 进入backend目录
cd "$PROJECT_ROOT/backend"

# 删除旧的数据库文件（如果存在且为空）
if [ -f "ctz_data.db" ]; then
    TABLE_COUNT=$(sqlite3 ctz_data.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
    if [ "$TABLE_COUNT" -eq 0 ]; then
        log_warn "发现空数据库文件，删除并重新创建..."
        rm -f ctz_data.db
    fi
fi

# 强制创建数据库表
log_info "创建数据库表..."

python3 << 'DBINIT'
import sys
import os

# 添加项目路径
backend_path = os.getcwd()
sys.path.insert(0, backend_path)

print("=" * 60)
print("正在初始化数据库...")
print("=" * 60)

try:
    from sqlalchemy import create_engine, inspect
    from app.models.student_data import Base
    
    # 使用绝对路径
    db_path = os.path.join(backend_path, "ctz_data.db")
    DATABASE_URL = f"sqlite:///{db_path}"
    
    print(f"\n数据库URL: {DATABASE_URL}")
    print(f"数据库文件: {db_path}")
    print(f"工作目录: {os.getcwd()}")
    
    # 创建引擎，启用 echo 查看 SQL
    engine = create_engine(DATABASE_URL, echo=True)
    
    # 创建所有表
    print("\n开始创建表...")
    Base.metadata.create_all(bind=engine)
    
    # 验证表是否创建成功
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n" + "=" * 60)
    if len(tables) > 0:
        print("✓ 数据库表创建成功！")
        print("=" * 60)
        print(f"\n已创建 {len(tables)} 个数据表:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        print(f"\n数据库文件: {db_path}")
        print("=" * 60)
    else:
        print("✗ 警告：表创建失败，数据库中没有表！")
        print("=" * 60)
        sys.exit(1)
    
except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ 数据库初始化失败: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
DBINIT

# 检查数据库初始化结果
if [ $? -eq 0 ]; then
    log_info "✓ 数据库初始化成功"
else
    log_error "✗ 数据库初始化失败"
    exit 1
fi

# 检查数据库文件是否创建
if [ -f "$PROJECT_ROOT/backend/ctz_data.db" ]; then
    DB_SIZE=$(du -h "$PROJECT_ROOT/backend/ctz_data.db" | cut -f1)
    log_info "✓ 数据库文件: $PROJECT_ROOT/backend/ctz_data.db ($DB_SIZE)"
    
    # 使用 Python 验证表（更可靠）
    log_info "验证数据库表..."
    python3 << 'VERIFY'
import sys
import os
import sqlite3

db_path = "/root/ctz_project/backend/ctz_data.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    if len(tables) > 0:
        print(f"✓ 数据库包含 {len(tables)} 个表:")
        for table in tables:
            print(f"    - {table[0]}")
        sys.exit(0)
    else:
        print("✗ 数据库中没有表！")
        sys.exit(1)
except Exception as e:
    print(f"✗ 验证失败: {e}")
    sys.exit(1)
VERIFY
    
    if [ $? -eq 0 ]; then
        log_info "✓ 数据库表验证通过"
    else
        log_error "✗ 数据库表验证失败"
        exit 1
    fi
else
    log_error "✗ 数据库文件未创建！"
    exit 1
fi

# 返回web-server目录
cd "$SCRIPT_DIR"

echo ""

# ==================== 10. 检查前端文件 ====================
log_step "步骤 10/10: 检查前端文件..."

log_info "检查前端数据管理文件..."

# 检查新增的前端文件
FRONTEND_FILES=(
    "$SCRIPT_DIR/static/js/data-manager.js"
    "$SCRIPT_DIR/static/css/data-styles.css"
    "$SCRIPT_DIR/templates/data-pages.html"
)

missing_frontend=false
for file in "${FRONTEND_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_warn "缺少前端文件: $(basename $file)"
        missing_frontend=true
    else
        log_info "✓ $(basename $file) 已存在"
    fi
done

# 检查index.html是否需要更新
if [ -f "$SCRIPT_DIR/templates/index.html" ]; then
    if grep -q "data-manager.js" "$SCRIPT_DIR/templates/index.html" 2>/dev/null; then
        log_info "✓ index.html 已包含数据管理模块"
    else
        log_warn "⚠ index.html 可能需要添加以下引用:"
        echo "  <link rel=\"stylesheet\" href=\"/static/css/data-styles.css\">"
        echo "  <script src=\"/static/js/data-manager.js\"></script>"
        log_info "建议手动添加或将data-pages.html内容合并到index.html"
    fi
else
    log_warn "未找到index.html"
fi

if [ "$missing_frontend" = true ]; then
    log_warn "部分前端文件缺失，数据管理功能可能不完整"
    log_info "请确保已上传以下文件:"
    echo "  - static/js/data-manager.js"
    echo "  - static/css/data-styles.css"
    echo "  - templates/data-pages.html"
else
    log_info "✓ 前端文件检查完成"
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
    echo -e "${YELLOW}!${NC} PostgreSQL: 未安装 (使用SQLite)"
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

# 后端代码状态
if grep -q "get_current_user" "$PROJECT_ROOT/backend/app/core/security.py" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 后端代码: 已更新 (v2.0.0)"
else
    echo -e "${YELLOW}!${NC} 后端代码: 可能需要更新"
fi

# 数据管理功能状态
if [ -f "$PROJECT_ROOT/backend/app/api/data_upload.py" ]; then
    echo -e "${GREEN}✓${NC} 数据管理: 已安装"
else
    echo -e "${YELLOW}!${NC} 数据管理: 未安装"
fi

# 数据库状态
if [ -f "$PROJECT_ROOT/backend/ctz_data.db" ]; then
    DB_SIZE=$(du -h "$PROJECT_ROOT/backend/ctz_data.db" | cut -f1)
    echo -e "${GREEN}✓${NC} 数据库: ctz_data.db ($DB_SIZE)"
else
    echo -e "${YELLOW}!${NC} 数据库: 将在首次运行时创建"
fi

echo ""
echo "=========================================="
echo "  配置信息"
echo "=========================================="
echo "数据库: SQLite (ctz_data.db)"
echo "Redis: redis://localhost:6379/0"
echo "Web端口: 9000"
echo ""
echo "📊 数据管理功能:"
echo "  - 体测数据上传: POST /api/data/upload/fitness-data"
echo "  - 动作库上传: POST /api/data/upload/sports-exercises"
echo "  - 学生查询: GET /api/data/student/{student_id}"
echo "  - 班级查询: GET /api/data/class/{class_name}"
echo "  - 训练推荐: GET /api/data/exercises/recommend"
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
echo "📝 API 端点:"
echo "  基础功能:"
echo "    - 健康检查: GET /health"
echo "    - 登录: POST /api/auth/login"
echo "    - 发送消息: POST /api/chat/send"
echo "    - 对话列表: GET /api/conversation/list"
echo ""
echo "  数据管理 (v2.0新增):"
echo "    - 上传体测数据: POST /api/data/upload/fitness-data"
echo "    - 上传动作库: POST /api/data/upload/sports-exercises"
echo "    - 查询学生: GET /api/data/student/{student_id}"
echo "    - 查询班级: GET /api/data/class/{class_name}"
echo "    - 训练推荐: GET /api/data/exercises/recommend?student_id=xxx"
echo ""
echo "💡 快速测试:"
echo "  1. 教师端: 选择'教师'角色 → 点击'数据'→ 上传CSV/Excel"
echo "  2. 学生端: 选择'学生'角色 → 点击'数据'→ 输入学号查询"
echo "  3. 示例学号: 092800001, 092800002, 092805147..."
echo ""
log_warn "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
cd "$SCRIPT_DIR"
python main.py
