# API路由模块

# 导出所有API路由，方便导入
from . import auth
from . import chat
from . import conversation
from . import fitness
from . import data_upload

__all__ = [
    'auth',
    'chat',
    'conversation',
    'fitness',
    'data_upload'
]
