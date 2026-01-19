"""
集成测试 - 对话API
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """模拟认证头"""
    return {
        "Authorization": "Bearer test_token"
    }


class TestChatAPI:
    """对话API集成测试"""
    
    @pytest.mark.asyncio
    async def test_send_message(self, client, auth_headers):
        """测试发送消息"""
        payload = {
            "message": "如何提高跑步速度？",
            "conversation_id": None
        }
        
        response = await client.post(
            "/api/chat/send",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
    
    @pytest.mark.asyncio
    async def test_send_unsafe_message(self, client, auth_headers):
        """测试发送不安全消息"""
        payload = {
            "message": "政治敏感内容",
            "conversation_id": None
        }
        
        response = await client.post(
            "/api/chat/send",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_fitness_analysis(self, client, auth_headers):
        """测试体测分析"""
        payload = {
            "gender": "male",
            "grade": 8,
            "test_data": {
                "height": 170,
                "weight": 60,
                "fifty_meter": 7.5,
                "standing_jump": 220
            }
        }
        
        response = await client.post(
            "/api/fitness/analyze",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "suggestions" in data
