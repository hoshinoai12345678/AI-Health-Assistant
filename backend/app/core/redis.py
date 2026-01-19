"""
Redis缓存配置
"""
import redis.asyncio as redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接Redis"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        print("✅ Redis连接成功")
    
    async def close(self):
        """关闭Redis连接"""
        if self.redis:
            await self.redis.close()
            print("👋 Redis连接已关闭")
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        if not self.redis:
            return None
        return await self.redis.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        if not self.redis:
            return False
        return await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis:
            return False
        return await self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if not self.redis:
            return False
        return await self.redis.exists(key) > 0


# 创建全局Redis客户端实例
redis_client = RedisClient()
