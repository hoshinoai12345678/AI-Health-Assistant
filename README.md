# AI大健康助手

## 📋 项目简介

AI大健康助手是一个基于微信小程序的智能健康服务平台，为学生、家长、教师及教育主管部门提供包括运动、心理、营养等内容的大健康AI助手服务。

### 核心特性

- 🤖 **AI智能对话**：基于大语言模型的智能问答
- 📚 **二级资源检索**：内部资源优先，互联网资源备用
- 👥 **角色识别**：针对教师、学生、家长、主管部门提供差异化服务
- 📊 **体测分析**：基于学生体测数据生成个性化训练方案
- 🔒 **安全机制**：风险提示、内容过滤、隐私保护

## 🛠️ 技术栈

### 前端
- 微信小程序原生开发
- TypeScript
- Vant Weapp（UI组件库）
- MobX（状态管理）

### 后端
- Python 3.11+
- FastAPI（Web框架）
- PostgreSQL 15+（主数据库）
- Redis 7+（缓存）
- MinIO（文件存储）

### AI服务
- 阿里云通义千问（LLM）
- Milvus（向量数据库）

## 🚀 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 微信开发者工具

### 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入实际配置

# 6. 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 前端启动

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 配置小程序AppID
3. 点击编译运行

## 📁 项目结构

```
ai-health-assistant/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   ├── core/        # 核心配置
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试代码
│   └── requirements.txt # Python依赖
├── miniprogram/         # 小程序前端
│   ├── pages/           # 页面
│   ├── components/      # 组件
│   └── utils/           # 工具函数
├── memory-bank/         # 项目文档
├── docker/              # Docker配置
└── docs/                # 其他文档
```

## 📚 文档

- [产品需求文档](memory-bank/product-requirements.md)
- [技术栈文档](memory-bank/tech-stack.md)
- [系统架构文档](memory-bank/architecture.md)
- [实施计划 - 第一阶段](memory-bank/implementation-plan-phase1.md)
- [实施计划 - 第二阶段](memory-bank/implementation-plan-phase2.md)
- [实施计划 - 第三阶段](memory-bank/implementation-plan-phase3.md)
- [项目进度](memory-bank/progress.md)

## 🔐 安全说明

- 所有API请求需要JWT认证
- 敏感数据采用AES-256加密
- 传输层使用HTTPS加密
- 实施限流防护（100次/分钟/用户）

## 📝 开发规范

- 单文件不超过200行
- 必须添加类型提示
- 必须添加注释
- 遵循PEP 8（Python）和ESLint（TypeScript）
- 提交前必须通过测试

详见 [.cursorrules](.cursorrules)

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_api.py

# 查看测试覆盖率
pytest --cov=app tests/
```

## 📦 部署

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目由北京市学校体育联合会开发和维护。

## 📞 联系方式

如有问题，请联系项目负责人。

---

**当前版本**: v1.0.0  
**最后更新**: 2026-01-19  
**开发状态**: 🚧 开发中
