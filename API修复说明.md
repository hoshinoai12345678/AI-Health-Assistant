# API 404 错误修复说明

## 问题描述

根据日志显示，`POST /api/chat/send` 返回 404 错误：

```
2026-01-20 14:46:12,280 - app.middleware.security - INFO - 请求开始: POST /api/chat/send
2026-01-20 14:46:12,281 - app.middleware.security - INFO - 请求完成: POST /api/chat/send 状态码=404 耗时=0.001秒
INFO:     111.199.105.151:2072 - "POST /api/chat/send HTTP/1.1" 404 Not Found
```

## 问题原因

API 端点的认证方式与前端发送的认证信息不匹配：

1. **前端 (app.js)**: 通过 `Authorization: Bearer <token>` Header 发送 token
2. **后端 (chat.py)**: 期望 token 作为查询参数 `?token=xxx`

这导致后端无法正确识别请求，返回 404 错误。

## 修复内容

### 1. 更新 `backend/app/core/security.py`

添加了 `get_current_user` 函数，用于从 Authorization Header 中提取和验证 token：

```python
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    从Authorization Header中获取当前用户信息
    
    Args:
        authorization: Authorization Header值 (格式: "Bearer <token>")
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 如果token无效或缺失
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 解析Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证格式",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload
```

### 2. 更新 `backend/app/api/chat.py`

修改了 `/send` 端点，使用依赖注入方式获取当前用户：

**修改前：**
```python
@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    token: str,  # 作为查询参数
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(...)
    user_id = payload.get("user_id")
```

**修改后：**
```python
@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),  # 从Header获取
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.get("user_id")
    user_role = current_user.get("role", "student")
```

同时修改了响应字段名从 `message` 改为 `reply`，以匹配前端期望。

### 3. 更新 `backend/app/api/conversation.py`

所有端点都改用 `Depends(get_current_user)` 方式：

- `GET /list` - 获取对话列表
- `GET /{conversation_id}` - 获取对话详情
- `DELETE /{conversation_id}` - 删除对话
- `DELETE /all` - 删除所有对话

### 4. 更新 `backend/app/api/fitness.py`

体测分析端点也改用新的认证方式：

```python
@router.get("/analyze/{student_id}", response_model=FitnessAnalysisResponse)
async def analyze_fitness(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
```

### 5. 更新 `backend/app/api/auth.py`

添加了简化的登录端点用于 Web 版测试：

```python
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """普通用户名密码登录（用于Web版测试）"""
```

## 如何重启服务

### 方法 1: 如果使用 Docker

```bash
docker-compose restart backend
docker-compose restart web-server
```

### 方法 2: 如果直接运行 Python

找到运行 web-server 的终端，按 `Ctrl+C` 停止，然后重新运行：

```bash
cd web-server
python main.py
```

### 方法 3: 使用 Windows 批处理脚本

如果服务是通过 `一键启动.bat` 启动的：

```bash
docker-compose restart
```

## 验证修复

修复后，前端发送的请求应该能正常工作：

```javascript
const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`  // ✅ 现在可以正确识别
    },
    body: JSON.stringify({
        message: text,
        conversation_id: currentConversationId
    })
});
```

## 注意事项

1. **需要重启服务**：修改代码后必须重启 web-server 服务才能生效
2. **登录状态**：如果之前有登录，可能需要重新登录以获取新的 token
3. **测试账号**：Web 版现在支持简单的用户名密码登录，无需微信授权

## 测试步骤

1. 重启 web-server 服务
2. 打开浏览器访问 http://localhost:9000 或您的服务器地址
3. 点击"个人中心"标签
4. 点击"登录"按钮，输入任意用户名和密码（会自动创建测试账号）
5. 返回"聊天"标签，发送消息测试

如果一切正常，您应该能看到 AI 的回复，而不是 404 错误。
