"""
安全检查服务
"""
from typing import Dict, Optional


class SafetyService:
    """安全检查服务"""
    
    # 医疗风险关键词
    MEDICAL_KEYWORDS = [
        '发烧', '发热', '高烧', '低烧',
        '吃药', '药物', '用药',
        '生病', '疾病', '病了',
        '疼痛', '痛', '不舒服',
        '受伤', '伤口', '骨折', '扭伤',
        '头晕', '恶心', '呕吐',
        '咳嗽', '感冒', '流感'
    ]
    
    # 心理风险关键词
    MENTAL_KEYWORDS = [
        '自杀', '想死', '不想活',
        '抑郁', '抑郁症',
        '活不下去', '没有希望',
        '轻生', '结束生命'
    ]
    
    # 排除关键词（非健康相关）
    EXCLUDED_KEYWORDS = [
        '语文', '数学', '英语', '物理', '化学',
        '历史', '地理', '政治', '生物',
        '作文', '考试', '作业', '成绩单',
        '学习', '功课', '补习'
    ]
    
    def check_risk(self, text: str) -> Dict:
        """
        检查健康风险
        
        Args:
            text: 输入文本
            
        Returns:
            风险检查结果
        """
        result = {
            'has_risk': False,
            'risk_type': None,
            'warning': None,
            'matched_keywords': []
        }
        
        # 检查医疗风险
        for keyword in self.MEDICAL_KEYWORDS:
            if keyword in text:
                result['has_risk'] = True
                result['risk_type'] = 'medical'
                result['warning'] = '⚠️ 健康提示：建议及时就医，以下内容仅供参考，不能替代专业医疗诊断。'
                result['matched_keywords'].append(keyword)
                return result
        
        # 检查心理风险
        for keyword in self.MENTAL_KEYWORDS:
            if keyword in text:
                result['has_risk'] = True
                result['risk_type'] = 'mental'
                result['warning'] = '''⚠️ 紧急提示：请立即联系专业心理医生或拨打心理援助热线。

全国心理援助热线：400-161-9995
北京心理危机干预热线：010-82951332

您的生命很重要，请寻求专业帮助。'''
                result['matched_keywords'].append(keyword)
                return result
        
        return result
    
    def check_excluded(self, text: str) -> Dict:
        """
        检查是否为排除内容
        
        Args:
            text: 输入文本
            
        Returns:
            检查结果
        """
        result = {
            'is_excluded': False,
            'matched_keywords': [],
            'message': None
        }
        
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in text:
                result['is_excluded'] = True
                result['matched_keywords'].append(keyword)
                result['message'] = '我们是大健康智能体，专注于健康、体育、营养、心理等相关内容。您可以问我运动训练、健康饮食、心理调节等方面的问题，换个问题试试吧。'
                return result
        
        return result
    
    def sanitize_content(self, content: str) -> str:
        """
        清理内容中的敏感信息
        
        Args:
            content: 原始内容
            
        Returns:
            清理后的内容
        """
        # 这里可以添加更多的内容清理逻辑
        # 例如：移除个人信息、敏感词汇等
        return content


# 创建全局安全服务实例
safety_service = SafetyService()
