# AI模型API申请配置指南

---

## 📋 目录

1. [阿里云通义千问API申请](#1-阿里云通义千问api申请)
2. [配置API密钥](#2-配置api密钥)
3. [测试API连接](#3-测试api连接)
4. [其他AI模型选择](#4-其他ai模型选择)
5. [常见问题](#5-常见问题)

---

## 1. 阿里云通义千问API申请

### 1.1 注册阿里云账号

1. **访问阿里云官网**
   - 网址：https://www.aliyun.com/
   - 点击右上角 "免费注册"

2. **填写注册信息**
   - 手机号或邮箱
   - 设置密码
   - 验证码
   - 点击 "注册"

3. **实名认证**
   - 登录后，点击右上角头像
   - 选择 "实名认证"
   - 个人认证：身份证信息
   - 企业认证：营业执照信息
   - 提交审核（通常几分钟内完成）

### 1.2 开通通义千问服务

1. **访问通义千问控制台**
   - 网址：https://dashscope.aliyun.com/
   - 或搜索 "阿里云 通义千问"

2. **开通服务**
   - 点击 "立即开通" 或 "免费试用"
   - 阅读并同意服务协议
   - 点击 "确认开通"

3. **选择套餐**
   - **免费额度**：
     - 新用户赠送100万tokens
     - 有效期3个月
     - 适合开发测试
   
   - **按量付费**：
     - qwen-turbo: ¥0.008/千tokens
     - qwen-plus: ¥0.02/千tokens
     - qwen-max: ¥0.12/千tokens
   
   - **资源包**：
     - 预付费，更优惠
     - 100万tokens: ¥15
     - 1000万tokens: ¥140

4. **推荐选择**
   - 开发测试：使用免费额度
   - 小规模生产：按量付费
   - 大规模生产：购买资源包

### 1.3 获取API密钥

1. **进入API-KEY管理**
   - 登录 https://dashscope.aliyun.com/
   - 点击右上角头像
   - 选择 "API-KEY管理"

2. **创建API-KEY**
   - 点击 "创建新的API-KEY"
   - 输入密钥名称：`AI健康助手`
   - 点击 "确定"

3. **复制API-KEY**
   - 创建成功后会显示API-KEY
   - **立即复制并保存**（只显示一次）
   - 格式类似：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

4. **保存密钥**
   - 将API-KEY保存到安全的地方
   - 不要泄露给他人
   - 不要提交到代码仓库

### 1.4 查看使用情况

1. **访问控制台**
   - https://dashscope.aliyun.com/
   - 查看 "用量统计"

2. **监控指标**
   - 今日调用量
   - 本月调用量
   - 剩余额度
   - 费用统计

---

## 2. 配置API密钥

### 2.1 配置后端环境变量

#### 开发环境

编辑项目根目录的 `.env` 文件：

```env
# 阿里云通义千问配置
TONGYI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TONGYI_MODEL=qwen-plus

# 其他配置...
```

**替换内容**：
- `TONGYI_API_KEY`: 替换为你的实际API密钥
- `TONGYI_MODEL`: 选择模型
  - `qwen-turbo`: 速度快，成本低
  - `qwen-plus`: 平衡性能和成本（推荐）
  - `qwen-max`: 最强性能，成本高

#### 生产环境

编辑 `.env.production` 文件：

```env
# 阿里云通义千问配置
TONGYI_API_KEY=sk-your-production-api-key
TONGYI_MODEL=qwen-plus
```

### 2.2 验证配置

```bash
# 查看环境变量
cat .env | grep TONGYI

# 重启服务使配置生效
docker-compose restart backend
```

---

## 3. 测试API连接

### 3.1 使用Python测试

创建测试脚本 `test_tongyi.py`：

```python
import os
from openai import OpenAI

# 配置API
client = OpenAI(
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 测试调用
try:
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己"}
        ]
    )
    print("✅ API连接成功！")
    print(f"回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API连接失败: {e}")
```

运行测试：

```bash
# 进入后端容器
docker-compose exec backend bash

# 设置环境变量
export TONGYI_API_KEY=sk-your-api-key

# 运行测试
python test_tongyi.py

# 退出容器
exit
```

### 3.2 使用API文档测试

1. **访问API文档**
   - http://localhost:8000/docs

2. **测试对话接口**
   - 找到 `POST /api/chat/send`
   - 先登录获取token
   - 发送测试消息：
   ```json
   {
     "message": "你好，请介绍一下自己",
     "conversation_id": null
   }
   ```
   - 查看AI回复

3. **检查日志**
   ```bash
   docker-compose logs -f backend
   ```
   - 查看是否有API调用错误

---

## 4. 其他AI模型选择

### 4.1 OpenAI GPT（国际版）

**申请步骤**：

1. 访问：https://platform.openai.com/
2. 注册账号（需要国际手机号）
3. 绑定信用卡
4. 获取API Key

**配置**：

```python
# backend/app/services/ai_service.py
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...]
)
```

**费用**：
- GPT-3.5-turbo: $0.002/1K tokens
- GPT-4: $0.03/1K tokens

### 4.2 百度文心一言

**申请步骤**：

1. 访问：https://cloud.baidu.com/product/wenxinworkshop
2. 注册百度智能云账号
3. 实名认证
4. 创建应用获取API Key和Secret Key

**配置**：

```python
import requests

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": "your_api_key",
        "client_secret": "your_secret_key"
    }
    return requests.post(url, params=params).json()["access_token"]

def chat(message):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={get_access_token()}"
    payload = {
        "messages": [{"role": "user", "content": message}]
    }
    return requests.post(url, json=payload).json()
```

**费用**：
- ERNIE-Bot-turbo: ¥0.012/千tokens
- ERNIE-Bot: ¥0.12/千tokens

### 4.3 讯飞星火

**申请步骤**：

1. 访问：https://xinghuo.xfyun.cn/
2. 注册讯飞开放平台账号
3. 创建应用
4. 获取APPID、APIKey、APISecret

**配置**：

```python
import websocket
import json

def chat(message):
    # 使用WebSocket连接
    ws_url = "wss://spark-api.xf-yun.com/v1.1/chat"
    # 实现WebSocket通信
    pass
```

**费用**：
- 免费额度：200万tokens/年
- 按量付费：¥0.018/千tokens

### 4.4 智谱AI（ChatGLM）

**申请步骤**：

1. 访问：https://open.bigmodel.cn/
2. 注册账号
3. 创建API Key

**配置**：

```python
import zhipuai

zhipuai.api_key = "your_api_key"

response = zhipuai.model_api.invoke(
    model="chatglm_turbo",
    prompt=[{"role": "user", "content": "你好"}]
)
```

**费用**：
- 免费额度：100万tokens
- ChatGLM-Turbo: ¥0.005/千tokens

---

## 5. 常见问题

### 问题1：API Key无效

**症状**：`Invalid API Key`

**解决**：
1. 检查API Key是否复制完整
2. 确认API Key未过期
3. 检查是否有空格或换行符
4. 重新生成API Key

### 问题2：余额不足

**症状**：`Insufficient balance`

**解决**：
1. 登录控制台查看余额
2. 购买资源包或充值
3. 检查是否超出免费额度

### 问题3：请求频率限制

**症状**：`Rate limit exceeded`

**解决**：
1. 降低请求频率
2. 升级套餐提高限额
3. 实现请求队列和重试机制

### 问题4：网络连接失败

**症状**：`Connection timeout`

**解决**：
1. 检查网络连接
2. 检查防火墙设置
3. 使用代理（如需要）
4. 检查API服务状态

### 问题5：模型不存在

**症状**：`Model not found`

**解决**：
1. 检查模型名称是否正确
2. 确认模型是否已开通
3. 查看官方文档确认可用模型

---

## 6. 成本优化建议

### 6.1 选择合适的模型

```
开发测试: qwen-turbo (便宜)
生产环境: qwen-plus (平衡)
高要求场景: qwen-max (贵)
```

### 6.2 优化提示词

```python
# ❌ 不好的提示词（浪费tokens）
prompt = "请详细介绍一下如何提高跑步速度，包括训练方法、饮食建议、装备选择等各个方面..."

# ✅ 好的提示词（节省tokens）
prompt = "简要说明提高跑步速度的3个关键训练方法"
```

### 6.3 实现缓存

```python
# 缓存常见问题的回答
from app.core.cache import cache_manager

cache_key = f"ai:response:{hash(message)}"
cached = await cache_manager.get(cache_key)
if cached:
    return cached

# 调用AI API
response = await call_ai_api(message)

# 缓存结果
await cache_manager.set(cache_key, response, expire=3600)
```

### 6.4 设置最大tokens

```python
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[...],
    max_tokens=500  # 限制回复长度
)
```

### 6.5 监控使用量

```python
# 记录每次调用
import logging

logger.info(f"AI调用: 用户={user_id}, tokens={tokens_used}, 费用={cost}")

# 设置预警
if monthly_cost > 1000:
    send_alert("AI费用超过预算")
```

---

## 7. 安全建议

### 7.1 保护API密钥

```bash
# ✅ 使用环境变量
TONGYI_API_KEY=sk-xxx

# ❌ 不要硬编码
api_key = "sk-xxx"  # 危险！

# ❌ 不要提交到Git
git add .env  # 危险！
```

### 7.2 使用.gitignore

```gitignore
# 环境变量文件
.env
.env.local
.env.production

# API密钥文件
*_api_key.txt
secrets/
```

### 7.3 定期轮换密钥

```
1. 创建新的API Key
2. 更新环境变量
3. 重启服务
4. 删除旧的API Key
```

### 7.4 设置IP白名单

在阿里云控制台：
1. API-KEY管理
2. 选择密钥
3. 设置IP白名单
4. 只允许服务器IP访问

---

## 8. 配置检查清单

部署前确认：

- [ ] 已注册阿里云账号
- [ ] 已完成实名认证
- [ ] 已开通通义千问服务
- [ ] 已创建API Key
- [ ] API Key已保存到安全位置
- [ ] 已配置到.env文件
- [ ] 已测试API连接
- [ ] 已设置使用量监控
- [ ] 已配置.gitignore
- [ ] 已了解费用标准

---

## 9. 相关资源

- **阿里云通义千问**：https://dashscope.aliyun.com/
- **API文档**：https://help.aliyun.com/zh/dashscope/
- **定价说明**：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-metering-and-billing
- **控制台**：https://dashscope.console.aliyun.com/

---

**配置完成后，你的AI助手就可以正常工作了！** 🎉
