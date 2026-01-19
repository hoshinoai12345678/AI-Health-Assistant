"""
单元测试 - 体测分析服务
"""
import pytest
from app.services.fitness_service import FitnessService


@pytest.fixture
def fitness_service():
    return FitnessService()


class TestFitnessService:
    """体测分析服务测试"""
    
    def test_analyze_male_student(self, fitness_service):
        """测试男生体测分析"""
        test_data = {
            "gender": "male",
            "grade": 8,
            "height": 170,
            "weight": 60,
            "fifty_meter": 7.5,
            "standing_jump": 220,
            "sit_ups": 45,
            "sit_reach": 15.0,
            "vital_capacity": 3500,
            "endurance_run": 210
        }
        
        result = fitness_service.analyze_fitness_test(test_data)
        
        assert result is not None
        assert 'total_score' in result
        assert 'level' in result
        assert 'item_scores' in result
        assert result['total_score'] >= 0
        assert result['total_score'] <= 120
    
    def test_analyze_female_student(self, fitness_service):
        """测试女生体测分析"""
        test_data = {
            "gender": "female",
            "grade": 8,
            "height": 160,
            "weight": 50,
            "fifty_meter": 8.5,
            "standing_jump": 180,
            "sit_ups": 40,
            "sit_reach": 18.0,
            "vital_capacity": 2800,
            "endurance_run": 240
        }
        
        result = fitness_service.analyze_fitness_test(test_data)
        
        assert result is not None
        assert result['total_score'] >= 0
    
    def test_bmi_calculation(self, fitness_service):
        """测试BMI计算"""
        bmi = fitness_service._calculate_bmi(170, 60)
        
        assert bmi > 0
        assert 15 < bmi < 30
    
    def test_generate_suggestions(self, fitness_service):
        """测试建议生成"""
        analysis = {
            "total_score": 75,
            "level": "良好",
            "weak_items": ["fifty_meter", "standing_jump"]
        }
        
        suggestions = fitness_service.generate_suggestions(analysis)
        
        assert suggestions is not None
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
