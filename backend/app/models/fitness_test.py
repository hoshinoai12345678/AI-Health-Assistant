"""
体测数据模型
"""
from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FitnessTest(Base):
    """体测数据表"""
    __tablename__ = "fitness_tests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    test_date = Column(Date, nullable=False)
    
    # 体测项目
    height = Column(Numeric(5, 2))  # 身高(cm)
    weight = Column(Numeric(5, 2))  # 体重(kg)
    bmi = Column(Numeric(5, 2))  # BMI
    vital_capacity = Column(Integer)  # 肺活量(ml)
    fifty_meter_run = Column(Numeric(5, 2))  # 50米跑(秒)
    standing_long_jump = Column(Integer)  # 立定跳远(cm)
    sit_and_reach = Column(Numeric(5, 2))  # 坐位体前屈(cm)
    one_minute_sit_ups = Column(Integer)  # 一分钟仰卧起坐(次)
    pull_ups = Column(Integer)  # 引体向上(次)
    endurance_run = Column(Numeric(6, 2))  # 耐力跑(秒)
    total_score = Column(Numeric(5, 2))  # 总分
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    student = relationship("Student", back_populates="fitness_tests")

    def __repr__(self):
        return f"<FitnessTest(id={self.id}, student_id={self.student_id})>"
