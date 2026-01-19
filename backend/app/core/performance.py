"""
性能监控和优化模块
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


def timing_decorator(func: Callable) -> Callable:
    """性能计时装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # 记录慢查询（超过1秒）
            if elapsed > 1.0:
                logger.warning(
                    f"慢操作: {func.__name__} 耗时 {elapsed:.2f}秒"
                )
            else:
                logger.debug(
                    f"{func.__name__} 耗时 {elapsed:.3f}秒"
                )
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{func.__name__} 失败 (耗时 {elapsed:.3f}秒): {e}"
            )
            raise
    
    return wrapper


@asynccontextmanager
async def performance_monitor(operation_name: str):
    """性能监控上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        if elapsed > 1.0:
            logger.warning(
                f"慢操作: {operation_name} 耗时 {elapsed:.2f}秒"
            )
        else:
            logger.debug(
                f"{operation_name} 耗时 {elapsed:.3f}秒"
            )


class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics = {
            "api_calls": {},
            "db_queries": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "ai_requests": 0,
        }
    
    def record_api_call(self, endpoint: str, duration: float):
        """记录API调用"""
        if endpoint not in self.metrics["api_calls"]:
            self.metrics["api_calls"][endpoint] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
            }
        
        stats = self.metrics["api_calls"][endpoint]
        stats["count"] += 1
        stats["total_time"] += duration
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], duration)
    
    def record_db_query(self, query_type: str, duration: float):
        """记录数据库查询"""
        if query_type not in self.metrics["db_queries"]:
            self.metrics["db_queries"][query_type] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
            }
        
        stats = self.metrics["db_queries"][query_type]
        stats["count"] += 1
        stats["total_time"] += duration
        stats["avg_time"] = stats["total_time"] / stats["count"]
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics["cache_misses"] += 1
    
    def record_ai_request(self):
        """记录AI请求"""
        self.metrics["ai_requests"] += 1
    
    def get_cache_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total == 0:
            return 0.0
        return self.metrics["cache_hits"] / total
    
    def get_summary(self) -> dict:
        """获取性能摘要"""
        return {
            **self.metrics,
            "cache_hit_rate": self.get_cache_hit_rate(),
        }
    
    def reset(self):
        """重置指标"""
        self.__init__()


# 全局性能指标实例
performance_metrics = PerformanceMetrics()
