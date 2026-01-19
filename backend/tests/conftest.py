"""
pytest配置文件
"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """数据库会话fixture"""
    # 这里可以配置测试数据库
    pass


@pytest.fixture(scope="function")
def mock_redis():
    """模拟Redis"""
    pass
