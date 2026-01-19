# AI大健康助手 - Web服务器版

## 项目简介

这是AI大健康助手的Web服务器版本，提供与微信小程序相同的功能和界面体验。用户可以通过浏览器访问，无需安装小程序。

## 主要特性

- ✅ **完整功能**: AI健康咨询、对话历史、个人中心
- ✅ **界面一致**: 与微信小程序保持相同的UI/UX设计
- ✅ **响应式设计**: 支持PC端和移动端访问
- ✅ **独立部署**: 部署在9000端口，不影响小程序
- ✅ **API复用**: 复用后端API服务，保持数据一致性

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **后端**: FastAPI + Python 3.8+
- **数据库**: PostgreSQL
- **缓存**: Redis
- **AI服务**: OpenAI / 通义千问

## 快速开始

### Windows系统

```bash
# 1. 进入web-server目录
cd web-server

# 2. 运行启动脚本
start.bat

# 3. 访问应用
# 打开浏览器访问: http://localhost:9000
```

### Linux/macOS系统

```bash
# 1. 进入web-server目录
cd web-server

# 2. 添加执行权限
chmod +x start.sh

# 3. 运行启动脚本
./start.sh

# 4. 访问应用
# 打开浏览器访问: http://localhost:9000
```

## 手动部署

### 1. 环境准备

确保已安装:
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置文件
cp env.example .env

# 编辑.env文件，配置以下内容:
# - DATABASE_URL: 数据库连接
# - REDIS_URL: Redis连接
# - SECRET_KEY: JWT密钥
# - OPENAI_API_KEY 或 DASHSCOPE_API_KEY: AI服务密钥
```

### 4. 初始化数据库

```bash
# 进入后端目录
cd ../backend

# 运行初始化脚本
python scripts/init_db.py

# 返回web-server目录
cd ../web-server
```

### 5. 启动服务

```bash
# 开发环境
python main.py

# 生产环境
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:9000
```

## 目录结构

```
web-server/
├── main.py                 # 主程序入口
├── requirements.txt        # Python依赖
├── env.example            # 环境变量示例
├── start.sh               # Linux启动脚本
├── start.bat              # Windows启动脚本
├── 部署文档.md            # 详细部署文档
├── static/                # 静态文件
│   ├── css/
│   │   └── style.css     # 样式文件
│   ├── js/
│   │   └── app.js        # JavaScript文件
│   └── images/           # 图片资源
└── templates/             # HTML模板
    └── index.html        # 主页面
```

## 功能说明

### 首页
- 功能卡片展示（AI咨询、训练方案、体测分析、健康知识）
- 快捷入口（运动指导、营养建议、体能训练、心理健康）

### AI助手
- 实时对话交互
- 消息历史记录
- 来源标识（内部资源/互联网）

### 历史记录
- 对话列表展示
- 对话详情查看
- 对话删除功能

### 个人中心
- 用户登录/注册
- 个人信息展示
- 设置和关于

## API接口

Web服务器复用后端API，主要接口包括:

- `POST /api/auth/login` - 用户登录
- `POST /api/chat/send` - 发送消息
- `GET /api/conversation/list` - 获取对话列表
- `GET /api/conversation/{id}` - 获取对话详情
- `DELETE /api/conversation/{id}` - 删除对话
- `GET /health` - 健康检查

## 配置说明

### 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| DATABASE_URL | 数据库连接URL | 是 |
| REDIS_URL | Redis连接URL | 是 |
| SECRET_KEY | JWT密钥 | 是 |
| OPENAI_API_KEY | OpenAI API密钥 | 否* |
| DASHSCOPE_API_KEY | 通义千问API密钥 | 否* |

*注: OPENAI_API_KEY 和 DASHSCOPE_API_KEY 至少配置一个

### 端口配置

默认端口: **9000**

可在 `main.py` 中修改:
```python
uvicorn.run("main:app", host="0.0.0.0", port=9000)
```

## 生产环境部署

详细的生产环境部署指南请参考 [部署文档.md](./部署文档.md)，包括:

- Systemd服务配置
- Nginx反向代理
- HTTPS配置
- Docker部署
- 监控和日志
- 备份策略

## 常见问题

### 1. 端口被占用

修改 `main.py` 中的端口号，或停止占用9000端口的进程。

### 2. 数据库连接失败

检查PostgreSQL服务是否运行，配置是否正确。

### 3. Redis连接失败

检查Redis服务是否运行，配置是否正确。

### 4. 静态文件无法加载

确保 `static` 目录存在且包含所有必要文件。

## 与小程序的区别

| 特性 | 小程序版 | Web服务器版 |
|------|---------|------------|
| 访问方式 | 微信小程序 | 浏览器 |
| 登录方式 | 微信授权 | 用户名密码 |
| 部署端口 | - | 9000 |
| 界面设计 | WXML/WXSS | HTML/CSS |
| 数据存储 | 共享后端 | 共享后端 |

## 更新日志

### v1.0.0 (2024-01-19)
- 初始版本发布
- 实现核心功能
- 完成界面开发
- 编写部署文档

## 技术支持

详细文档请参考:
- [部署文档.md](./部署文档.md) - 完整的部署指南
- [../docs/API文档.md](../docs/API文档.md) - API接口文档

## 许可证

本项目与主项目使用相同的许可证。
