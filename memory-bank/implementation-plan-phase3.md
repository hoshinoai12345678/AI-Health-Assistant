# AI大健康助手 - 实施计划（第三阶段）

## 📅 阶段3：优化与测试（第7-8周）

---

### 步骤 3.1：性能优化

**目标**：提升系统响应速度和并发能力

**任务清单**：
1. 添加Redis缓存优化
2. 优化数据库查询
3. 实现接口限流
4. 优化前端加载速度

**后端优化**：

**1. Redis缓存优化**
```python
# backend/app/services/cache_service.py
from app.core.redis import redis_client
import json

class CacheService:
    async def get_cached_response(self, key: str):
        """获取缓存的AI响应"""
        cached = await redis_client.get(f"ai_response:{key}")
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_response(self, key: str, response: dict, expire: int = 3600):
        """缓存AI响应"""
        await redis_client.set(
            f"ai_response:{key}",
            json.dumps(response),
            expire=expire
        )
    
    async def get_hot_resources(self):
        """获取热门资源（缓存）"""
        cached = await redis_client.get("hot_resources")
        if cached:
            return json.loads(cached)
        
        # 从数据库查询
        resources = await self._query_hot_resources()
        
        # 缓存1小时
        await redis_client.set(
            "hot_resources",
            json.dumps(resources),
            expire=3600
        )
        
        return resources
```

**2. 数据库查询优化**
```python
# 添加索引
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_resources_type_category ON internal_resources(type, category);

# 使用连接池
from sqlalchemy.pool import NullPool, QueuePool

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

**3. 接口限流**
```python
# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from app.core.redis import redis_client

async def rate_limit_middleware(request: Request, call_next):
    """限流中间件"""
    user_id = request.state.user_id if hasattr(request.state, 'user_id') else 'anonymous'
    key = f"rate_limit:{user_id}"
    
    # 获取当前请求次数
    count = await redis_client.get(key)
    
    if count and int(count) > 100:  # 每分钟100次
        raise HTTPException(status_code=429, detail="请求过于频繁")
    
    # 增加计数
    if count:
        await redis_client.incr(key)
    else:
        await redis_client.set(key, 1, expire=60)
    
    response = await call_next(request)
    return response
```

**前端优化**：

**1. 图片懒加载**
```xml
<!-- miniprogram/components/lazy-image/lazy-image.wxml -->
<image 
  src="{{loaded ? src : placeholder}}" 
  lazy-load="{{true}}"
  bindload="onLoad"
  class="lazy-image"
/>
```

**2. 分页加载**
```typescript
// miniprogram/pages/history/history.ts
Page({
  data: {
    conversations: [],
    page: 1,
    hasMore: true
  },

  async loadMore() {
    if (!this.data.hasMore) return;
    
    const res = await request({
      url: `/conversation/list?page=${this.data.page}&size=20`,
      method: 'GET'
    });
    
    this.setData({
      conversations: [...this.data.conversations, ...res.data],
      page: this.data.page + 1,
      hasMore: res.hasMore
    });
  }
});
```

**验证标准**：
- [ ] API响应时间 < 500ms
- [ ] 热门资源命中缓存
- [ ] 限流机制正常工作
- [ ] 前端加载流畅

**预计时间**：8小时

---

### 步骤 3.2：全面测试

**目标**：确保系统稳定可靠

**任务清单**：
1. 编写单元测试
2. 编写集成测试
3. 进行压力测试
4. 进行用户体验测试

**单元测试**：

**backend/tests/test_ai_service.py**
```python
import pytest
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_chat():
    """测试AI对话"""
    service = AIService()
    
    messages = [
        {'role': 'user', 'content': '我想要平衡能力训练方案'}
    ]
    
    response = await service.chat(messages, 'teacher')
    
    assert response is not None
    assert len(response) > 0

@pytest.mark.asyncio
async def test_system_prompt():
    """测试系统提示词"""
    service = AIService()
    
    teacher_prompt = service._get_system_prompt('teacher')
    student_prompt = service._get_system_prompt('student')
    
    assert '教学' in teacher_prompt
    assert '学生' in student_prompt
```

**backend/tests/test_keyword_service.py**
```python
from app.services.keyword_service import KeywordService

def test_detect_internal_keywords():
    """测试内部关键词识别"""
    service = KeywordService()
    
    result = service.detect_keywords('我想要课课练方案')
    
    assert result['has_internal'] == True
    assert '课课练' in result['internal_keywords']

def test_detect_excluded_keywords():
    """测试排除关键词"""
    service = KeywordService()
    
    result = service.detect_keywords('我想要语文教学方案')
    
    assert result['is_excluded'] == True
```

**集成测试**：

**backend/tests/test_api.py**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_chat_api():
    """测试对话API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/send",
            json={"message": "我想要平衡能力训练"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data

@pytest.mark.asyncio
async def test_conversation_list():
    """测试对话列表API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/conversation/list",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

**压力测试**：

**backend/tests/load_test.py**
```python
import asyncio
import aiohttp
import time

async def send_request(session, url):
    """发送单个请求"""
    async with session.post(url, json={"message": "测试"}) as response:
        return await response.json()

async def load_test(concurrent_users=100, requests_per_user=10):
    """压力测试"""
    url = "http://localhost:8000/api/chat/send"
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(concurrent_users):
            for _ in range(requests_per_user):
                tasks.append(send_request(session, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    total_time = end_time - start_time
    
    print(f"总请求数: {len(tasks)}")
    print(f"成功请求: {success_count}")
    print(f"失败请求: {len(tasks) - success_count}")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"QPS: {len(tasks) / total_time:.2f}")

if __name__ == '__main__':
    asyncio.run(load_test())
```

**运行测试**：
```bash
# 单元测试
pytest backend/tests/ -v

# 测试覆盖率
pytest backend/tests/ --cov=app --cov-report=html

# 压力测试
python backend/tests/load_test.py
```

**验证标准**：
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有集成测试通过
- [ ] 支持100+并发用户
- [ ] QPS > 50

**预计时间**：12小时

---

### 步骤 3.3：部署准备

**目标**：准备生产环境部署

**任务清单**：
1. 配置Docker容器
2. 配置Nginx
3. 配置SSL证书
4. 编写部署文档

**Docker配置**：

**docker/docker-compose.yml**
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    restart: always

  backend:
    build: ../backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://health_user:health_pass@postgres:5432/health_db
      - REDIS_URL=redis://redis:6379/0
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=health_db
      - POSTGRES_USER=health_user
      - POSTGRES_PASSWORD=health_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    restart: always

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

**Nginx配置**：

**docker/nginx/nginx.conf**
```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name api.health-assistant.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.health-assistant.com;
    
    # SSL证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 日志
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
    
    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

**部署脚本**：

**deploy.sh**
```bash
#!/bin/bash

echo "开始部署 AI大健康助手..."

# 1. 拉取最新代码
git pull origin main

# 2. 构建Docker镜像
cd docker
docker-compose build

# 3. 停止旧容器
docker-compose down

# 4. 启动新容器
docker-compose up -d

# 5. 等待服务启动
sleep 10

# 6. 检查服务状态
docker-compose ps

# 7. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 8. 健康检查
curl -f http://localhost/api/health || exit 1

echo "部署完成！"
```

**验证标准**：
- [ ] Docker容器可以正常启动
- [ ] Nginx配置正确
- [ ] SSL证书配置成功
- [ ] 服务可以通过域名访问

**预计时间**：8小时

---

### 步骤 3.4：文档完善

**目标**：完善项目文档

**任务清单**：
1. 更新API文档
2. 编写部署文档
3. 编写运维文档
4. 编写用户手册

**API文档**（FastAPI自动生成）：
- 访问：https://api.health-assistant.com/docs
- 包含所有接口的详细说明

**部署文档**：

**docs/deployment.md**
```markdown
# 部署文档

## 环境要求
- 服务器：4核8G，Ubuntu 22.04
- Docker 20.10+
- Docker Compose 2.0+

## 部署步骤

### 1. 准备服务器
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 安装Docker Compose
sudo apt install docker-compose-plugin
```

### 2. 克隆代码
```bash
git clone https://github.com/your-org/ai-health-assistant.git
cd ai-health-assistant
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入实际配置
```

### 4. 启动服务
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. 验证部署
```bash
curl https://api.health-assistant.com/health
```

## 常见问题
...
```

**运维文档**：

**docs/operations.md**
```markdown
# 运维文档

## 日常维护

### 查看日志
```bash
# 查看后端日志
docker-compose logs -f backend

# 查看Nginx日志
docker-compose logs -f nginx
```

### 备份数据库
```bash
# 备份
docker-compose exec postgres pg_dump -U health_user health_db > backup.sql

# 恢复
docker-compose exec -T postgres psql -U health_user health_db < backup.sql
```

### 监控指标
- CPU使用率 < 70%
- 内存使用率 < 80%
- 磁盘使用率 < 80%
- API响应时间 < 500ms

## 故障处理
...
```

**验证标准**：
- [ ] API文档完整
- [ ] 部署文档清晰
- [ ] 运维文档实用
- [ ] 用户手册易懂

**预计时间**：6小时

---

### 步骤 3.5：上线前检查

**目标**：确保系统可以安全上线

**检查清单**：

**功能检查**：
- [ ] 用户可以正常登录
- [ ] AI对话功能正常
- [ ] 内部资源检索正常
- [ ] 体测分析功能正常
- [ ] 历史记录功能正常
- [ ] 风险提示正常工作
- [ ] 内容过滤正常工作

**性能检查**：
- [ ] API响应时间 < 3秒
- [ ] 页面加载时间 < 2秒
- [ ] 支持2000+并发用户
- [ ] 缓存命中率 > 60%

**安全检查**：
- [ ] HTTPS配置正确
- [ ] JWT认证正常
- [ ] 数据加密正常
- [ ] 限流机制正常
- [ ] SQL注入防护
- [ ] XSS防护

**合规检查**：
- [ ] 符合微信小程序规范
- [ ] 符合个人信息保护法
- [ ] 内容来源标注清晰
- [ ] 风险提示完整

**监控检查**：
- [ ] 日志记录正常
- [ ] 错误告警配置
- [ ] 性能监控配置
- [ ] 备份策略配置

**预计时间**：4小时

---

## 📊 阶段3总结

### 完成的工作
- ✅ 性能优化
- ✅ 全面测试
- ✅ 部署准备
- ✅ 文档完善
- ✅ 上线前检查

### 最终验收标准
- [ ] 所有功能正常工作
- [ ] 性能指标达标
- [ ] 测试覆盖率 > 80%
- [ ] 安全检查通过
- [ ] 文档完整
- [ ] 可以稳定运行

### 项目交付物
1. ✅ 完整的源代码
2. ✅ 数据库脚本
3. ✅ 部署配置
4. ✅ API文档
5. ✅ 部署文档
6. ✅ 运维文档
7. ✅ 用户手册
8. ✅ 测试报告

---

## 🎉 项目完成

恭喜！AI大健康助手项目开发完成，可以正式上线了！

### 后续工作
1. 持续监控系统运行状态
2. 收集用户反馈
3. 迭代优化功能
4. 扩充内部资源库
5. 开发新功能

---

**文档状态**：✅ 已完成  
**最后更新**：2026-01-19  
**预计完成时间**：2周
