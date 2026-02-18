"""
{{PLUGIN_DISPLAY_NAME}} 工具函数模块

将通用功能抽取到这里，避免 plugin.py 过于臃肿。
"""

import asyncio
import datetime
from typing import Optional, Dict, Any


def format_time(timestamp: Optional[float] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳为字符串"""
    if timestamp is None:
        dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime(fmt)


def truncate_text(text: str, max_len: int = 100, suffix: str = "...") -> str:
    """截断过长的文本"""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


async def safe_http_get(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    安全的 HTTP GET 请求（需要安装 aiohttp）
    
    使用前请在 plugin.py 的 python_dependencies 中添加 "aiohttp"
    """
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
    except ImportError:
        raise ImportError("请先安装 aiohttp：pip install aiohttp")
    except Exception as e:
        return None
