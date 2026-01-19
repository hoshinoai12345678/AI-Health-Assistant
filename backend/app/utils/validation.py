"""
输入验证工具
"""
from typing import Optional
import re
from fastapi import HTTPException


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_message(message: str) -> str:
        """验证消息内容"""
        if not message or not message.strip():
            raise HTTPException(
                status_code=400,
                detail="消息内容不能为空"
            )
        
        # 长度限制
        if len(message) > 2000:
            raise HTTPException(
                status_code=400,
                detail="消息内容过长（最多2000字符）"
            )
        
        # 移除多余空白
        message = message.strip()
        
        return message
    
    @staticmethod
    def validate_grade(grade: int) -> int:
        """验证年级"""
        if grade < 1 or grade > 12:
            raise HTTPException(
                status_code=400,
                detail="年级必须在1-12之间"
            )
        return grade
    
    @staticmethod
    def validate_gender(gender: str) -> str:
        """验证性别"""
        if gender not in ["male", "female"]:
            raise HTTPException(
                status_code=400,
                detail="性别必须是male或female"
            )
        return gender
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """验证手机号"""
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            raise HTTPException(
                status_code=400,
                detail="手机号格式不正确"
            )
        return phone
    
    @staticmethod
    def validate_email(email: str) -> str:
        """验证邮箱"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise HTTPException(
                status_code=400,
                detail="邮箱格式不正确"
            )
        return email
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """清理HTML标签"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除脚本
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        return text


# 全局验证器实例
input_validator = InputValidator()
