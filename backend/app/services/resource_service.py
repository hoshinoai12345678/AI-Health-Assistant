"""
资源检索服务（优化版）
"""
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resource import InternalResource
from app.core.cache import cache_manager, CacheKeys, CacheExpire
from app.core.performance import timing_decorator, performance_metrics
import logging

logger = logging.getLogger(__name__)


class ResourceService:
    """资源检索服务"""
    
    @timing_decorator
    async def search_internal(
        self,
        keywords: List[str],
        category: Optional[str],
        db: AsyncSession,
        limit: int = 10
    ) -> List[InternalResource]:
        """
        搜索内部资源（带缓存）
        
        Args:
            keywords: 关键词列表
            category: 资源分类
            db: 数据库会话
            limit: 返回数量限制
            
        Returns:
            资源列表
        """
        # 尝试从缓存获取
        if keywords and len(keywords) == 1:
            cache_key = CacheKeys.resource_by_keyword(keywords[0])
            cached = await cache_manager.get(cache_key)
            if cached:
                performance_metrics.record_cache_hit()
                logger.debug(f"缓存命中: {cache_key}")
                return [InternalResource(**item) for item in cached]
            performance_metrics.record_cache_miss()
        
        query = select(InternalResource)
        
        # 按分类筛选
        if category:
            query = query.where(InternalResource.category == category)
        
        # 关键词匹配
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    InternalResource.keywords.contains([keyword])
                )
            
            if keyword_conditions:
                query = query.where(or_(*keyword_conditions))
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        resources = result.scalars().all()
        
        # 缓存结果
        if keywords and len(keywords) == 1 and resources:
            cache_key = CacheKeys.resource_by_keyword(keywords[0])
            cache_data = [
                {
                    "id": r.id,
                    "title": r.title,
                    "content": r.content,
                    "type": r.type,
                    "category": r.category,
                    "keywords": r.keywords,
                    "file_url": r.file_url,
                }
                for r in resources
            ]
            await cache_manager.set(
                cache_key, cache_data, CacheExpire.HOUR_1
            )
        
        return resources
    
    async def get_by_type(
        self,
        resource_type: str,
        db: AsyncSession,
        limit: int = 10
    ) -> List[InternalResource]:
        """
        按类型获取资源
        """
        query = select(InternalResource).where(
            InternalResource.type == resource_type
        ).limit(limit)
        
        result = await db.execute(query)
        resources = result.scalars().all()
        
        return resources
    
    def format_resource_response(
        self,
        resources: List[InternalResource],
        source: str = "internal"
    ) -> str:
        """
        格式化资源响应
        """
        if not resources:
            return None
        
        response_parts = []
        
        for idx, resource in enumerate(resources, 1):
            part = f"{idx}. {resource.title}\n"
            if resource.content:
                part += f"{resource.content}\n"
            if resource.file_url:
                part += f"资源链接：{resource.file_url}\n"
            response_parts.append(part)
        
        response = "\n".join(response_parts)
        
        if source == "internal":
            response += "\n\n（内容来自于北京市学校体育联合会）"
        
        return response


# 创建全局资源服务实例
resource_service = ResourceService()
