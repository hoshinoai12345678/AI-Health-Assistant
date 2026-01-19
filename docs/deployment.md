# 🚀 AI大健康助手 - 部署指南

## 📋 文档信息
- **项目名称**：AI大健康助手
- **版本**：v1.0
- **创建日期**：2026-01-19

---

## 🎯 部署方式

本项目支持三种部署方式：
1. **本地开发部署**（推荐用于开发）
2. **Docker部署**（推荐用于生产）
3. **云服务器部署**（推荐用于正式上线）

---

## 📦 方式一：本地开发部署

### 前置要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 微信开发者工具

### 步骤1：安装数据库

#### PostgreSQL安装

**Windows:**
```bash
# 下载安装包
https://www.postgresql.org/download/windows/

# 安装后创建数据库
psql -U postgres
CREATE DATABASE health_db;
\q
```

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb health_db
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql-15
sudo systemctl start postgresql
sudo -u postgres createdb health_db
```

#### Redis安装

**Windows:**
```bash
# 下载Redis for Windows
https://github.com/tporadowski/redis/releases

# 解压后运行
redis-server.exe
```

**Mac:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

### 步骤2：配置后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Windows CMD
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env

# 6. 编辑.env文件，填入实际配置
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/health_db
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your-secret-key-here
# WECHAT_APP_ID=your-wechat-app-id
# WECHAT_APP_SECRET=your-wechat-app-secret
# DASHSCOPE_API_KEY=your-dashscope-api-key

# 7. 初始化数据库
python scripts/init_db.py

# 8. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤3：配置小程序

```bash
# 1. 使用微信开发者工具打开miniprogram目录

# 2. 配置AppID
# 在project.config.json中修改appid字段

# 3. 配置API地址
# 在utils/request.ts中修改BASE_URL
# const BASE_URL = 'http://localhost:8000/api'

# 4. 点击编译运行
```

### 验证部署

1. **后端验证**
   - 访问 http://localhost:8000
   - 访问 http://localhost:8000/docs
   - 访问 http://localhost:8000/health

2. **小程序验证**
   - 首页正常显示
   - 可以跳转到各个页面
   - 可以进行登录操作

---

## 🐳 方式二：Docker部署

### 前置要求

- Docker 20+
- Docker Compose 2+

### 步骤1：准备配置

```bash
# 1. 进入docker目录
cd docker

# 2. 创建环境变量文件
cat > .env << EOF
SECRET_KEY=your-secret-key-change-in-production
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
DASHSCOPE_API_KEY=your-dashscope-api-key
EOF
```

### 步骤2：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
```

### 步骤3：初始化数据库

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行初始化脚本
python scripts/init_db.py

# 退出容器
exit
```

### 服务访问

- **后端API**: http://localhost:80
- **API文档**: http://localhost:80/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MinIO**: http://localhost:9000 (控制台: http://localhost:9001)

### 常用命令

```bash
# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v

# 查看资源使用
docker-compose stats

# 更新镜像
docker-compose pull
docker-compose up -d
```

---

## ☁️ 方式三：云服务器部署

### 推荐配置

**开发环境**：
- CPU: 2核
- 内存: 4GB
- 硬盘: 40GB
- 带宽: 3Mbps
- 费用: 约¥100/月

**生产环境**：
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB
- 带宽: 5Mbps
- 费用: 约¥300/月

### 步骤1：购买服务器

推荐云服务商：
- 阿里云ECS
- 腾讯云CVM
- 华为云ECS

操作系统：Ubuntu 22.04 LTS

### 步骤2：配置服务器

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 更新系统
apt update && apt upgrade -y

# 3. 安装Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 4. 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 5. 安装Git
apt install git -y

# 6. 克隆项目
git clone https://your-repo-url.git
cd ai-health-assistant
```

### 步骤3：配置SSL证书

```bash
# 1. 安装certbot
apt install certbot -y

# 2. 申请证书
certbot certonly --standalone -d your-domain.com

# 3. 证书路径
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem

# 4. 配置Nginx使用证书
# 编辑 docker/nginx/nginx.conf
```

### 步骤4：配置域名

```bash
# 1. 在域名服务商添加A记录
# 主机记录: @
# 记录类型: A
# 记录值: your-server-ip

# 2. 添加www记录
# 主机记录: www
# 记录类型: CNAME
# 记录值: your-domain.com
```

### 步骤5：部署应用

```bash
# 1. 配置环境变量
cd docker
cp .env.example .env
vim .env

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 初始化数据库
docker-compose exec backend python scripts/init_db.py
```

### 步骤6：配置防火墙

```bash
# 开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

## 🔒 安全配置

### 1. 修改默认密码

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres
ALTER USER postgres WITH PASSWORD 'new-strong-password';

# Redis
# 编辑docker-compose.yml，添加密码配置
redis:
  command: redis-server --requirepass your-redis-password
```

### 2. 配置JWT密钥

```bash
# 生成强密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 更新.env文件
SECRET_KEY=generated-strong-key
```

### 3. 限制访问

```bash
# 配置Nginx限流
# 编辑docker/nginx/nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    proxy_pass http://backend/api/;
}
```

---

## 📊 监控和日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 日志文件位置

```
backend/logs/app.log
docker/nginx/logs/access.log
docker/nginx/logs/error.log
```

### 监控指标

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看数据库连接数
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🔄 更新部署

### 更新代码

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d

# 4. 查看日志确认
docker-compose logs -f backend
```

### 数据库迁移

```bash
# 1. 备份数据库
docker-compose exec postgres pg_dump -U postgres health_db > backup.sql

# 2. 运行迁移
docker-compose exec backend alembic upgrade head

# 3. 验证迁移
docker-compose exec backend alembic current
```

---

## 🔧 故障排查

### 后端无法启动

```bash
# 1. 查看日志
docker-compose logs backend

# 2. 检查数据库连接
docker-compose exec backend python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"

# 3. 检查Redis连接
docker-compose exec backend python -c "from app.core.redis import redis_client; import asyncio; asyncio.run(redis_client.connect())"
```

### 数据库连接失败

```bash
# 1. 检查PostgreSQL状态
docker-compose ps postgres

# 2. 检查数据库日志
docker-compose logs postgres

# 3. 手动连接测试
docker-compose exec postgres psql -U postgres -d health_db
```

### 小程序无法连接后端

```bash
# 1. 检查API地址配置
# miniprogram/utils/request.ts中的BASE_URL

# 2. 检查服务器防火墙
ufw status

# 3. 检查Nginx配置
docker-compose exec nginx nginx -t
```

---

## 📝 备份和恢复

### 数据库备份

```bash
# 手动备份
docker-compose exec postgres pg_dump -U postgres health_db > backup_$(date +%Y%m%d).sql

# 定时备份（添加到crontab）
0 2 * * * cd /path/to/project && docker-compose exec postgres pg_dump -U postgres health_db > backup_$(date +\%Y\%m\%d).sql
```

### 数据库恢复

```bash
# 恢复数据库
docker-compose exec -T postgres psql -U postgres health_db < backup.sql
```

### 文件备份

```bash
# 备份上传文件
tar -czf uploads_backup.tar.gz uploads/

# 备份MinIO数据
docker-compose exec minio mc mirror /data /backup
```

---

## 🎯 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- 分析表
ANALYZE users;
ANALYZE messages;
ANALYZE conversations;
```

### 2. Redis优化

```bash
# 配置最大内存
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 3. Nginx优化

```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
```

---

## 📞 技术支持

如有问题，请查阅：
- [项目文档](../README.md)
- [快速启动指南](../快速启动指南.md)
- [架构文档](../memory-bank/architecture.md)

---

**文档创建时间**：2026-01-19  
**最后更新**：2026-01-19  
**版本**：v1.0
