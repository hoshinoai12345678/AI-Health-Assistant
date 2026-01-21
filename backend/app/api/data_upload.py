"""
数据上传API
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.student_data import StudentFitnessData, SportsExercise

router = APIRouter()


@router.post("/upload/fitness-data")
async def upload_fitness_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传学生体测数据（Excel格式）
    Web版本：无需认证（生产环境建议添加认证）
    """
    # 检查文件格式
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="仅支持Excel或CSV格式文件")
    
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型读取数据
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 数据清洗和验证
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查学生编号是否存在（保留前导0）
                student_id_raw = row.get('学生编号', '')
                if pd.isna(student_id_raw):
                    continue
                    
                # 转换为字符串并保留前导0
                if isinstance(student_id_raw, (int, float)):
                    # 如果是数字，转为字符串并补齐到9位
                    student_id = str(int(student_id_raw)).zfill(9)
                else:
                    student_id = str(student_id_raw).strip()
                
                if not student_id or student_id == 'nan':
                    continue
                
                # 检查是否已存在
                existing = db.query(StudentFitnessData).filter(
                    StudentFitnessData.student_id == student_id
                ).first()
                
                if existing:
                    # 更新现有记录
                    for col in df.columns:
                        field_map = {
                            '年级编号': 'grade_code',
                            '年级': 'grade_name',
                            '班级名称': 'class_name',
                            '性别': 'gender',
                            '身高': 'height',
                            '体重': 'weight',
                            '体重评分': 'weight_score',
                            '体重等级': 'weight_level',
                            '肺活量': 'lung_capacity',
                            '肺活量评分': 'lung_capacity_score',
                            '肺活量等级': 'lung_capacity_level',
                            '50米跑': 'run_50m',
                            '50米跑评分': 'run_50m_score',
                            '50米跑等级': 'run_50m_level',
                            '坐位体前屈': 'sit_reach',
                            '坐位体前屈评分': 'sit_reach_score',
                            '坐位体前屈等级': 'sit_reach_level',
                            '一分钟仰卧起坐': 'sit_up',
                            '一分钟仰卧起坐评分': 'sit_up_score',
                            '一分钟仰卧起坐等级': 'sit_up_level',
                            '一分钟仰卧起坐附加分': 'sit_up_bonus',
                            '一分钟跳绳': 'rope_skip',
                            '一分钟跳绳评分': 'rope_skip_score',
                            '一分钟跳绳等级': 'rope_skip_level',
                            '一分钟跳绳附加分': 'rope_skip_bonus',
                            '立定跳远': 'standing_jump',
                            '立定跳远评分': 'standing_jump_score',
                            '立定跳远等级': 'standing_jump_level',
                            '800米跑': 'run_800m',
                            '800米跑评分': 'run_800m_score',
                            '800米跑等级': 'run_800m_level',
                            '800米跑附加分': 'run_800m_bonus',
                            '1000米跑': 'run_1000m',
                            '1000米跑评分': 'run_1000m_score',
                            '1000米跑等级': 'run_1000m_level',
                            '1000米跑附加分': 'run_1000m_bonus',
                            '引体向上': 'pull_up',
                            '引体向上评分': 'pull_up_score',
                            '引体向上等级': 'pull_up_level',
                            '引体向上附加分': 'pull_up_bonus',
                            '50米×8往返跑': 'run_50m_8',
                            '50米×8往返跑评分': 'run_50m_8_score',
                            '50米×8往返跑等级': 'run_50m_8_level',
                            '标准分': 'standard_score',
                            '附加分': 'bonus_score',
                            '总分': 'total_score',
                            '总分等级': 'total_level',
                        }
                        if col in field_map:
                            value = row[col]
                            if pd.notna(value):
                                setattr(existing, field_map[col], value)
                    existing.update_time = datetime.now()
                else:
                    # 创建新记录
                    student_data = StudentFitnessData(
                        grade_code=str(row.get('年级编号', '')),
                        grade_name=str(row.get('年级', '')),
                        class_name=str(row.get('班级名称', '')),
                        student_id=student_id,
                        gender=str(row.get('性别', '')),
                        height=float(row['身高']) if pd.notna(row.get('身高')) else None,
                        weight=float(row['体重']) if pd.notna(row.get('体重')) else None,
                        weight_score=float(row['体重评分']) if pd.notna(row.get('体重评分')) else None,
                        weight_level=str(row.get('体重等级', '')),
                        lung_capacity=float(row['肺活量']) if pd.notna(row.get('肺活量')) else None,
                        lung_capacity_score=float(row['肺活量评分']) if pd.notna(row.get('肺活量评分')) else None,
                        lung_capacity_level=str(row.get('肺活量等级', '')),
                        run_50m=float(row['50米跑']) if pd.notna(row.get('50米跑')) else None,
                        run_50m_score=float(row['50米跑评分']) if pd.notna(row.get('50米跑评分')) else None,
                        run_50m_level=str(row.get('50米跑等级', '')),
                        sit_reach=float(row['坐位体前屈']) if pd.notna(row.get('坐位体前屈')) else None,
                        sit_reach_score=float(row['坐位体前屈评分']) if pd.notna(row.get('坐位体前屈评分')) else None,
                        sit_reach_level=str(row.get('坐位体前屈等级', '')),
                        sit_up=int(row['一分钟仰卧起坐']) if pd.notna(row.get('一分钟仰卧起坐')) else None,
                        sit_up_score=float(row['一分钟仰卧起坐评分']) if pd.notna(row.get('一分钟仰卧起坐评分')) else None,
                        sit_up_level=str(row.get('一分钟仰卧起坐等级', '')),
                        sit_up_bonus=float(row['一分钟仰卧起坐附加分']) if pd.notna(row.get('一分钟仰卧起坐附加分')) else None,
                        rope_skip=int(row['一分钟跳绳']) if pd.notna(row.get('一分钟跳绳')) else None,
                        rope_skip_score=float(row['一分钟跳绳评分']) if pd.notna(row.get('一分钟跳绳评分')) else None,
                        rope_skip_level=str(row.get('一分钟跳绳等级', '')),
                        rope_skip_bonus=float(row['一分钟跳绳附加分']) if pd.notna(row.get('一分钟跳绳附加分')) else None,
                        standing_jump=float(row['立定跳远']) if pd.notna(row.get('立定跳远')) else None,
                        standing_jump_score=float(row['立定跳远评分']) if pd.notna(row.get('立定跳远评分')) else None,
                        standing_jump_level=str(row.get('立定跳远等级', '')),
                        run_800m=str(row.get('800米跑', '')),
                        run_800m_score=float(row['800米跑评分']) if pd.notna(row.get('800米跑评分')) else None,
                        run_800m_level=str(row.get('800米跑等级', '')),
                        run_800m_bonus=float(row['800米跑附加分']) if pd.notna(row.get('800米跑附加分')) else None,
                        run_1000m=str(row.get('1000米跑', '')),
                        run_1000m_score=float(row['1000米跑评分']) if pd.notna(row.get('1000米跑评分')) else None,
                        run_1000m_level=str(row.get('1000米跑等级', '')),
                        run_1000m_bonus=float(row['1000米跑附加分']) if pd.notna(row.get('1000米跑附加分')) else None,
                        pull_up=int(row['引体向上']) if pd.notna(row.get('引体向上')) else None,
                        pull_up_score=float(row['引体向上评分']) if pd.notna(row.get('引体向上评分')) else None,
                        pull_up_level=str(row.get('引体向上等级', '')),
                        pull_up_bonus=float(row['引体向上附加分']) if pd.notna(row.get('引体向上附加分')) else None,
                        run_50m_8=str(row.get('50米×8往返跑', '')),
                        run_50m_8_score=float(row['50米×8往返跑评分']) if pd.notna(row.get('50米×8往返跑评分')) else None,
                        run_50m_8_level=str(row.get('50米×8往返跑等级', '')),
                        standard_score=float(row['标准分']) if pd.notna(row.get('标准分')) else None,
                        bonus_score=float(row['附加分']) if pd.notna(row.get('附加分')) else None,
                        total_score=float(row['总分']) if pd.notna(row.get('总分')) else None,
                        total_level=str(row.get('总分等级', '')),
                    )
                    db.add(student_data)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"第{index+2}行: {str(e)}")
        
        # 提交事务
        db.commit()
        
        return {
            "success": True,
            "message": f"上传成功！成功导入{success_count}条数据，失败{error_count}条",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]  # 只返回前10条错误
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")


@router.post("/upload/sports-exercises")
async def upload_sports_exercises(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传体育动作库（Excel格式）
    Web版本：无需认证（生产环境建议添加认证）
    """
    # 检查文件格式
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="仅支持Excel或CSV格式文件")
    
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 根据文件类型读取数据
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # 数据清洗和验证
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查编号是否存在
                code = str(row.get('编号', '')).strip()
                if not code or code == 'nan':
                    continue
                
                # 检查是否已存在
                existing = db.query(SportsExercise).filter(
                    SportsExercise.code == code
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.name = str(row.get('名称', ''))
                    existing.source = str(row.get('来源', ''))
                    existing.description = str(row.get('说明', ''))
                    existing.equipment = str(row.get('使用器械', ''))
                    existing.form = str(row.get('开展形式', ''))
                    existing.movement_type = str(row.get('运动方式', ''))
                    existing.difficulty = str(row.get('难度等级', ''))
                    existing.suitable_level = str(row.get('适用水平', ''))
                    existing.fitness_quality = str(row.get('锻炼身体素质', ''))
                    existing.improve_test = str(row.get('提升体测项目', ''))
                    existing.image_url = str(row.get('图片', ''))
                    existing.update_time = datetime.now()
                else:
                    # 创建新记录
                    exercise = SportsExercise(
                        name=str(row.get('名称', '')),
                        source=str(row.get('来源', '')),
                        code=code,
                        description=str(row.get('说明', '')),
                        equipment=str(row.get('使用器械', '')),
                        form=str(row.get('开展形式', '')),
                        movement_type=str(row.get('运动方式', '')),
                        difficulty=str(row.get('难度等级', '')),
                        suitable_level=str(row.get('适用水平', '')),
                        fitness_quality=str(row.get('锻炼身体素质', '')),
                        improve_test=str(row.get('提升体测项目', '')),
                        image_url=str(row.get('图片', ''))
                    )
                    db.add(exercise)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"第{index+2}行: {str(e)}")
        
        # 提交事务
        db.commit()
        
        return {
            "success": True,
            "message": f"上传成功！成功导入{success_count}条数据，失败{error_count}条",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")


@router.get("/student/{student_id}")
async def get_student_data(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    根据学号查询学生体测数据
    学生端、家长端可用
    """
    # 记录查询的学号
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"查询学号: {student_id}")
    
    # 查询学生
    student = db.query(StudentFitnessData).filter(
        StudentFitnessData.student_id == student_id
    ).first()
    
    if not student:
        # 查询数据库中有哪些学号（用于调试）
        all_students = db.query(StudentFitnessData.student_id).limit(5).all()
        student_ids = [s.student_id for s in all_students]
        logger.warning(f"未找到学号 {student_id}，数据库中的学号示例: {student_ids}")
        
        raise HTTPException(
            status_code=404, 
            detail=f"未找到该学生的数据。数据库中的学号示例: {student_ids[:3]}"
        )
    
    return {
        "success": True,
        "data": {
            "student_id": student.student_id,
            "grade": student.grade_name,
            "class": student.class_name,
            "gender": student.gender,
            "basic_info": {
                "height": student.height,
                "weight": student.weight,
                "weight_level": student.weight_level,
            },
            "test_results": {
                "lung_capacity": {
                    "value": student.lung_capacity,
                    "score": student.lung_capacity_score,
                    "level": student.lung_capacity_level
                },
                "run_50m": {
                    "value": student.run_50m,
                    "score": student.run_50m_score,
                    "level": student.run_50m_level
                },
                "sit_reach": {
                    "value": student.sit_reach,
                    "score": student.sit_reach_score,
                    "level": student.sit_reach_level
                },
                "sit_up": {
                    "value": student.sit_up,
                    "score": student.sit_up_score,
                    "level": student.sit_up_level
                },
                "rope_skip": {
                    "value": student.rope_skip,
                    "score": student.rope_skip_score,
                    "level": student.rope_skip_level
                },
                "standing_jump": {
                    "value": student.standing_jump,
                    "score": student.standing_jump_score,
                    "level": student.standing_jump_level
                }
            },
            "total": {
                "standard_score": student.standard_score,
                "bonus_score": student.bonus_score,
                "total_score": student.total_score,
                "level": student.total_level
            }
        }
    }


@router.get("/class/{class_name}")
async def get_class_data(
    class_name: str,
    db: Session = Depends(get_db)
):
    """
    查询班级体测数据
    Web版本：无需认证（生产环境建议添加认证）
    """
    students = db.query(StudentFitnessData).filter(
        StudentFitnessData.class_name == class_name
    ).all()
    
    if not students:
        raise HTTPException(status_code=404, detail="未找到该班级的数据")
    
    # 统计分析
    total_count = len(students)
    avg_score = sum([s.total_score for s in students if s.total_score]) / total_count if total_count > 0 else 0
    
    level_stats = {}
    for student in students:
        level = student.total_level or "未知"
        level_stats[level] = level_stats.get(level, 0) + 1
    
    return {
        "success": True,
        "data": {
            "class_name": class_name,
            "total_count": total_count,
            "avg_score": round(avg_score, 2),
            "level_stats": level_stats,
            "students": [
                {
                    "student_id": s.student_id,
                    "gender": s.gender,
                    "total_score": s.total_score,
                    "level": s.total_level
                } for s in students
            ]
        }
    }


@router.get("/exercises/recommend")
async def recommend_exercises(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    根据学生体测数据推荐训练动作
    """
    # 查询学生数据
    student = db.query(StudentFitnessData).filter(
        StudentFitnessData.student_id == student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="未找到该学生的数据")
    
    # 分析薄弱项目
    weak_items = []
    if student.run_50m_score and student.run_50m_score < 70:
        weak_items.append("50米跑")
    if student.sit_reach_score and student.sit_reach_score < 70:
        weak_items.append("坐位体前屈")
    if student.rope_skip_score and student.rope_skip_score < 70:
        weak_items.append("1分钟跳绳")
    if student.standing_jump_score and student.standing_jump_score < 70:
        weak_items.append("立定跳远")
    
    # 推荐相关训练动作
    recommended = []
    for item in weak_items:
        exercises = db.query(SportsExercise).filter(
            SportsExercise.improve_test.contains(item)
        ).limit(3).all()
        
        for ex in exercises:
            recommended.append({
                "name": ex.name,
                "description": ex.description,
                "difficulty": ex.difficulty,
                "improve_test": ex.improve_test,
                "image_url": ex.image_url
            })
    
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "weak_items": weak_items,
            "recommended_exercises": recommended
        }
    }
