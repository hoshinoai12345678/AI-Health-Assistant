"""
对话历史API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()


class ConversationItem(BaseModel):
    """对话项"""
    id: int
    title: str
    lastMessage: str
    updated_at: str


@router.get("/list")
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话列表
    """
    user_id = current_user.get("user_id")
    
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
        
        conversation_list.append({
            "id": conv.id,
            "title": conv.title or "未命名对话",
            "lastMessage": last_message.content[:50] if last_message else "",
            "updated_at": conv.updated_at.isoformat()
        })
    
    return {"conversations": conversation_list}


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取对话详情和消息
    """
    user_id = current_user.get("user_id")
    
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
    
    # 查询消息列表
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = msg_result.scalars().all()
    
    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        },
        "messages": [
        {
            'id': msg.id,
            'role': msg.role.value,
            'content': msg.content,
            'source': msg.source.value if msg.source else None,
            'created_at': msg.created_at.isoformat()
        }
        for msg in messages
    ]
    }


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除对话
    """
    user_id = current_user.get("user_id")
    
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除所有对话
    """
    user_id = current_user.get("user_id")
    
    # 删除用户的所有对话
    await db.execute(
        delete(Conversation).where(Conversation.user_id == user_id)
    )
    await db.commit()
    
    return {"message": "已删除所有对话"}
