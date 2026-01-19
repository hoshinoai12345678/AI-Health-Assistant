"""
单元测试 - 安全检查服务
"""
import pytest
from app.services.safety_service import SafetyService


@pytest.fixture
def safety_service():
    return SafetyService()


class TestSafetyService:
    """安全检查服务测试"""
    
    def test_check_safe_content(self, safety_service):
        """测试安全内容"""
        text = "如何提高跑步速度？"
        result = safety_service.check_content(text)
        
        assert result['is_safe'] is True
        assert len(result['risk_keywords']) == 0
        assert result['risk_level'] == 'safe'
    
    def test_check_political_content(self, safety_service):
        """测试政治敏感内容"""
        text = "政治相关的敏感话题"
        result = safety_service.check_content(text)
        
        assert result['is_safe'] is False
        assert result['risk_level'] == 'high'
    
    def test_check_violence_content(self, safety_service):
        """测试暴力内容"""
        text = "如何打架更厉害"
        result = safety_service.check_content(text)
        
        assert result['is_safe'] is False
        assert len(result['risk_keywords']) > 0
    
    def test_check_illegal_content(self, safety_service):
        """测试违法内容"""
        text = "怎么买毒品"
        result = safety_service.check_content(text)
        
        assert result['is_safe'] is False
        assert result['risk_level'] == 'high'
    
    def test_filter_response(self, safety_service):
        """测试响应过滤"""
        response = "这是一个包含敏感词的回复"
        filtered = safety_service.filter_response(response)
        
        assert filtered is not None
        assert isinstance(filtered, str)
