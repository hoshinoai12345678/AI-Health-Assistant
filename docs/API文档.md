# API文档

## 概述

AI健康助手API提供了完整的健康咨询和体测分析功能。

**基础URL**: `https://api.example.com`

**认证方式**: Bearer Token (JWT)

---

## 认证接口

### 1. 用户登录

**接口**: `POST /api/auth/login`

**请求体**:
```json
{
  "wechat_code": "微信登录code"
}
```

**响应**:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "openid": "xxx",
    "role": "student"
  }
}
```

---

## 对话接口

### 2. 发送消息

**接口**: `POST /api/chat/send`

**请求头**:
```
Authorization: Bearer {token}
```

**请求体**:
```json
{
  "message": "如何提高跑步速度？",
  "conversation_id": 123
}
```

**响应**:
```json
{
  "response": "AI回复内容...",
  "conversation_id": 123,
  "sources": ["internal"],
  "timestamp": "2024-01-19T10:00:00Z"
}
```

**错误响应**:
- `400`: 消息内容不安全
- `401`: 未授权
- `500`: 服务器错误

---

## 对话历史接口

### 3. 获取对话列表

**接口**: `GET /api/conversation/list`

**请求头**:
```
Authorization: Bearer {token}
```

**查询参数**:
- `skip`: 跳过数量（默认0）
- `limit`: 返回数量（默认20）

**响应**:
```json
{
  "conversations": [
    {
      "id": 123,
      "title": "跑步训练咨询",
      "created_at": "2024-01-19T10:00:00Z",
      "updated_at": "2024-01-19T10:30:00Z",
      "message_count": 5
    }
  ],
  "total": 10
}
```

### 4. 获取对话详情

**接口**: `GET /api/conversation/{conversation_id}`

**响应**:
```json
{
  "id": 123,
  "title": "跑步训练咨询",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "如何提高跑步速度？",
      "timestamp": "2024-01-19T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "AI回复...",
      "timestamp": "2024-01-19T10:00:05Z"
    }
  ]
}
```

---

## 体测分析接口

### 5. 体测数据分析

**接口**: `POST /api/fitness/analyze`

**请求体**:
```json
{
  "gender": "male",
  "grade": 8,
  "test_data": {
    "height": 170,
    "weight": 60,
    "fifty_meter": 7.5,
    "standing_jump": 220,
    "sit_ups": 45,
    "pull_ups": 8,
    "sit_reach": 15.0,
    "vital_capacity": 3500,
    "endurance_run": 210
  }
}
```

**响应**:
```json
{
  "analysis": {
    "total_score": 85,
    "level": "良好",
    "bmi": 20.8,
    "bmi_level": "正常",
    "item_scores": {
      "fifty_meter": 90,
      "standing_jump": 85,
      "sit_ups": 80
    },
    "weak_items": ["sit_reach"]
  },
  "suggestions": [
    "建议加强柔韧性训练",
    "可以多做拉伸运动"
  ]
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权或token过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 限流说明

- 每个IP每分钟最多100次请求
- 超过限制返回429错误
- 建议客户端实现指数退避重试

---

## 安全说明

1. 所有API请求必须使用HTTPS
2. Token有效期为7天
3. 敏感内容会被自动过滤
4. 所有输入会进行安全检查
