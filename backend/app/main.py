"""
FastAPI主应用（优化版）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat, conversation, fitness
from app.core.config import settings
from app.core.cache import cache_manager
from app.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="AI健康助手API",
    description="三精准小程序后端服务",
    version="1.0.0"
)

# 添加安全中间件
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,
    window=60
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(
    conversation.router, 
    prefix="/api/conversation", 
    tags=["对话历史"]
)
app.include_router(
    fitness.router, 
    prefix="/api/fitness", 
    tags=["体测分析"]
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI健康助手API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    await cache_manager.connect()
    logging.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    await cache_manager.disconnect()
    logging.info("应用已关闭")
