"""
内部资源数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class InternalResource(Base):
    """内部资源表"""
    __tablename__ = "internal_resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    keywords = Column(ARRAY(String))  # 关键词数组
    file_url = Column(String(500))
    extra_data = Column(JSONB)  # 存储额外信息（避免使用metadata保留字）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<InternalResource(id={self.id}, type={self.type}, title={self.title})>"
