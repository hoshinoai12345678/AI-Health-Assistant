"""
性能测试 - Locust配置
"""
from locust import HttpUser, task, between
import random


class APIUser(HttpUser):
    """API用户模拟"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """初始化：登录获取token"""
        response = self.client.post("/api/auth/login", json={
            "wechat_code": f"test_code_{random.randint(1000, 9999)}"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = "test_token"
    
    @task(5)
    def send_message(self):
        """发送对话消息（高频）"""
        messages = [
            "如何提高跑步速度？",
            "体测成绩怎么分析？",
            "有什么课课练资料？",
            "如何提高立定跳远成绩？",
            "怎么训练耐力？"
        ]
        
        self.client.post(
            "/api/chat/send",
            json={
                "message": random.choice(messages),
                "conversation_id": None
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def get_conversations(self):
        """获取对话列表（中频）"""
        self.client.get(
            "/api/conversation/list",
            params={"skip": 0, "limit": 20},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def fitness_analysis(self):
        """体测分析（低频）"""
        self.client.post(
            "/api/fitness/analyze",
            json={
                "gender": random.choice(["male", "female"]),
                "grade": random.randint(7, 9),
                "test_data": {
                    "height": random.randint(160, 180),
                    "weight": random.randint(50, 70),
                    "fifty_meter": round(random.uniform(7.0, 9.0), 1),
                    "standing_jump": random.randint(180, 240)
                }
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def get_conversation_detail(self):
        """获取对话详情（低频）"""
        conversation_id = random.randint(1, 100)
        self.client.get(
            f"/api/conversation/{conversation_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
