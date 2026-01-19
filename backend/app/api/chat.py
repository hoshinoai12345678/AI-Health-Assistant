"""
对话API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole, MessageSource
from app.services.ai_service import ai_service
from app.services.keyword_service import keyword_service
from app.services.resource_service import resource_service
from app.services.safety_service import safety_service
from app.services.fitness_service import fitness_service

router = APIRouter(prefix="/chat", tags=["对话"])


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """对话响应"""
    message: str
    source: str
    conversation_id: int
    has_risk: bool = False
    risk_warning: Optional[str] = None


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    发送消息
    
    流程：
    1. 验证用户身份
    2. 安全检查（风险检测、内容过滤）
    3. 关键词识别
    4. 资源检索或AI生成
    5. 保存对话记录
    6. 返回响应
    """
    # 1. 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    user_id = payload.get("user_id")
    user_role = payload.get("role", "student")
    
    # 2. 安全检查 - 排除内容
    excluded_check = safety_service.check_excluded(request.message)
    if excluded_check['is_excluded']:
        return ChatResponse(
            message=excluded_check['message'],
            source='system',
            conversation_id=request.conversation_id or 0,
            has_risk=False
        )
    
    # 3. 安全检查 - 风险检测
    risk_check = safety_service.check_risk(request.message)
    
    # 4. 关键词识别
    keyword_result = keyword_service.detect_keywords(request.message)
    
    response_message = ""
    message_source = "ai"
    
    # 5. 处理逻辑
    if keyword_result['has_internal']:
        # 有内部关键词，检索内部资源
        category = keyword_service.get_category_priority(
            keyword_result['categories']
        )
        
        # 特殊处理：体测分析
        if 'fitness_test' in keyword_result['categories']:
            # 这里应该获取学生ID，简化处理
            response_message = "根据您的体测成绩分析，建议加强以下训练...\n\n"
            response_message += "（完整的体测分析功能需要绑定学生信息）"
            message_source = "internal"
        else:
            # 检索内部资源
            resources = await resource_service.search_internal(
                keywords=keyword_result['internal_keywords'],
                category=category,
                db=db,
                limit=5
            )
            
            if resources:
                response_message = resource_service.format_resource_response(
                    resources,
                    source="internal"
                )
                message_source = "internal"
            else:
                # 内部资源未找到，使用AI生成
                response_message = await ai_service.chat(
                    messages=[{'role': 'user', 'content': request.message}],
                    user_role=user_role
                )
                response_message += "\n\n（内容来自于互联网，请斟酌使用）"
                message_source = "internet"
    else:
        # 没有内部关键词，直接使用AI
        response_message = await ai_service.chat(
            messages=[{'role': 'user', 'content': request.message}],
            user_role=user_role
        )
        response_message += "\n\n（内容来自于互联网，请斟酌使用）"
        message_source = "internet"
    
    # 6. 添加风险提示
    risk_warning = None
    if risk_check['has_risk']:
        response_message = risk_check['warning'] + "\n\n" + response_message
        risk_warning = risk_check['warning']
    
    # 7. 保存对话记录
    conversation_id = request.conversation_id
    
    if not conversation_id:
        # 创建新对话
        conversation = Conversation(
            user_id=user_id,
            title=request.message[:50]  # 使用前50个字符作为标题
        )
        db.add(conversation)
        await db.flush()
        conversation_id = conversation.id
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=request.message
    )
    db.add(user_message)
    
    # 保存AI回复
    ai_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=response_message,
        source=MessageSource.INTERNAL if message_source == "internal" else MessageSource.INTERNET
    )
    db.add(ai_message)
    
    await db.commit()
    
    # 8. 返回响应
    return ChatResponse(
        message=response_message,
        source=message_source,
        conversation_id=conversation_id,
        has_risk=risk_check['has_risk'],
        risk_warning=risk_warning
    )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """获取对话历史"""
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    # 获取消息列表
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return [
        {
            'id': msg.id,
            'role': msg.role.value,
            'content': msg.content,
            'source': msg.source.value if msg.source else None,
            'created_at': msg.created_at.isoformat()
        }
        for msg in messages
    ]
