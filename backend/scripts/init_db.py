"""
数据库初始化脚本
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine, Base
from app.models.user import User
from app.models.student import Student
from app.models.fitness_test import FitnessTest
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.resource import InternalResource


async def create_tables():
    """创建所有数据表"""
    async with engine.begin() as conn:
        # 删除所有表（仅开发环境）
        await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 数据库表创建成功")


async def create_indexes():
    """创建索引"""
    async with engine.begin() as conn:
        # 为keywords字段创建GIN索引（用于数组搜索）
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_resources_keywords "
            "ON internal_resources USING GIN(keywords)"
        ))
        print("✅ 索引创建成功")


async def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    await create_tables()
    await create_indexes()
    print("✅ 数据库初始化完成")


if __name__ == "__main__":
    asyncio.run(init_database())
