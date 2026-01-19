"""
体测分析API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_token
from app.services.fitness_service import fitness_service

router = APIRouter(prefix="/fitness", tags=["体测分析"])


class FitnessAnalysisResponse(BaseModel):
    """体测分析响应"""
    has_data: bool
    analysis: Optional[dict] = None
    training_plan: Optional[dict] = None
    message: str


@router.get("/analyze/{student_id}", response_model=FitnessAnalysisResponse)
async def analyze_fitness(
    student_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    分析学生体测成绩
    """
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    # 获取最新体测数据
    test = await fitness_service.get_latest_test(student_id, db)
    
    if not test:
        return FitnessAnalysisResponse(
            has_data=False,
            message="暂无体测数据"
        )
    
    # 分析体测成绩
    analysis = fitness_service.analyze_test(test)
    
    # 生成训练方案
    training_plan = await fitness_service.generate_training_plan(analysis, db)
    
    return FitnessAnalysisResponse(
        has_data=True,
        analysis=analysis,
        training_plan=training_plan,
        message="分析完成"
    )
