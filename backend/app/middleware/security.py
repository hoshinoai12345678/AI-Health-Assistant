"""
安全加固中间件
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """API限流中间件"""
    
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = request.client.host
        
        # 清理过期记录
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        # 检查限流
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"限流触发: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"}
            )
        
        # 记录请求
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = \
            "max-age=31536000; includeSubDomains"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        logger.info(
            f"请求开始: {request.method} {request.url.path}"
        )
        
        try:
            response = await call_next(request)
            
            # 记录响应
            duration = time.time() - start_time
            logger.info(
                f"请求完成: {request.method} {request.url.path} "
                f"状态码={response.status_code} 耗时={duration:.3f}秒"
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"请求失败: {request.method} {request.url.path} "
                f"错误={str(e)} 耗时={duration:.3f}秒"
            )
            raise
