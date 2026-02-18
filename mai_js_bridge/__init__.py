"""
mai_js_bridge - MaiBot JavaScript 插件桥接器

允许使用 JavaScript 编写麦麦插件。
通过解析 JS 文件中注册的 command/action，动态生成 Python 组件类。

使用方式（在 plugin.py 中）：
    from mai_js_bridge import JsBridgeLoader
    
    loader = JsBridgeLoader("path/to/plugin.js", plugin_name="my_plugin")
    components = loader.get_components()
"""

from .bridge import JsBridgeLoader, JsBridgePlugin
from .js_context import JsContext

# 别名：JsExecutionContext = JsContext
JsExecutionContext = JsContext

__version__ = "1.0.0"
__all__ = [
    "JsBridgeLoader",
    "JsBridgePlugin",   # JsBridgeLoader 的别名
    "JsContext",
    "JsExecutionContext",  # JsContext 的别名
]
