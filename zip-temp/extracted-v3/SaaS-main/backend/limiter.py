"""Rate Limiter 单例，所有路由共享同一实例。测试模式自动放宽限制。"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

if os.environ.get("TESTING") == "1":
    # 测试模式：极高上限，不干扰测试
    limiter = Limiter(key_func=get_remote_address, default_limits=["1000000/day"])
else:
    limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "60/hour"])
