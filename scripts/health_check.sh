#!/bin/bash

# 健康检查脚本

HEALTH_URL="https://your-domain.com/health"
ALERT_WEBHOOK="https://your-alert-webhook-url"

# 执行健康检查
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "健康检查失败: HTTP $RESPONSE"
    
    # 发送告警
    curl -X POST $ALERT_WEBHOOK \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"AI健康助手API健康检查失败，状态码: $RESPONSE\"}"
    
    exit 1
else
    echo "健康检查通过"
    exit 0
fi
