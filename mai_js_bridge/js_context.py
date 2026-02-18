"""
JsContext - 执行 JS 插件时传入的上下文对象

在 JavaScript 代码中以 ctx.xxx() 的方式调用。
"""
import asyncio
import logging
from typing import Any, Optional, Dict, List


class JsContext:
    """
    JS 插件执行上下文。
    在执行 JS 的 execute(ctx) 时传入。
    
    所有 async 方法由 JS 通过回调调用。
    由于 JS 桥接是同步的（使用 Node.js 子进程），
    实际 async 操作会在 Python 侧被 asyncio.run_coroutine_threadsafe 处理。
    """

    def __init__(
        self,
        stream_id: str,
        plugin_name: str,
        loop: asyncio.AbstractEventLoop,
        send_api: Any,
        config_getter: Any,
        logger: logging.Logger,
        matched=None,         # re.Match 对象（Command 专用）
        action_data: Optional[Dict] = None,  # Action 参数（Action 专用）
    ):
        self.stream_id = stream_id
        self.plugin_name = plugin_name
        self._loop = loop
        self._send_api = send_api
        self._config_getter = config_getter
        self.logger = logger
        self._matched = matched
        self._action_data = action_data or {}
        self._results: List[str] = []

    # =========================================================================
    # 消息发送方法（供 JS 调用）
    # =========================================================================

    def send_text(self, text: str) -> None:
        """发送文本消息（同步包装，内部 schedule async 任务）"""
        if not text:
            return
        future = asyncio.run_coroutine_threadsafe(
            self._send_api.text_to_stream(str(text), self.stream_id),
            self._loop,
        )
        try:
            future.result(timeout=30)
        except Exception as e:
            self.logger.error(f"[JsContext] send_text 失败：{e}")

    def send_image(self, base64_str: str) -> None:
        """发送图片（base64 编码）"""
        if not base64_str:
            return
        future = asyncio.run_coroutine_threadsafe(
            self._send_api.image_to_stream(str(base64_str), self.stream_id),
            self._loop,
        )
        try:
            future.result(timeout=30)
        except Exception as e:
            self.logger.error(f"[JsContext] send_image 失败：{e}")

    def send_emoji(self, base64_str: str) -> None:
        """发送表情包（base64 编码）"""
        if not base64_str:
            return
        future = asyncio.run_coroutine_threadsafe(
            self._send_api.emoji_to_stream(str(base64_str), self.stream_id),
            self._loop,
        )
        try:
            future.result(timeout=30)
        except Exception as e:
            self.logger.error(f"[JsContext] send_emoji 失败：{e}")

    # =========================================================================
    # 参数获取方法（供 JS 调用）
    # =========================================================================

    def get_param(self, key: str, default: Any = None) -> Any:
        """获取 Action 中 LLM 传入的参数值"""
        return self._action_data.get(key, default)

    def get_match(self, group: int) -> Optional[str]:
        """获取 Command 正则的捕获组"""
        if self._matched is None:
            return None
        try:
            return self._matched.group(group)
        except (IndexError, AttributeError):
            return None

    def get_config(self, key: str, default: Any = None) -> Any:
        """读取配置值（格式：'section.key'）"""
        if self._config_getter is None:
            return default
        try:
            return self._config_getter(key, default)
        except Exception:
            return default

    # =========================================================================
    # 工具方法（供 JS 调用）
    # =========================================================================

    def log(self, message: str) -> None:
        """输出日志"""
        self.logger.info(f"[JS:{self.plugin_name}] {message}")

    def log_error(self, message: str) -> None:
        """输出错误日志"""
        self.logger.error(f"[JS:{self.plugin_name}] {message}")

    def to_dict(self) -> Dict:
        """导出为可序列化的字典（供 JS 侧读取上下文信息）"""
        return {
            "stream_id": self.stream_id,
            "plugin_name": self.plugin_name,
            "action_data": self._action_data,
        }


# ─── 公开别名 ─────────────────────────────────────────────────────────────────
# JsExecutionContext 和 JsContext 完全等价，可按喜好选用
JsExecutionContext = JsContext
