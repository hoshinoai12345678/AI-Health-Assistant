# AI健康助手

## 📋 项目简介

AI健康助手是一个基于微信小程序的智能健康服务平台，为学生、家长、教师及教育主管部门提供包括运动、心理、营养等内容的大健康AI助手服务。

### 核心特性

- 🤖 **AI智能对话**：基于阿里云通义千问的智能问答
- 📚 **二级资源检索**：内部资源优先，互联网资源备用
- 👥 **角色识别**：针对教师、学生、家长、主管部门提供差异化服务
- 📊 **体测分析**：基于学生体测数据生成个性化训练方案
- 🔒 **安全机制**：风险提示、内容过滤、隐私保护

---

## 🛠️ 技术栈

### 前端
- 微信小程序（TypeScript）

### 后端
- Python 3.11+ / FastAPI
- PostgreSQL 15+ / Redis 7+

### AI服务
- 阿里云通义千问

---

## 🚀 快速开始

### 第一步：申请账号

1. **微信小程序**：https://mp.weixin.qq.com/
   - 获取：AppID 和 AppSecret

2. **阿里云通义千问**：https://dashscope.aliyun.com/
   - 获取：API Key（免费100万tokens）

### 第二步：启动服务

```bash
# 1. 克隆项目
git clone https://github.com/hoshinoai12345678/AI-Health-Assistant.git
cd AI-Health-Assistant

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的AppID、AppSecret、API Key

# 3. 启动Docker服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/import_resources.py

# 5. 验证服务
# 访问：http://localhost:8000/health
# 访问：http://localhost:8000/docs
```

### 第三步：开发小程序

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 修改 `project.config.json` 中的 `appid`
3. 修改 `utils/config.ts` 中的 `APP_ID`
4. 点击编译运行

**详细步骤请查看：[快速开始.md](快速开始.md)**

---

## 📁 项目结构

```
AI-Health-Assistant/
├── backend/              # 后端代码
│   ├── app/             # 应用代码
│   ├── tests/           # 测试代码
│   └── scripts/         # 脚本工具
├── miniprogram/         # 小程序前端
│   ├── pages/           # 页面
│   ├── utils/           # 工具函数
│   └── services/        # 服务
├── docs/                # 技术文档
├── memory-bank/         # 项目文档
├── docker-compose.yml   # Docker配置
└── README.md            # 项目说明
```

---

## 📚 文档

### 快速开始
- **[快速开始.md](快速开始.md)** ⭐ 从这里开始！
- [微信小程序开发部署指南.md](微信小程序开发部署指南.md)
- [AI模型API申请配置指南.md](AI模型API申请配置指南.md)

### 技术文档
- [API文档](docs/API文档.md)
- [生产环境部署指南](docs/生产环境部署指南.md)
- [测试指南](docs/测试指南.md)
- [安全加固指南](docs/安全加固指南.md)
- [性能优化指南](docs/性能优化指南.md)

### 项目文档
- [项目总结报告.md](项目总结报告.md)
- [产品需求文档](memory-bank/product-requirements.md)
- [系统架构文档](memory-bank/architecture.md)

---

## 🔐 安全说明

- 所有API请求需要JWT认证
- 敏感数据采用加密存储
- 传输层使用HTTPS加密
- 实施限流防护（100次/分钟/用户）

---

## 🧪 测试

```bash
# 运行单元测试
docker-compose exec backend pytest tests/ -v

# 查看测试覆盖率
docker-compose exec backend pytest --cov=app tests/
```

---

## 🔧 常用命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 完全清理
docker-compose down -v
```

---

## 📄 许可证

本项目由北京市学校体育联合会开发和维护。

---

**当前版本**: v1.0.0  
**最后更新**: 2026-01-19  
**开发状态**: ✅ 已完成
