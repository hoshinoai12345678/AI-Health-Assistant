"""
数据库连接池优化配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


# 创建声明式基类
Base = declarative_base()

# 创建异步引擎（优化连接池配置）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,              # 连接池大小
    max_overflow=10,           # 最大溢出连接数
    pool_timeout=30,           # 连接超时时间
    pool_recycle=3600,         # 连接回收时间（1小时）
    pool_pre_ping=True,        # 连接前检查
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
