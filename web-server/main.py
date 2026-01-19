"""
Web服务器主程序
部署在9000端口，提供Web界面和API服务
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import sys
import os

# 添加后端路径到系统路径
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

from app.api import auth, chat, conversation, fitness
from app.core.config import settings
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

# 创建FastAPI应用
app = FastAPI(
    title="AI健康助手Web版",
    description="AI大健康助手Web服务器版本",
    version="1.0.0"
)

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 配置模板
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

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
    allow_origins=["*"],  # Web版允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "web-server"
    }


@app.get("/api/info")
async def api_info():
    """API信息"""
    return {
        "name": "AI大健康助手Web版",
        "version": "1.0.0",
        "description": "提供Web界面和API服务",
        "port": 9000
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
