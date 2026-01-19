"""
对话历史API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.security import verify_token
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(prefix="/conversation", tags=["对话历史"])


class ConversationItem(BaseModel):
    """对话项"""
    id: int
    title: str
    last_message: str
    created_at: str
    updated_at: str


@router.get("/list", response_model=List[ConversationItem])
async def get_conversations(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话列表
    """
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    user_id = payload.get("user_id")
    
    # 查询对话列表
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    
    # 获取每个对话的最后一条消息
    conversation_list = []
    for conv in conversations:
        # 获取最后一条消息
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = msg_result.scalar_one_or_none()
        
        conversation_list.append(
            ConversationItem(
                id=conv.id,
                title=conv.title or "未命名对话",
                last_message=last_message.content[:50] if last_message else "",
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat()
            )
        )
    
    return conversation_list


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话消息
    """
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    # 查询消息列表
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


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除对话
    """
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    user_id = payload.get("user_id")
    
    # 验证对话所有权
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权限"
        )
    
    # 删除对话（级联删除消息）
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "删除成功"}


@router.delete("/all")
async def delete_all_conversations(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除所有对话
    """
    # 验证token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )
    
    user_id = payload.get("user_id")
    
    # 删除用户的所有对话
    await db.execute(
        delete(Conversation).where(Conversation.user_id == user_id)
    )
    await db.commit()
    
    return {"message": "已删除所有对话"}
