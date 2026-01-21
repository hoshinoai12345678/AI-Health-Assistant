"""
学生体测数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class StudentFitnessData(Base):
    """学生体测数据表"""
    __tablename__ = "student_fitness_data"
    
    id = Column(Integer, primary_key=True, index=True)
    grade_code = Column(String(50), index=True, comment="年级编号")
    grade_name = Column(String(50), comment="年级")
    class_name = Column(String(50), index=True, comment="班级名称")
    student_id = Column(String(50), unique=True, index=True, comment="学生编号")
    gender = Column(String(10), comment="性别")
    
    # 身体指标
    height = Column(Float, comment="身高")
    weight = Column(Float, comment="体重")
    weight_score = Column(Float, comment="体重评分")
    weight_level = Column(String(20), comment="体重等级")
    
    # 肺活量
    lung_capacity = Column(Float, comment="肺活量")
    lung_capacity_score = Column(Float, comment="肺活量评分")
    lung_capacity_level = Column(String(20), comment="肺活量等级")
    
    # 50米跑
    run_50m = Column(Float, comment="50米跑")
    run_50m_score = Column(Float, comment="50米跑评分")
    run_50m_level = Column(String(20), comment="50米跑等级")
    
    # 坐位体前屈
    sit_reach = Column(Float, comment="坐位体前屈")
    sit_reach_score = Column(Float, comment="坐位体前屈评分")
    sit_reach_level = Column(String(20), comment="坐位体前屈等级")
    
    # 仰卧起坐
    sit_up = Column(Integer, comment="一分钟仰卧起坐")
    sit_up_score = Column(Float, comment="一分钟仰卧起坐评分")
    sit_up_level = Column(String(20), comment="一分钟仰卧起坐等级")
    sit_up_bonus = Column(Float, comment="一分钟仰卧起坐附加分")
    
    # 跳绳
    rope_skip = Column(Integer, comment="一分钟跳绳")
    rope_skip_score = Column(Float, comment="一分钟跳绳评分")
    rope_skip_level = Column(String(20), comment="一分钟跳绳等级")
    rope_skip_bonus = Column(Float, comment="一分钟跳绳附加分")
    
    # 立定跳远
    standing_jump = Column(Float, comment="立定跳远")
    standing_jump_score = Column(Float, comment="立定跳远评分")
    standing_jump_level = Column(String(20), comment="立定跳远等级")
    
    # 800米跑（女）
    run_800m = Column(String(20), comment="800米跑")
    run_800m_score = Column(Float, comment="800米跑评分")
    run_800m_level = Column(String(20), comment="800米跑等级")
    run_800m_bonus = Column(Float, comment="800米跑附加分")
    
    # 1000米跑（男）
    run_1000m = Column(String(20), comment="1000米跑")
    run_1000m_score = Column(Float, comment="1000米跑评分")
    run_1000m_level = Column(String(20), comment="1000米跑等级")
    run_1000m_bonus = Column(Float, comment="1000米跑附加分")
    
    # 引体向上（男）
    pull_up = Column(Integer, comment="引体向上")
    pull_up_score = Column(Float, comment="引体向上评分")
    pull_up_level = Column(String(20), comment="引体向上等级")
    pull_up_bonus = Column(Float, comment="引体向上附加分")
    
    # 50米×8往返跑
    run_50m_8 = Column(String(20), comment="50米×8往返跑")
    run_50m_8_score = Column(Float, comment="50米×8往返跑评分")
    run_50m_8_level = Column(String(20), comment="50米×8往返跑等级")
    
    # 总分
    standard_score = Column(Float, comment="标准分")
    bonus_score = Column(Float, comment="附加分")
    total_score = Column(Float, comment="总分")
    total_level = Column(String(20), comment="总分等级")
    
    # 元数据
    upload_time = Column(DateTime, default=datetime.now, comment="上传时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class SportsExercise(Base):
    """体育动作库表"""
    __tablename__ = "sports_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, comment="名称")
    source = Column(String(50), comment="来源")
    code = Column(String(50), unique=True, index=True, comment="编号")
    description = Column(String(2000), comment="说明")
    equipment = Column(String(200), comment="使用器械")
    form = Column(String(50), comment="开展形式")
    movement_type = Column(String(50), comment="运动方式")
    difficulty = Column(String(20), comment="难度等级")
    suitable_level = Column(String(100), comment="适用水平")
    fitness_quality = Column(String(200), comment="锻炼身体素质")
    improve_test = Column(String(200), comment="提升体测项目")
    image_url = Column(String(500), comment="图片")
    
    # 元数据
    upload_time = Column(DateTime, default=datetime.now, comment="上传时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
