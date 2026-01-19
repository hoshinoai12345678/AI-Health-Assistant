"""
AI服务 - 集成通义千问
"""
from typing import List, Dict, Optional
import httpx
from app.core.config import settings


class AIService:
    """AI对话服务"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_role: str = "student"
    ) -> str:
        """
        AI对话
        
        Args:
            messages: 对话历史
            user_role: 用户角色
            
        Returns:
            AI回复内容
        """
        # 根据角色设置系统提示词
        system_prompt = self._get_system_prompt(user_role)
        
        # 构建完整消息
        full_messages = [
            {'role': 'system', 'content': system_prompt}
        ] + messages
        
        # 调用通义千问API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'qwen-turbo',
                        'input': {
                            'messages': full_messages
                        },
                        'parameters': {
                            'result_format': 'message'
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['output']['choices'][0]['message']['content']
                else:
                    return "抱歉，AI服务暂时不可用，请稍后再试。"
        
        except Exception as e:
            print(f"AI服务调用失败: {e}")
            return "抱歉，AI服务出现异常，请稍后再试。"
    
    def _get_system_prompt(self, role: str) -> str:
        """
        获取系统提示词
        
        Args:
            role: 用户角色
            
        Returns:
            系统提示词
        """
        prompts = {
            'teacher': '''你是一个专业的体育教学AI助手，为教师提供教学支持。
你的职责包括：
1. 提供体育教学方案和建议
2. 分析学生体测数据
3. 推荐训练动作和方法
4. 设计体育活动方案

回答时要：
- 使用专业术语
- 结合校园场景
- 提供可操作的建议
- 数据化表达''',
            
            'student': '''你是一个友好的健康指导AI助手，为学生提供健康建议。
你的职责包括：
1. 解答运动健康问题
2. 提供训练指导
3. 给出营养建议
4. 心理健康支持

回答时要：
- 使用简单易懂的语言
- 鼓励和激励学生
- 提供实用的方法
- 注意安全提示''',
            
            'parent': '''你是一个专业的家庭健康顾问，为家长提供育儿建议。
你的职责包括：
1. 解答儿童健康问题
2. 提供家庭锻炼指导
3. 给出营养建议
4. 协助学校教育

回答时要：
- 通俗易懂
- 专业且实用
- 关注儿童安全
- 提供科学依据''',
            
            'admin': '''你是一个数据分析专家，为教育主管部门提供决策支持。
你的职责包括：
1. 分析学校健康数据
2. 提供政策建议
3. 识别问题和趋势
4. 支持资源配置

回答时要：
- 数据化表达
- 专业分析
- 提供决策依据
- 关注整体趋势'''
        }
        
        return prompts.get(role, prompts['student'])


# 创建全局AI服务实例
ai_service = AIService()
