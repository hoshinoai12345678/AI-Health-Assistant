"""
Redis缓存管理模块
提供统一的缓存接口和策略
"""
from typing import Optional, Any
import json
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """连接Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            self._connected = True
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self._connected = False
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
            logger.info("Redis连接已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self._connected:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: int = 3600
    ) -> bool:
        """设置缓存"""
        if not self._connected:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            await self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self._connected:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self._connected:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"检查缓存失败 {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有缓存"""
        if not self._connected:
            return 0
        
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"清除缓存失败 {pattern}: {e}")
            return 0


# 全局缓存管理器实例
cache_manager = CacheManager()


# 缓存键生成器
class CacheKeys:
    """缓存键命名空间"""
    
    @staticmethod
    def user_info(user_id: int) -> str:
        return f"user:info:{user_id}"
    
    @staticmethod
    def user_role(user_id: int) -> str:
        return f"user:role:{user_id}"
    
    @staticmethod
    def resource_keywords() -> str:
        return "resource:keywords:all"
    
    @staticmethod
    def resource_by_keyword(keyword: str) -> str:
        return f"resource:keyword:{keyword}"
    
    @staticmethod
    def conversation_list(user_id: int) -> str:
        return f"conversation:list:{user_id}"
    
    @staticmethod
    def conversation_detail(conversation_id: int) -> str:
        return f"conversation:detail:{conversation_id}"
    
    @staticmethod
    def fitness_standards() -> str:
        return "fitness:standards:all"
    
    @staticmethod
    def safety_keywords() -> str:
        return "safety:keywords:all"


# 缓存过期时间（秒）
class CacheExpire:
    """缓存过期时间常量"""
    MINUTE_1 = 60
    MINUTE_5 = 300
    MINUTE_15 = 900
    HOUR_1 = 3600
    HOUR_6 = 21600
    DAY_1 = 86400
    WEEK_1 = 604800
