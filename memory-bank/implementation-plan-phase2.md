# AI大健康助手 - 实施计划（第二阶段）

## 📅 阶段2：核心功能开发（第3-6周）

---

### 步骤 2.1：AI对话基础功能

**目标**：实现基础的AI对话功能

**任务清单**：
1. 集成通义千问API
2. 实现对话接口
3. 实现角色识别
4. 创建聊天界面

**后端实现**：

**backend/app/services/ai_service.py**
```python
from dashscope import Generation
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
    
    async def chat(self, messages: list, user_role: str):
        """AI对话"""
        # 根据角色设置系统提示词
        system_prompt = self._get_system_prompt(user_role)
        
        full_messages = [
            {'role': 'system', 'content': system_prompt}
        ] + messages
        
        response = Generation.call(
            model='qwen-turbo',
            messages=full_messages,
            result_format='message'
        )
        
        return response.output.choices[0].message.content
    
    def _get_system_prompt(self, role: str) -> str:
        prompts = {
            'teacher': '你是一个专业的体育教学AI助手...',
            'student': '你是一个友好的健康指导AI助手...',
            'parent': '你是一个专业的家庭健康顾问...',
        }
        return prompts.get(role, prompts['student'])
```

**backend/app/api/chat.py**
```python
from fastapi import APIRouter, Depends
from app.services.ai_service import AIService
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["对话"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: int = None

@router.post("/send")
async def send_message(request: ChatRequest):
    """发送消息"""
    ai_service = AIService()
    
    # 获取历史对话
    history = []  # 从数据库获取
    
    # 调用AI
    response = await ai_service.chat(
        messages=history + [{'role': 'user', 'content': request.message}],
        user_role='student'
    )
    
    # 保存对话记录
    # ...
    
    return {
        'message': response,
        'source': 'ai'
    }
```

**前端实现**：

**miniprogram/pages/chat/chat.wxml**
```xml
<view class="chat-container">
  <scroll-view class="message-list" scroll-y scroll-into-view="{{scrollToView}}">
    <view wx:for="{{messages}}" wx:key="id" class="message-item {{item.role}}">
      <view class="message-content">{{item.content}}</view>
      <view class="message-time">{{item.time}}</view>
    </view>
  </scroll-view>
  
  <view class="input-bar">
    <input class="message-input" 
           value="{{inputText}}" 
           bindinput="onInput"
           placeholder="请输入您的问题..."/>
    <button class="send-btn" bindtap="sendMessage">发送</button>
  </view>
</view>
```

**验证标准**：
- [ ] 用户可以发送消息
- [ ] AI可以正确回复
- [ ] 对话历史正确显示
- [ ] 界面流畅无卡顿

**预计时间**：6小时

---

### 步骤 2.2：关键词识别与资源检索

**目标**：实现内部资源库优先检索逻辑

**任务清单**：
1. 创建关键词配置
2. 实现关键词识别
3. 实现资源检索服务
4. 集成到对话流程

**backend/app/services/keyword_service.py**
```python
class KeywordService:
    # 关键词配置
    KEYWORDS = {
        'internal': {
            '课课练': 'course_practice',
            '全员运动会': 'sports_meeting',
            '动作库': 'exercise_library',
            '体测': 'fitness_test',
            '平衡': 'balance',
            '力量': 'strength',
            '柔韧': 'flexibility',
            '速度': 'speed',
            '耐力': 'endurance',
        },
        'excluded': ['语文', '数学', '英语', '物理', '化学']
    }
    
    def detect_keywords(self, text: str) -> dict:
        """检测关键词"""
        result = {
            'has_internal': False,
            'internal_keywords': [],
            'is_excluded': False,
            'category': None
        }
        
        # 检查排除关键词
        for keyword in self.KEYWORDS['excluded']:
            if keyword in text:
                result['is_excluded'] = True
                return result
        
        # 检查内部资源关键词
        for keyword, category in self.KEYWORDS['internal'].items():
            if keyword in text:
                result['has_internal'] = True
                result['internal_keywords'].append(keyword)
                result['category'] = category
        
        return result
```

**backend/app/services/resource_service.py**
```python
from sqlalchemy import select
from app.models.resource import InternalResource

class ResourceService:
    async def search_internal(self, keywords: list, category: str, db):
        """搜索内部资源"""
        query = select(InternalResource).where(
            InternalResource.category == category
        )
        
        # 关键词匹配
        for keyword in keywords:
            query = query.where(
                InternalResource.keywords.contains([keyword])
            )
        
        result = await db.execute(query)
        resources = result.scalars().all()
        
        return resources
    
    async def search_internet(self, query: str):
        """搜索互联网资源（备用）"""
        # 调用搜索API或LLM
        return "互联网搜索结果..."
```

**验证标准**：
- [ ] 关键词可以正确识别
- [ ] 内部资源可以正确检索
- [ ] 无匹配时使用互联网资源
- [ ] 排除关键词正确过滤

**预计时间**：8小时

---

### 步骤 2.3：内部资源库数据导入

**目标**：将课课练、动作库等资源导入数据库

**任务清单**：
1. 准备资源数据
2. 创建数据导入脚本
3. 导入课课练教材
4. 导入动作库
5. 导入运动会方案

**backend/scripts/import_resources.py**
```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.resource import InternalResource

async def import_course_practice():
    """导入课课练教材"""
    async with AsyncSessionLocal() as db:
        resources = [
            {
                'type': 'course_practice',
                'category': 'balance',
                'title': '平衡能力训练 - 单脚站立',
                'content': '练习方法：...',
                'keywords': ['平衡', '课课练', '单脚'],
                'file_url': '/resources/balance_1.jpg'
            },
            # 更多资源...
        ]
        
        for res in resources:
            resource = InternalResource(**res)
            db.add(resource)
        
        await db.commit()
        print(f"导入了 {len(resources)} 条课课练资源")

async def import_exercise_library():
    """导入动作库"""
    async with AsyncSessionLocal() as db:
        exercises = [
            {
                'type': 'exercise',
                'category': 'flexibility',
                'title': '单臂体侧屈',
                'content': '''
                练习方法：盘腿坐姿，左臂上举、掌心向内...
                每组时长：30秒
                组数：每侧2-3组
                组间歇：30秒
                ''',
                'keywords': ['柔韧', '体侧屈', '训练'],
                'file_url': '/videos/flexibility_1.mp4'
            },
            # 更多动作...
        ]
        
        for ex in exercises:
            exercise = InternalResource(**ex)
            db.add(exercise)
        
        await db.commit()
        print(f"导入了 {len(exercises)} 条动作库资源")

if __name__ == '__main__':
    asyncio.run(import_course_practice())
    asyncio.run(import_exercise_library())
```

**验证标准**：
- [ ] 资源成功导入数据库
- [ ] 可以通过关键词检索到资源
- [ ] 资源内容完整
- [ ] 文件路径正确

**预计时间**：12小时（包括数据整理）

---

### 步骤 2.4：体测数据分析功能

**目标**：根据体测成绩生成个性化训练方案

**任务清单**：
1. 实现体测数据分析逻辑
2. 实现薄弱项识别
3. 实现训练方案生成
4. 创建前端展示页面

**backend/app/services/fitness_service.py**
```python
class FitnessService:
    # 国家标准（示例）
    STANDARDS = {
        'grade_4': {  # 四年级
            'fifty_meter_run': {'excellent': 9.0, 'good': 10.0, 'pass': 11.5},
            'standing_long_jump': {'excellent': 160, 'good': 140, 'pass': 120},
            # 更多项目...
        }
    }
    
    async def analyze_fitness_test(self, student_id: int, db):
        """分析体测成绩"""
        # 获取最新体测数据
        test = await self._get_latest_test(student_id, db)
        
        # 分析各项成绩
        analysis = {
            'weakest': None,
            'second_weakest': None,
            'suggestions': []
        }
        
        scores = {
            'fifty_meter_run': self._calculate_score(test.fifty_meter_run, 'fifty_meter_run'),
            'standing_long_jump': self._calculate_score(test.standing_long_jump, 'standing_long_jump'),
            # 更多项目...
        }
        
        # 找出最弱和次弱项
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        analysis['weakest'] = sorted_scores[0][0]
        analysis['second_weakest'] = sorted_scores[1][0]
        
        return analysis
    
    async def generate_training_plan(self, analysis: dict, db):
        """生成训练方案"""
        # 根据薄弱项查找对应素质
        quality_map = {
            'fifty_meter_run': ['speed', 'leg_strength'],
            'standing_long_jump': ['leg_strength', 'explosive'],
            # 更多映射...
        }
        
        qualities = quality_map.get(analysis['weakest'], [])
        
        # 从动作库查找训练动作
        exercises = await self._find_exercises(qualities, db)
        
        # 生成方案
        plan = {
            'weakest_quality': qualities[0],
            'exercises': exercises[:3],  # 3个针对最弱素质
            'secondary_exercises': exercises[3:4]  # 1个针对次弱素质
        }
        
        return plan
```

**验证标准**：
- [ ] 可以正确分析体测成绩
- [ ] 可以识别薄弱项
- [ ] 可以生成训练方案
- [ ] 方案内容合理

**预计时间**：10小时

---

### 步骤 2.5：历史对话记录功能

**目标**：实现对话历史的保存和查看

**任务清单**：
1. 实现对话保存逻辑
2. 实现历史记录查询
3. 实现记录删除功能
4. 创建历史记录页面

**backend/app/api/conversation.py**
```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/conversation", tags=["对话历史"])

@router.get("/list")
async def get_conversations(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations

@router.get("/{conversation_id}/messages")
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """获取对话消息"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """删除对话"""
    await db.execute(
        delete(Conversation).where(Conversation.id == conversation_id)
    )
    await db.commit()
    return {"message": "删除成功"}
```

**miniprogram/pages/history/history.ts**
```typescript
Page({
  data: {
    conversations: []
  },

  onLoad() {
    this.loadHistory();
  },

  async loadHistory() {
    const res = await request({
      url: '/conversation/list',
      method: 'GET'
    });
    
    this.setData({
      conversations: res
    });
  },

  async deleteConversation(e: any) {
    const id = e.currentTarget.dataset.id;
    
    await wx.showModal({
      title: '确认删除',
      content: '确定要删除这条对话记录吗？'
    });
    
    await request({
      url: `/conversation/${id}`,
      method: 'DELETE'
    });
    
    this.loadHistory();
  }
});
```

**验证标准**：
- [ ] 对话可以正确保存
- [ ] 历史记录可以查看
- [ ] 可以删除单条记录
- [ ] 可以删除全部记录

**预计时间**：6小时

---

### 步骤 2.6：风险提示与内容过滤

**目标**：实现健康风险提示和非健康内容过滤

**任务清单**：
1. 创建风险关键词库
2. 实现风险检测
3. 实现内容过滤
4. 添加提示信息

**backend/app/services/safety_service.py**
```python
class SafetyService:
    # 风险关键词
    RISK_KEYWORDS = {
        'medical': ['发烧', '吃药', '生病', '疼痛', '受伤'],
        'mental': ['自杀', '抑郁', '想死', '活不下去'],
    }
    
    # 排除关键词
    EXCLUDED_KEYWORDS = ['语文', '数学', '英语', '物理', '化学', '历史', '地理']
    
    def check_risk(self, text: str) -> dict:
        """检查风险"""
        result = {
            'has_risk': False,
            'risk_type': None,
            'warning': None
        }
        
        # 检查医疗风险
        for keyword in self.RISK_KEYWORDS['medical']:
            if keyword in text:
                result['has_risk'] = True
                result['risk_type'] = 'medical'
                result['warning'] = '建议及时就医，以下仅供参考：'
                return result
        
        # 检查心理风险
        for keyword in self.RISK_KEYWORDS['mental']:
            if keyword in text:
                result['has_risk'] = True
                result['risk_type'] = 'mental'
                result['warning'] = '请立即联系专业心理医生或拨打心理援助热线：400-xxx-xxxx'
                return result
        
        return result
    
    def check_excluded(self, text: str) -> bool:
        """检查是否为排除内容"""
        for keyword in self.EXCLUDED_KEYWORDS:
            if keyword in text:
                return True
        return False
```

**集成到对话流程**：
```python
@router.post("/send")
async def send_message(request: ChatRequest):
    safety_service = SafetyService()
    
    # 检查排除内容
    if safety_service.check_excluded(request.message):
        return {
            'message': '我们是大健康智能体，您可以问我健康、体育、营养等相关内容，换个问题试试吧。',
            'source': 'system'
        }
    
    # 检查风险
    risk = safety_service.check_risk(request.message)
    
    # 调用AI
    response = await ai_service.chat(...)
    
    # 添加风险提示
    if risk['has_risk']:
        response = risk['warning'] + '\n\n' + response
    
    return {'message': response, 'source': 'ai'}
```

**验证标准**：
- [ ] 风险内容可以正确识别
- [ ] 提示信息正确显示
- [ ] 非健康内容被过滤
- [ ] 不影响正常对话

**预计时间**：4小时

---

## 📊 阶段2总结

### 完成的工作
- ✅ AI对话基础功能
- ✅ 关键词识别与资源检索
- ✅ 内部资源库数据导入
- ✅ 体测数据分析功能
- ✅ 历史对话记录功能
- ✅ 风险提示与内容过滤

### 验收标准
- [ ] 用户可以与AI正常对话
- [ ] 内部资源可以正确检索
- [ ] 体测分析功能正常
- [ ] 历史记录可以查看和管理
- [ ] 风险提示正常工作
- [ ] 非健康内容被过滤

### 下一步
继续 [实施计划第三阶段](memory-bank/implementation-plan-phase3.md)

---

**文档状态**：✅ 已完成  
**最后更新**：2026-01-19  
**预计完成时间**：4周
