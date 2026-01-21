"""
认证相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import httpx

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.models.user import User, UserRole

router = APIRouter()


class WxLoginRequest(BaseModel):
    """微信登录请求"""
    code: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = UserRole.STUDENT


class LoginRequest(BaseModel):
    """普通登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/wx-login", response_model=LoginResponse)
async def wx_login(
    request: WxLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    微信小程序登录
    
    流程：
    1. 通过code换取openid
    2. 查询或创建用户
    3. 生成JWT token
    4. 返回token和用户信息
    """
    # 1. 调用微信API换取openid
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": settings.WECHAT_APP_ID,
                    "secret": settings.WECHAT_APP_SECRET,
                    "js_code": request.code,
                    "grant_type": "authorization_code"
                },
                timeout=10.0
            )
            wx_data = response.json()
            
            if "openid" not in wx_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信登录失败: {wx_data.get('errmsg', '未知错误')}"
                )
            
            openid = wx_data["openid"]
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="微信服务请求超时"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"微信登录异常: {str(e)}"
            )
    
    # 2. 查询或创建用户
    result = await db.execute(
        select(User).where(User.openid == openid)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # 创建新用户
        user = User(
            openid=openid,
            role=request.role,
            nickname=request.nickname,
            avatar_url=request.avatar_url
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # 更新用户信息
        if request.nickname:
            user.nickname = request.nickname
        if request.avatar_url:
            user.avatar_url = request.avatar_url
        await db.flush()
    
    await db.commit()
    
    # 3. 生成JWT token
    token = create_access_token({
        "user_id": user.id,
        "role": user.role.value
    })
    
    # 4. 返回响应
    return LoginResponse(
        access_token=token,
        user={
            "id": user.id,
            "role": user.role.value,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    普通用户名密码登录（用于Web版测试）
    """
    # 简化版登录，实际项目中应该验证密码
    result = await db.execute(
        select(User).where(User.nickname == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # 创建测试用户
        user = User(
            openid=f"test_{request.username}",
            role=UserRole.STUDENT,
            nickname=request.username,
            avatar_url=None
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        await db.commit()
    
    # 生成JWT token
    token = create_access_token({
        "user_id": user.id,
        "role": user.role.value
    })
    
    return LoginResponse(
        access_token=token,
        user={
            "id": user.id,
            "role": user.role.value,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url
        }
    )


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    user_id = current_user.get("user_id")
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "id": user.id,
        "role": user.role.value,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url
    }
