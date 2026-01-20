# AI大健康助手 - Web服务器版

## 项目简介

AI大健康助手的Web服务器版本，提供与微信小程序相同的功能和界面体验。用户可以通过浏览器访问，无需安装小程序。

## 主要特性

- ✅ **完整功能**: AI健康咨询、对话历史、个人中心
- ✅ **响应式设计**: 支持PC端和移动端访问
- ✅ **一键部署**: CentOS服务器自动化部署脚本
- ✅ **API复用**: 复用后端API服务，保持数据一致性

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: FastAPI + Python 3.8+
- **数据库**: PostgreSQL
- **缓存**: Redis
- **AI服务**: 阿里云通义千问

---

## 🚀 快速开始

### CentOS服务器（一键部署）⭐ 推荐

```bash
cd /opt/ctz_project/web-server
chmod +x start.sh && sudo ./start.sh
```

**脚本会自动完成：**
- ✅ 安装Python、PostgreSQL、Redis
- ✅ 配置防火墙（开放9000端口）
- ✅ 创建虚拟环境并安装依赖
- ✅ 初始化数据库
- ✅ 启动Web服务器

**访问地址：** `http://服务器IP:9000`

**默认配置：**
- 数据库密码: `123456`
- API Key: `sk-a67e8c874a694d48a81b72dcdebeb045`

### Windows系统

```bash
cd web-server
start.bat
```

访问: `http://localhost:9000`

---

## 📋 配置说明

### 默认配置

| 配置项 | 值 |
|--------|-----|
| Web端口 | 9000 |
| 数据库密码 | 123456 |
| API Key | sk-a67e8c874a694d48a81b72dcdebeb045 |

### 修改配置

```bash
vim /opt/ctz_project/web-server/.env
```

⚠️ **生产环境请务必修改默认密码！**

---

## 🔧 常用命令

```bash
# 查看服务状态
sudo systemctl status postgresql redis

# 测试服务
curl http://localhost:9000/health

# 查看日志
sudo journalctl -u health-web -f

# 重启服务
sudo systemctl restart health-web
```

---

## 📚 详细文档

- [部署文档.md](./部署文档.md) - 完整的部署指南、生产环境配置、故障排查

---

## 🆘 常见问题

**Q: 外网无法访问？**  
A: 检查云服务器安全组，确保开放9000端口

**Q: 数据库连接失败？**  
A: `sudo systemctl start postgresql`

**Q: 端口被占用？**  
A: `sudo lsof -i :9000` 查看占用进程

更多问题请查看 [部署文档.md](./部署文档.md)

---

**最后更新**: 2026年1月19日  
**版本**: v1.0.0
