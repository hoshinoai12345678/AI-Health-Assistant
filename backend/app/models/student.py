"""
学生数据模型
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Student(Base):
    """学生信息表"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    grade = Column(String(20))
    class_name = Column(String(50))
    school_id = Column(Integer)
    birth_date = Column(Date)
    created_at = Column(Date, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="students")
    fitness_tests = relationship("FitnessTest", back_populates="student")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, grade={self.grade})>"
