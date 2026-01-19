"""
关键词识别服务（优化版）
"""
from typing import Dict, List
from app.core.cache import cache_manager, CacheKeys, CacheExpire
from app.core.performance import performance_metrics
import logging

logger = logging.getLogger(__name__)


class KeywordService:
    """关键词识别服务"""
    
    # 内部资源关键词配置
    INTERNAL_KEYWORDS = {
        # 课课练相关
        '课课练': 'course_practice',
        '课练': 'course_practice',
        
        # 运动会相关
        '全员运动会': 'sports_meeting',
        '运动会': 'sports_meeting',
        '运动会方案': 'sports_meeting',
        
        # 动作库相关
        '动作库': 'exercise_library',
        '训练动作': 'exercise_library',
        '练习动作': 'exercise_library',
        
        # 体测相关
        '体测': 'fitness_test',
        '体测成绩': 'fitness_test',
        '体测分析': 'fitness_test',
        '成绩': 'fitness_test',
        
        # 身体素质相关
        '平衡': 'balance',
        '平衡能力': 'balance',
        '力量': 'strength',
        '柔韧': 'flexibility',
        '柔韧性': 'flexibility',
        '速度': 'speed',
        '耐力': 'endurance',
        '协调': 'coordination',
        '协调性': 'coordination',
        '爆发力': 'explosive',
        
        # 具体项目
        '50米': 'fifty_meter',
        '立定跳远': 'standing_jump',
        '仰卧起坐': 'sit_ups',
        '引体向上': 'pull_ups',
        '坐位体前屈': 'sit_reach',
        '肺活量': 'vital_capacity',
    }
    
    # 排除关键词（非健康相关）
    EXCLUDED_KEYWORDS = [
        '语文', '数学', '英语', '物理', '化学',
        '历史', '地理', '政治', '生物',
        '作文', '考试', '作业', '成绩单'
    ]
    
    async def detect_keywords(self, text: str) -> Dict:
        """
        检测文本中的关键词（带缓存）
        
        Args:
            text: 输入文本
            
        Returns:
            检测结果字典
        """
        # 尝试从缓存获取
        cache_key = f"keyword:detect:{hash(text)}"
        cached = await cache_manager.get(cache_key)
        if cached:
            performance_metrics.record_cache_hit()
            return cached
        performance_metrics.record_cache_miss()
        
        result = {
            'has_internal': False,
            'internal_keywords': [],
            'categories': [],
            'is_excluded': False,
            'matched_keywords': []
        }
        
        # 检查排除关键词
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in text:
                result['is_excluded'] = True
                result['matched_keywords'].append(keyword)
                await cache_manager.set(
                    cache_key, result, CacheExpire.HOUR_1
                )
                return result
        
        # 检查内部资源关键词
        for keyword, category in self.INTERNAL_KEYWORDS.items():
            if keyword in text:
                result['has_internal'] = True
                result['internal_keywords'].append(keyword)
                if category not in result['categories']:
                    result['categories'].append(category)
                result['matched_keywords'].append(keyword)
        
        # 缓存结果
        await cache_manager.set(cache_key, result, CacheExpire.HOUR_1)
        
        return result
    
    def get_category_priority(self, categories: List[str]) -> str:
        """
        获取优先级最高的分类
        
        Args:
            categories: 分类列表
            
        Returns:
            优先级最高的分类
        """
        # 优先级顺序
        priority = [
            'fitness_test',
            'course_practice',
            'sports_meeting',
            'exercise_library',
            'balance',
            'strength',
            'flexibility',
            'speed',
            'endurance',
        ]
        
        for cat in priority:
            if cat in categories:
                return cat
        
        return categories[0] if categories else None


# 创建全局关键词服务实例
keyword_service = KeywordService()
