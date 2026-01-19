# AI大健康助手 - 实施计划（第一阶段）

## 📋 文档信息
- **项目名称**：AI大健康助手
- **版本**：v1.0
- **创建日期**：2026-01-19

---

## 🎯 总体规划

### 开发周期：8周
- **阶段1**：基础架构搭建（第1-2周）
- **阶段2**：核心功能开发（第3-6周）
- **阶段3**：优化与测试（第7-8周）

### 开发原则
1. ✅ **一次只做一个步骤**
2. ✅ **完成后必须验证测试通过**
3. ✅ **通过后提交 Git**
4. ✅ **更新 progress.md 记录进度**
5. ✅ **更新 architecture.md 记录架构变化**
6. ✅ **开始下一步前新建 AI 对话**

### 禁止行为
- ❌ 跳过测试直接进入下一步
- ❌ 一次性生成大量代码
- ❌ 生成单体巨文件（> 200行）
- ❌ 未经确认就重构现有代码

---

## 📅 阶段1：基础架构搭建（第1-2周）

---

### 步骤 1.1：项目初始化

**目标**：创建项目基础结构和配置

**任务清单**：
1. 创建项目目录结构
2. 初始化 Git 仓库
3. 配置开发环境
4. 创建基础配置文件

**具体操作**：

```bash
# 1. 创建项目根目录
mkdir ai-health-assistant
cd ai-health-assistant

# 2. 创建目录结构
mkdir -p backend/{app/{api,models,services,utils,core},tests}
mkdir -p miniprogram/{pages,components,utils,services}
mkdir -p memory-bank
mkdir -p docs
mkdir -p docker

# 3. 初始化 Git
git init
```

**需要创建的文件**：

1. **backend/requirements.txt**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

2. **backend/app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI大健康助手API",
    description="为学生、家长、教师提供大健康服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI大健康助手API服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

3. **backend/app/core/config.py**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI大健康助手"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/health_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI配置
    OPENAI_API_KEY: str = ""
    DASHSCOPE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

4. **.gitignore**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# 日志
*.log

# 数据库
*.db
*.sqlite

# 微信小程序
miniprogram/node_modules/
miniprogram/miniprogram_npm/
```

5. **README.md**
```markdown
# AI大健康助手

## 项目简介
为学生、家长、教师及教育主管部门提供大健康AI助手服务。

## 技术栈
- 前端：微信小程序原生 + TypeScript
- 后端：Python + FastAPI
- 数据库：PostgreSQL + Redis
- AI：阿里云通义千问

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端启动
使用微信开发者工具打开 miniprogram 目录

## 文档
- [产品需求文档](memory-bank/product-requirements.md)
- [技术栈文档](memory-bank/tech-stack.md)
- [实施计划](memory-bank/implementation-plan-phase1.md)
```

**验证标准**：
- [ ] 项目目录结构创建完成
- [ ] Git 仓库初始化成功
- [ ] 后端项目可以启动：`uvicorn app.main:app --reload`
- [ ] 访问 http://localhost:8000 返回欢迎信息
- [ ] 访问 http://localhost:8000/docs 可以看到 API 文档

**预计时间**：2小时

---

### 步骤 1.2：数据库设计与初始化

**目标**：设计并创建数据库表结构

**任务清单**：
1. 设计数据库表结构
2. 创建数据库模型
3. 配置数据库连接
4. 创建数据库迁移脚本

**数据库表设计**：

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL, -- teacher/student/parent/admin
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学生信息表
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    grade VARCHAR(20),
    class_name VARCHAR(50),
    school_id INTEGER,
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 体测数据表
CREATE TABLE fitness_tests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    test_date DATE NOT NULL,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    bmi DECIMAL(5,2),
    vital_capacity INTEGER,
    fifty_meter_run DECIMAL(5,2),
    standing_long_jump INTEGER,
    sit_and_reach DECIMAL(5,2),
    one_minute_sit_ups INTEGER,
    pull_ups INTEGER,
    endurance_run DECIMAL(6,2),
    total_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话会话表
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话消息表
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- user/assistant/system
    content TEXT NOT NULL,
    source VARCHAR(50), -- internal/internet
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 内部资源表
CREATE TABLE internal_resources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL, -- course/exercise/plan/video
    category VARCHAR(50), -- balance/strength/flexibility/etc
    title VARCHAR(200) NOT NULL,
    content TEXT,
    keywords TEXT[],
    file_url VARCHAR(500),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_openid ON users(openid);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_fitness_tests_student_id ON fitness_tests(student_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_internal_resources_type ON internal_resources(type);
CREATE INDEX idx_internal_resources_keywords ON internal_resources USING GIN(keywords);
```

**创建文件**：

1. **backend/app/models/user.py**
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(String(500))
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

2. **backend/app/core/database.py**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

3. **backend/alembic.ini** 和迁移脚本
```bash
# 安装 alembic
pip install alembic

# 初始化 alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial tables"

# 执行迁移
alembic upgrade head
```

**验证标准**：
- [ ] 数据库连接成功
- [ ] 所有表创建成功
- [ ] 可以插入测试数据
- [ ] 可以查询测试数据
- [ ] 迁移脚本可以正常运行

**预计时间**：4小时

---

### 步骤 1.3：Redis 缓存配置

**目标**：配置 Redis 连接和基础缓存功能

**任务清单**：
1. 配置 Redis 连接
2. 创建缓存工具类
3. 测试缓存功能

**创建文件**：

1. **backend/app/core/redis.py**
```python
import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def close(self):
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        await self.redis.delete(key)

redis_client = RedisClient()
```

2. **backend/app/main.py** (更新)
```python
from fastapi import FastAPI
from app.core.redis import redis_client

app = FastAPI(title="AI大健康助手API")

@app.on_event("startup")
async def startup_event():
    await redis_client.connect()
    print("Redis 连接成功")

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.close()
    print("Redis 连接关闭")
```

**验证标准**：
- [ ] Redis 连接成功
- [ ] 可以设置缓存值
- [ ] 可以获取缓存值
- [ ] 可以删除缓存值
- [ ] 过期时间设置正常

**预计时间**：2小时

---

### 步骤 1.4：微信小程序基础框架

**目标**：创建微信小程序基础结构

**任务清单**：
1. 初始化小程序项目
2. 配置项目基础信息
3. 创建基础页面结构
4. 配置网络请求工具

**创建文件**：

1. **miniprogram/app.json**
```json
{
  "pages": [
    "pages/index/index",
    "pages/chat/chat",
    "pages/history/history",
    "pages/profile/profile"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "AI大健康助手",
    "navigationBarTextStyle": "black"
  },
  "tabBar": {
    "color": "#999",
    "selectedColor": "#1AAD19",
    "backgroundColor": "#fff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/home.png",
        "selectedIconPath": "images/home-active.png"
      },
      {
        "pagePath": "pages/chat/chat",
        "text": "AI助手",
        "iconPath": "images/chat.png",
        "selectedIconPath": "images/chat-active.png"
      },
      {
        "pagePath": "pages/history/history",
        "text": "历史",
        "iconPath": "images/history.png",
        "selectedIconPath": "images/history-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "images/profile.png",
        "selectedIconPath": "images/profile-active.png"
      }
    ]
  },
  "sitemapLocation": "sitemap.json"
}
```

2. **miniprogram/utils/request.ts**
```typescript
interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: any;
}

const BASE_URL = 'https://your-api-domain.com/api';

export function request(options: RequestOptions): Promise<any> {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    
    wx.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          wx.showToast({
            title: '请求失败',
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}
```

3. **miniprogram/pages/index/index.wxml**
```xml
<view class="container">
  <view class="header">
    <text class="title">AI大健康助手</text>
    <text class="subtitle">您的健康管理专家</text>
  </view>
  
  <view class="features">
    <view class="feature-item" bindtap="goToChat">
      <image src="/images/chat-icon.png" class="feature-icon"></image>
      <text class="feature-title">AI咨询</text>
      <text class="feature-desc">智能健康问答</text>
    </view>
    
    <view class="feature-item">
      <image src="/images/plan-icon.png" class="feature-icon"></image>
      <text class="feature-title">训练方案</text>
      <text class="feature-desc">个性化训练计划</text>
    </view>
    
    <view class="feature-item">
      <image src="/images/report-icon.png" class="feature-icon"></image>
      <text class="feature-title">健康报告</text>
      <text class="feature-desc">体测数据分析</text>
    </view>
  </view>
</view>
```

**验证标准**：
- [ ] 小程序可以在开发者工具中打开
- [ ] 页面可以正常显示
- [ ] 底部导航栏正常工作
- [ ] 网络请求工具可以正常调用

**预计时间**：3小时

---

### 步骤 1.5：用户认证系统

**目标**：实现微信登录和JWT认证

**任务清单**：
1. 实现微信登录接口
2. 实现JWT token生成和验证
3. 实现用户信息获取接口
4. 前端集成登录功能

**创建文件**：

1. **backend/app/api/auth.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/auth", tags=["认证"])

class WxLoginRequest(BaseModel):
    code: str
    nickname: str = None
    avatar_url: str = None

@router.post("/wx-login")
async def wx_login(
    request: WxLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """微信登录"""
    # 1. 通过code换取openid
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": "your-appid",
                "secret": "your-secret",
                "js_code": request.code,
                "grant_type": "authorization_code"
            }
        )
        wx_data = response.json()
        
        if "openid" not in wx_data:
            raise HTTPException(status_code=400, detail="微信登录失败")
        
        openid = wx_data["openid"]
    
    # 2. 查询或创建用户
    result = await db.execute(
        select(User).where(User.openid == openid)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            openid=openid,
            role="student",  # 默认角色
            nickname=request.nickname,
            avatar_url=request.avatar_url
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # 3. 生成token
    token = create_access_token({"user_id": user.id, "role": user.role})
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "role": user.role,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        }
    }
```

2. **backend/app/core/security.py**
```python
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except:
        return None
```

3. **miniprogram/pages/profile/profile.ts**
```typescript
Page({
  data: {
    userInfo: null,
    hasLogin: false
  },

  onLoad() {
    this.checkLogin();
  },

  checkLogin() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.getUserInfo();
    }
  },

  async login() {
    try {
      // 1. 获取微信登录code
      const loginRes = await wx.login();
      
      // 2. 获取用户信息
      const userInfoRes = await wx.getUserProfile({
        desc: '用于完善用户资料'
      });
      
      // 3. 调用后端登录接口
      const res = await request({
        url: '/auth/wx-login',
        method: 'POST',
        data: {
          code: loginRes.code,
          nickname: userInfoRes.userInfo.nickName,
          avatar_url: userInfoRes.userInfo.avatarUrl
        }
      });
      
      // 4. 保存token和用户信息
      wx.setStorageSync('token', res.token);
      wx.setStorageSync('userInfo', res.user);
      
      this.setData({
        userInfo: res.user,
        hasLogin: true
      });
      
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });
    } catch (error) {
      wx.showToast({
        title: '登录失败',
        icon: 'none'
      });
    }
  }
});
```

**验证标准**：
- [ ] 用户可以通过微信登录
- [ ] 登录后获得有效的JWT token
- [ ] Token可以正确验证
- [ ] 用户信息正确保存
- [ ] 前端可以获取用户信息

**预计时间**：4小时

---

## 📊 阶段1总结

### 完成的工作
- ✅ 项目初始化
- ✅ 数据库设计与创建
- ✅ Redis缓存配置
- ✅ 微信小程序基础框架
- ✅ 用户认证系统

### 验收标准
- [ ] 后端服务可以正常启动
- [ ] 数据库连接正常
- [ ] Redis缓存正常工作
- [ ] 小程序可以打开并显示
- [ ] 用户可以登录并获得token
- [ ] API文档可以访问

### 下一步
继续 [实施计划第二阶段](memory-bank/implementation-plan-phase2.md)

---

**文档状态**：✅ 已完成  
**最后更新**：2026-01-19  
**预计完成时间**：2周
