"""
单元测试 - 关键词服务
"""
import pytest
from app.services.keyword_service import KeywordService


@pytest.fixture
def keyword_service():
    return KeywordService()


class TestKeywordService:
    """关键词服务测试"""
    
    @pytest.mark.asyncio
    async def test_detect_fitness_keywords(self, keyword_service):
        """测试体测关键词检测"""
        text = "我的体测成绩怎么样？"
        result = await keyword_service.detect_keywords(text)
        
        assert result['has_internal'] is True
        assert 'fitness_test' in result['categories']
        assert len(result['internal_keywords']) > 0
    
    @pytest.mark.asyncio
    async def test_detect_course_keywords(self, keyword_service):
        """测试课课练关键词检测"""
        text = "有没有课课练的资料？"
        result = await keyword_service.detect_keywords(text)
        
        assert result['has_internal'] is True
        assert 'course_practice' in result['categories']
    
    @pytest.mark.asyncio
    async def test_detect_excluded_keywords(self, keyword_service):
        """测试排除关键词检测"""
        text = "数学作业怎么做？"
        result = await keyword_service.detect_keywords(text)
        
        assert result['is_excluded'] is True
        assert result['has_internal'] is False
    
    @pytest.mark.asyncio
    async def test_detect_no_keywords(self, keyword_service):
        """测试无关键词情况"""
        text = "今天天气真好"
        result = await keyword_service.detect_keywords(text)
        
        assert result['has_internal'] is False
        assert result['is_excluded'] is False
        assert len(result['categories']) == 0
    
    def test_category_priority(self, keyword_service):
        """测试分类优先级"""
        categories = ['strength', 'fitness_test', 'balance']
        priority = keyword_service.get_category_priority(categories)
        
        assert priority == 'fitness_test'
